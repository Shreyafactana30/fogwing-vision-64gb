#!/bin/bash

# Run this script in display 0 - the monitor
export DISPLAY=:0

# Run Chromium and open tabs
firefox --disable-pinch --kiosk http://localhost &

sleep 1
# Hide the mouse from the display
unclutter &
