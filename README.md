# fleet-manager
Fleet manager is designed to be a lite application that displays the only the critical information relating to an operation or "mission".

## What it does
The application displays key information such as a vehicle's location, callsign, and status onto a gridmap of the relevant mission area. 
As well as displaying the operational data defined in the mission file such as the operational area, the estimation duration, the start time and location.


## How it works
The application utilises python3 and the kivyMD framework for design and functionality. On the manager screen it uses a premade kivy garden mapview widget 
to provide a modern gridmap that has a variety of different tile servers to select from. 

The application starts on a 'Login' window where a 'mission' file is selected that defines all of the mission values and parameters, this file is yaml a file 
and must be placed in the '/missions' directory to be found by the app.

Once a "mission" file has been successfully loaded, the app will switch to the 'Manager' window where all of the aforementioned data will be displayed. 

The app then spools a server behind the application to receive POST requests from a vehicle, which updates respectively information such as the vehicles location onto to the manager screen. 

The server presently provides the following routes: 
 - '/' GET route which serves as the root of the server and returns only a 200 OK if hit. 
 - '/update/location' POST route which is used to update the location of a vehicle. See 'demos/brisbane_demo.sh' for the expected formatting of th request. 

The app uses timers to update both the locations of the vehicles, statuses and markers drawn onto the map.

This application is intended to be open-source and as a basis to build further functionality ontop of. 

## Video demo
This demo can be recreated and used to test any changes by running './demos/brisbane_demo.sh'

![Alt Text](https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcGduemllbGtjcWppNzgxdXN0ZHJxaGxoa3ExaXB1MHFlbHF0eDRucSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Sj09AVKud2AG8BzyAq/giphy.gif =250x)

## Requirements
- kivy-garden.mapview              1.0.6
- kivymd                           1.0.1

TODO

Currently only tested with Ubuntu 20.04

### Future work
- Investigate packaging options.
- Move update tasks from timed to event driven such as the callsign drawing and marker update. 
- Ability to preload / offline download map tiles (probably a way to invoke the api calls to the tile server).
- Split out the manager settings from the mission definition. 
- Rename "mission" to "operation" - kinda cringe. 
- Find a better application icon.
- Some kind of database for storing data / replayability?
- Add get request from the server to provide an interface. 
- Addition of a notification window on the bottom right of the screen.
- Ability to launch secondary app from each of listed vehicles to show other info / send POST requests to the vehicles.

### Icons by icons 8
https://icons8.com"

The following icons were sourced from icons 8: 
- images/active.png
- images/inactive.png
- images/app_icon.png
- images/tank_dark.png
- images/tank_light.png
- images/uav_dark.png
- images/uav_light.png
