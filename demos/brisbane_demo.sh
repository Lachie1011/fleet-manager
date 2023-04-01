#!/bin/bash

## This is a scipt to demo the UAV App over brisbane
## To be run with a running UAVApp
## It only publishes locations to one UAV with callsign: alpha1 
## It curls POST requests over a block in brisbane indefinetly or until ctrl-c is pressed

## Data grabbed from www.geoplanner.com

echo "[INFO]  starting brisbane demo"
echo "[INFO]  press ctrl-c to exit"

## loops forever publishing locations
while [ 1 ]
do
    curl -X POST -F "callsign=alpha1" -F "lat=-27.46988" -F "long=153.02282" 127.0.0.1:8500/update/location
    sleep 1
    curl -X POST -F "callsign=alpha1" -F "lat=-27.46788" -F "long=153.02518" 127.0.0.1:8500/update/location
    sleep 1 
    curl -X POST -F "callsign=alpha1" -F "lat=-27.469128" -F "long=153.02756" 127.0.0.1:8500/update/location
    sleep 1 
    curl -X POST -F "callsign=alpha1" -F "lat=-27.47101" -F "long=153.02951" 127.0.0.1:8500/update/location
    sleep 1 
    curl -X POST -F "callsign=alpha1" -F "lat=-27.47253" -F "long=153.0281" 127.0.0.1:8500/update/location
    sleep 1 
    curl -X POST -F "callsign=alpha1" -F "lat=-27.47344" -F "long=153.02591" 127.0.0.1:8500/update/location
    sleep 1
    curl -X POST -F "callsign=alpha1" -F "lat=-27.47171" -F "long=153.02404" 127.0.0.1:8500/update/location
    sleep 1
done
