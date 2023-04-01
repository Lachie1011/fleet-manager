"""
    mission.py 
    Used to load and manage configuration for a mission
"""

import yaml 

class Mission():
    """
        creates and holds information relevant to the mission
    """
    def __init__(self, path) -> None:
        # valid mission flag
        self.isValid = True

        # attempt to load in file
        with open(path, "r") as stream:
            try:
                mission_file = yaml.safe_load(stream)
                self.construct_mission(mission_file)
            except Exception as exc:
                self.isValid = False
                print(exc)

    def construct_mission(self, mission_file) -> None:
        """ constructs the mission from yaml file"""
        # reading in mission values
        self.name = mission_file["mission"]
        self.start = mission_file["mission_date"] + " at " + str(mission_file["mission_start"])
        self.lat = mission_file["mission_start_lat"]
        self.lon = mission_file["mission_start_long"]
        self.location = str(self.lat) + " " + str(self.lon)
        self.duration = str(mission_file["mission_duration"]) + "mins"
        self.operation = str(mission_file["operational_distance"]) + "km"
        
        # reading in manager preferences
        self.darkmode = mission_file["darkmode"]
        self.preloadMap = mission_file["preload_map"]

        # reading in UAV information
        self.fleetName = mission_file["fleet_plan"][0]["fleet_name"]
        self.fleetNunber = mission_file["fleet_plan"][0]["number"]
        self.fleet = mission_file["fleet_plan"][0]["fleet"]
    
    def update_location(self, callsign, lat, long) -> bool:
        """ updates the current location of a vehicle """
        try:
            # testing is lat and long are numbers
            lat = float(lat)
            long = float(long)
        except Exception as e:
            return False
        
        for i in range(len(self.fleet)):
            if self.fleet[i]["callsign"] == callsign:
                self.fleet[i]["location"] = [lat, long]
                return True        
        return False