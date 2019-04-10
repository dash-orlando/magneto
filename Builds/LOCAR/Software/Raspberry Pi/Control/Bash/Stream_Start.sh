#!/bin/bash

source ~/.profile
echo "Profile set"

workon magneto
echo "Working on magneto virtual environment"
echo "Running program now"
echo "Press q to exit"
sudo python3 pi_camera.py