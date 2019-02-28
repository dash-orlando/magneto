#!/bin/bash
#
# Automated Build Bash Script
#
# Fluvio L Lobo Fenoglietto 02/28/2019
#
echo "### STARTING MAGNETO SETUP ###"

echo "[1] MAKING LSM9DS1 LIBRARIES..."
# Currently using the relative of the repository
cd ../ ; cd Libraries/LSM9DS1_RaspberryPi_Library/
# Make libraries
sudo make

echo "[2] INSTALLING LSM9DS1 LIBRARIES"
sudo make install

echo "[3] INSTALL DEPENDENCIES OR LEVMAR SOLVER"
sudo apt install f2c liblapack-dev gfortran libblas-dev

echo "[4] MAKE LEVMAR SOLVER"
# Change to levmar directory
cd ../ ; cd levmar-2.6/
# Build levmar
sudo make
# Copy levmar build to /usr/lib
echo "Creating liblevmar.a copy in /usr/local/lib"
sudo cp liblevmar.a /usr/local/lib

echo "[5] MAKE MAGNETO"
# Move to magneto C directory
cd ../../ ; cd C/
# make magneto
sudo make



