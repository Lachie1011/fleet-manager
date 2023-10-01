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
from kivymd.uix.label import MDLabel
from kivy.core.window import Window
from kivy.garden.mapview import MapSource, MapMarker  # pylint: disable=E0611, E0401
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.list import TwoLineAvatarListItem, ImageLeftWidget

# adding app modules
from server import Server
from mission import Mission


class Windows(Enum):
    """ window enums """
    loginWindow = 0
    mainWindow = 1


class LoginWindow(Screen):
    """ login window class """


class MainWindow(Screen):
    """ main window class """


class WindowManager(ScreenManager):
    """ window manager """


class FleetManager(MDApp):  # pylint: disable=R0902
    """
        main application
    """
    __current_frame = Windows.loginWindow.name
    __server_status = False
    __markers = []
    __status_list = []
    __status_list_image = []

    # window configuration
    Window.maximize()

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

        return Builder.load_file('fleet_manager.kv')

    def time_function(self, dt) -> None:
        """ function to updated the time label """
        self.icon = "images/app_icon.png"

        if self.__current_frame == Windows.loginWindow.name:
            now = datetime.now()

            current_time = now.strftime("%H:%M:%S")

            # self.root.ids.timeLbl.text = current_time
            self.root.screens[Windows.loginWindow.value].ids.timeLbl.text = current_time

        if self.__current_frame == Windows.mainWindow.name:
            now = datetime.now()

            current_time = now.strftime("%H:%M:%S")

            self.root.screens[Windows.mainWindow.value].ids.timeLbl.text = current_time

    def fleet_update(self, dt) -> None:
        """ function that runs every second and updates fleet information """
        if self.__current_frame == Windows.mainWindow.name:
            # updates markers on screen
            for marker in self.__markers:
                # removing existing markers
                self.root.screens[Windows.mainWindow.value].ids.map.remove_marker(
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

                self.root.screens[Windows.mainWindow.value].ids.map.add_marker(
                    marker)

                # updating label onto marker
                lbl = MDLabel(text=vehicle["callsign"], halign="center")
                lbl.pos = marker.pos[:]
                lbl.pos[0] = lbl.pos[0] - 25
                lbl.pos[1] = lbl.pos[1] - 70
                marker.add_widget(lbl)

            # checking last update time and updating activity statuses
            current_time = datetime.now()
            for i in range(len(self.mission.vehicle_status)):
                delta = (current_time - self.mission.vehicle_status[i][2])
                if delta.total_seconds() > 10:  # TODO update this to be a set variable from yaml
                    self.mission.vehicle_status[i][1] = "offline"

            # updating fleet status information
            for i in range(len(self.mission.vehicle_status)):
                # updating text
                self.__status_list[i].secondary_text = self.mission.vehicle_status[i][1]

                # updating icon
                if self.mission.vehicle_status[i][1] == "online":
                    self.__status_list_image[i].source = "images/active.png"
                else:
                    self.__status_list_image[i].source = "images/inactive.png"

    def mission_validate(self, text) -> None:
        """ validates the mission file """
        self.root.screens[Windows.loginWindow.value].ids.spinner.active = True

        # creating mission object
        try:
            self.mission = Mission("missions/" + text + ".yaml")  # pylint: disable=W0201
        except Exception as exc:  # pylint: disable=W0703
            self.root.screens[Windows.loginWindow.value].ids.spinner.active = False
            self.root.screens[Windows.loginWindow.value].ids.missionTxt.text = ""
            print(exc)
            return

        # setup manager screen
        if self.configure_manager():

            self.root.screens[Windows.loginWindow.value].ids.spinner.active = False

            # creating the server to run in a thread
            self.__server = Server(self.mission)  # pylint: disable=W0201
            self.__server_thread = threading.Thread(  # pylint: disable=W0201
                target=self.thread_function)
            self.__server_thread.start()
            self.__server_status = True  # server is now active

            self.root.current = "Main"
            self.__current_frame = Windows.mainWindow.name

    def configure_manager(self) -> bool:
        """ sets up manager screen """
        # update mission values
        self.root.screens[Windows.mainWindow.value].ids.missionName.text = self.mission.name
        self.root.screens[Windows.mainWindow.value].ids.missionStart.text = self.mission.start
        self.root.screens[Windows.mainWindow.value].ids.missionLocation.text = self.mission.location
        self.root.screens[Windows.mainWindow.value].ids.missionDuration.text = self.mission.duration
        self.root.screens[Windows.mainWindow.value].ids.missionOperation.text = self.mission.operation  # pylint: disable=C0301

        # darkmode configuration
        if self.mission.darkmode:
            source = MapSource(url="http://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
                               cache_key="darkmap", tile_size=512,
                               image_ext="png", attribution="Darkmap")
            self.root.screens[Windows.mainWindow.value].ids.map.map_source = source

            # recentering map - when the source changes it loses its initial lat and long
            self.root.screens[Windows.mainWindow.value].ids.map.center_on(
                self.mission.lat, self.mission.lon)

            # TODO: update this to take in all different maps offered by mapview
            # TODO: if not darkmode should update text label text colour

        # preloading maps
        if self.mission.preload_map:
            # TODO: figure out how to make api calls around the area and for all zooms?
            pass

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

            self.root.screens[Windows.mainWindow.value].ids.map.add_marker(
                marker)

            # updating vehicle list - inactive initially
            right_icon = ImageLeftWidget(source="images/inactive.png")
            vehicle_item = TwoLineAvatarListItem(
                text=vehicle["callsign"], secondary_text="offline")

            vehicle_item.add_widget(right_icon)
            self.root.screens[Windows.mainWindow.value].ids.fleetList.add_widget(
                vehicle_item)
            self.__status_list_image.append(right_icon)
            self.__status_list.append(vehicle_item)

        return True

    def thread_function(self):
        """ thread function for server"""
        self.__server.run()

    def on_stop(self):
        """ Clean up on application close """
        if self.__server_status:
            os.kill(self.__server_thread.native_id, signal.SIGKILL)
        return True


# entry point
if __name__ == '__main__':
    FleetManager().run()
