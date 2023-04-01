#!/usr/bin/env python3.9

"""
    manager.py
    Is the main entry point for battle space manager and sets up the app
"""

import threading
from enum import Enum
from datetime import datetime

from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.config import Config
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.uix.screenmanager import ScreenManager, Screen 
from kivy.garden.mapview import MapSource, MapMarker

# adding app modules
from server import Server
from mission import Mission

class windows(Enum):
	""" window enums """
	loginWindow = 0
	mainWindow = 1

class LoginWindow(Screen):
	""" login window class """
	pass

class MainWindow(Screen):
	""" main window class """
	pass

class WindowManager(ScreenManager): 
	""" window manager """
	pass

class BattleManager(MDApp):
	"""
		logic for the main application
	"""

	# current frame
	currentFrame = windows.loginWindow.name

	# window configuration 
	Window.maximize()

	def __init__(self) -> None:
		super().__init__()

	def build(self) -> any:
		""" build the application """
		self.title = "battlespace manager"
		# layout options
		self.theme_cls.theme_style = "Dark"
		self.theme_cls.primary_palette = "BlueGray"

		# scheduling time clock
		Clock.schedule_interval(self.timeFunction, 1)

		# scheduling marker update
		Clock.schedule_interval(self.marker_update, 1)

		return Builder.load_file('manager.kv') 

	def timeFunction(self, dt) -> None:
		""" function to updated the time label """
		if(self.currentFrame == windows.loginWindow.name):
			now = datetime.now()

			current_time = now.strftime("%H:%M:%S")

			#self.root.ids.timeLbl.text = current_time
			self.root.screens[windows.loginWindow.value].ids.timeLbl.text = current_time # todo: make this an enum 

		if(self.currentFrame == windows.mainWindow.name):
			now = datetime.now()

			current_time = now.strftime("%H:%M:%S")

			#self.root.ids.timeLbl.text = current_time
			self.root.screens[windows.mainWindow.value].ids.timeLbl.text = current_time # todo: make this an enum 

	def marker_update(self, dt) -> None:
		""" function that runs every second and updates markers """
		# TODO: there might be a nicer or smarter way to do this
		if(self.currentFrame == windows.mainWindow.name):
			# remove existing markers
			for marker in self.__markers:
				# first remove existing markers
				self.root.screens[windows.mainWindow.value].ids.map.remove_marker(marker)

			self.__markers = []
			
			# update UAVs
			for vehicle in self.mission.fleet:
				# place UAV onto map
				# TODO: check if valid  lat and long first
				if self.mission.darkmode:
					if vehicle["type"] == "uav":
						_source = "images/uav_dark.png"
					if vehicle["type"] == "tank":
						_source = "images/tank_dark.png" 
					marker = MapMarker(lat = vehicle["location"][0], lon = vehicle["location"][1], source = _source)
					self.__markers.append(marker)
				else:
					if vehicle["type"] == "uav":
						_source = "images/uav_light.png"
					if vehicle["type"] == "tank":
						_source = "images/tank_light.png" 		
					marker = MapMarker(lat = vehicle["location"][0], lon = vehicle["location"][1], source = _source)
					self.__markers.append(marker)
				self.root.screens[windows.mainWindow.value].ids.map.add_marker(marker)

	def	mission_validate(self, text) -> None:
		""" validates the mission file """
		self.root.screens[windows.loginWindow.value].ids.spinner.active = True
		
		# creating mission object
		try:
			self.mission = Mission("missions/" + text + ".yaml")
		except Exception as exc:
			self.root.screens[windows.loginWindow.value].ids.spinner.active = False
			self.root.screens[windows.loginWindow.value].ids.missionTxt.text = ""
			return
		
		# setup manager screen
		if(self.configure_manager()):

			self.root.screens[windows.loginWindow.value].ids.spinner.active = False
			
			# creating the server to run in a thread
			self.__server = Server(self.mission)
			self.__server_thread = threading.Thread(target=self.thread_function)
			self.__server_thread.start()  # TODO: figure out nice way to end server when app is closed, probs just a stop call to server on end func

			self.root.current = "Main"
			self.currentFrame = windows.mainWindow.name

	def configure_manager(self) -> bool: 
		""" sets up manager screen """
		# update mission values
		self.root.screens[windows.mainWindow.value].ids.missionNameLbl.text += self.mission.name
		self.root.screens[windows.mainWindow.value].ids.missionStart.text += self.mission.start
		self.root.screens[windows.mainWindow.value].ids.missionLocation.text += self.mission.location 
		self.root.screens[windows.mainWindow.value].ids.missionDuration.text += self.mission.duration
		self.root.screens[windows.mainWindow.value].ids.missionOperation.text += self.mission.operation

		# darkmode configuration
		if self.mission.darkmode:
			source = MapSource(url="http://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
					cache_key="darkmap", tile_size=512,
					image_ext="png", attribution="Darkmap")
			self.root.screens[windows.mainWindow.value].ids.map.map_source = source

			# recentering map - when the source changes it loses its initial lat and long 
			self.root.screens[windows.mainWindow.value].ids.map.center_on(self.mission.lat, self.mission.lon)

			# TODO: update this to take in all different maps offered by mapview
			# TODO: if not darkmode should update text label text colour

		# preloading maps
		if self.mission.preloadMap:
			# TODO: figure out how to make api calls around the area and for all zooms? 
			pass
		
		self.__markers = []

		# load fleet
		for vehicle in self.mission.fleet:
			if self.mission.darkmode:
				if vehicle["type"] == "uav":
					_source = "images/uav_dark.png"
				if vehicle["type"] == "tank":
					_source = "images/tank_dark.png" 
				marker = MapMarker(lat = self.mission.lat, lon = self.mission.lon, source = _source)
				self.__markers.append(marker)
			else:
				if vehicle["type"] == "uav":
					_source = "images/uav_light.png"
				if vehicle["type"] == "tank":
					_source = "images/tank_light.png" 		
				marker = MapMarker(lat = self.mission.lat, lon = self.mission.lon, source = _source)
				self.__markers.append(marker)
			self.root.screens[windows.mainWindow.value].ids.map.add_marker(marker)


			# TODO: load callsign information onto screen

		return True
	
	def thread_function(self):
		""" thread function for server"""
		self.__server.run()


# entry point 
if __name__ == '__main__':
    BattleManager().run()
