#!/usr/bin/env python3.9

"""
    manager.py
    Is the main entry point for fleetmanager and sets up the app
"""

import os
import signal
import threading
from enum import Enum
from datetime import datetime

from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.config import Config
from kivy.uix.image import Image
from kivymd.uix.label import MDLabel
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.garden.mapview import MapSource, MapMarker
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.list import TwoLineAvatarListItem, ImageLeftWidget

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


class FleetManager(MDApp):
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

        # TODO: verify that this is set once the app is packaged properly
        self.icon = "images/app_icon.png"
        self.title = "fleet manager"

        # layout options
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Gray"

        # scheduling time clock
        Clock.schedule_interval(self.time_function, 1)

        # scheduling marker update
        Clock.schedule_interval(self.fleet_update, 0.01)

        # member variables
        self.serverStatus = False

        return Builder.load_file('fleet_manager.kv')

    def time_function(self, dt) -> None:
        """ function to updated the time label """
        self.icon = "images/app_icon.png"

        if (self.currentFrame == windows.loginWindow.name):
            now = datetime.now()

            current_time = now.strftime("%H:%M:%S")

            # self.root.ids.timeLbl.text = current_time
            self.root.screens[windows.loginWindow.value].ids.timeLbl.text = current_time

        if (self.currentFrame == windows.mainWindow.name):
            now = datetime.now()

            current_time = now.strftime("%H:%M:%S")

            self.root.screens[windows.mainWindow.value].ids.timeLbl.text = current_time

    def fleet_update(self, dt) -> None:
        """ function that runs every second and updates fleet information """
        if (self.currentFrame == windows.mainWindow.name):
            # updates markers on screen
            for marker in self.__markers:
                # removing existing markers
                self.root.screens[windows.mainWindow.value].ids.map.remove_marker(
                    marker)

            self.__markers = []

            # update markers
            for vehicle in self.mission.fleet:
                # place marker onto map
                # TODO: check if valid  lat and long first
                if self.mission.darkmode:
                    if vehicle["type"] == "uav":
                        _source = "images/uav_dark.png"
                    if vehicle["type"] == "tank":
                        _source = "images/tank_dark.png"
                    marker = MapMarker(
                        lat=vehicle["location"][0], lon=vehicle["location"][1], source=_source)
                    self.__markers.append(marker)
                else:
                    if vehicle["type"] == "uav":
                        _source = "images/uav_light.png"
                    if vehicle["type"] == "tank":
                        _source = "images/tank_light.png"
                    marker = MapMarker(
                        lat=vehicle["location"][0], lon=vehicle["location"][1], source=_source)
                    self.__markers.append(marker)

                self.root.screens[windows.mainWindow.value].ids.map.add_marker(
                    marker)

                # updating label onto marker
                lbl = MDLabel(text=vehicle["callsign"], halign="center")
                lbl.pos = marker.pos[:]
                lbl.pos[0] = lbl.pos[0] - 25
                lbl.pos[1] = lbl.pos[1] - 70
                marker.add_widget(lbl)

            # checking last update time and updating activity statuses
            currentTime = datetime.now()
            for i in range(len(self.mission.vehicleStatus)):
                delta = (currentTime - self.mission.vehicleStatus[i][2])
                if delta.total_seconds() > 10:  # TODO update this to be a set variable from yaml
                    self.mission.vehicleStatus[i][1] = "offline"

            # updating fleet status information
            for i in range(len(self.mission.vehicleStatus)):
                # updating text
                self.__statusList[i].secondary_text = self.mission.vehicleStatus[i][1]

                # updating icon
                if (self.mission.vehicleStatus[i][1] == "online"):
                    self.__statusListImage[i].source = "images/active.png"
                else:
                    self.__statusListImage[i].source = "images/inactive.png"

    def mission_validate(self, text) -> None:
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
        if (self.configure_manager()):

            self.root.screens[windows.loginWindow.value].ids.spinner.active = False

            # creating the server to run in a thread
            self.__server = Server(self.mission)
            self.__server_thread = threading.Thread(
                target=self.thread_function)
            # TODO: figure out nice way to end server when app is closed, probs just a stop call to server on end func
            self.__server_thread.start()
            self.serverStatus = True  # server is now active

            self.root.current = "Main"
            self.currentFrame = windows.mainWindow.name

    def configure_manager(self) -> bool:
        """ sets up manager screen """
        # update mission values
        self.root.screens[windows.mainWindow.value].ids.missionName.text = self.mission.name
        self.root.screens[windows.mainWindow.value].ids.missionStart.text = self.mission.start
        self.root.screens[windows.mainWindow.value].ids.missionLocation.text = self.mission.location
        self.root.screens[windows.mainWindow.value].ids.missionDuration.text = self.mission.duration
        self.root.screens[windows.mainWindow.value].ids.missionOperation.text = self.mission.operation

        # darkmode configuration
        if self.mission.darkmode:
            source = MapSource(url="http://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
                               cache_key="darkmap", tile_size=512,
                               image_ext="png", attribution="Darkmap")
            self.root.screens[windows.mainWindow.value].ids.map.map_source = source

            # recentering map - when the source changes it loses its initial lat and long
            self.root.screens[windows.mainWindow.value].ids.map.center_on(
                self.mission.lat, self.mission.lon)

            # TODO: update this to take in all different maps offered by mapview
            # TODO: if not darkmode should update text label text colour

        # preloading maps
        if self.mission.preloadMap:
            # TODO: figure out how to make api calls around the area and for all zooms?
            pass

        self.__markers = []
        self.__statusList = []
        self.__statusListImage = []

        # load fleet
        for vehicle in self.mission.fleet:
            # adding markers to manager
            if self.mission.darkmode:
                if vehicle["type"] == "uav":
                    _source = "images/uav_dark.png"
                if vehicle["type"] == "tank":
                    _source = "images/tank_dark.png"
                marker = MapMarker(lat=self.mission.lat,
                                   lon=self.mission.lon, source=_source)
                self.__markers.append(marker)
            else:
                if vehicle["type"] == "uav":
                    _source = "images/uav_light.png"
                if vehicle["type"] == "tank":
                    _source = "images/tank_light.png"
                marker = MapMarker(lat=self.mission.lat,
                                   lon=self.mission.lon, source=_source)
                self.__markers.append(marker)

            # creating a label for the marker TODO:toggle functionality for showing the labels
            # lbl = MDLabel(text=vehicle["callsign"], halign="center")
            # marker.add_widget(lbl)

            self.root.screens[windows.mainWindow.value].ids.map.add_marker(
                marker)

            # updating vehicle list - inactive initially
            rightIcon = ImageLeftWidget(source="images/inactive.png")
            vehicleItem = TwoLineAvatarListItem(
                text=vehicle["callsign"], secondary_text="offline")

            vehicleItem.add_widget(rightIcon)
            self.root.screens[windows.mainWindow.value].ids.fleetList.add_widget(
                vehicleItem)
            self.__statusListImage.append(rightIcon)
            self.__statusList.append(vehicleItem)

        return True

    def thread_function(self):
        """ thread function for server"""
        self.__server.run()

    def on_stop(self):
        """ Clean up on application close """
        if self.serverStatus:
            os.kill(self.__server_thread.native_id, signal.SIGKILL)
        return True


# entry point
if __name__ == '__main__':
    FleetManager().run()
