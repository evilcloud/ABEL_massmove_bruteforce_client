#!/bin/bash

while true; do
    active_app=$(osascript -e 'tell application "System Events" to get the name of every process whose frontmost is true')
    echo "Currently active application: $active_app"
    sleep 5
done

