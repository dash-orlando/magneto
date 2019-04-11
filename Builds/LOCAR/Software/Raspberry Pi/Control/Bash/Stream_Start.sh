#!/bin/bash

source ~/.profile
echo "Profile set"

workon magneto
echo -e "Working on \e[4mmagneto virtual environment\e[0m"
echo -e "Running program now"
echo -e "\e[92mPress 'q' to exit on stream window\e[0m"

sudo python3 pi_camera.py