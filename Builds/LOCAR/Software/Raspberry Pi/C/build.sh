#!/bin/bash
#
# Automated Build Bash Script
#
# Fluvio L Lobo Fenoglietto 02/28/2019
#

# Formatting Def. =================================================== #
RED='\033[0;31m'	# RED
GREEN='\033[0;32m'	# GREEN
LPURPLE='\033[1;35m'	# LIGTH PURPLE
NC='\033[0m'		# No COLOR


# EXECUTION ========================================================= #
echo "${LPURPLE}### STARTING MAGNETO SETUP ############${NC}"

echo "${GREEN}[1] MAKING LSM9DS1 LIBRARIES...${NC}"
# Currently using the relative of the repository
cd ../ ; cd Libraries/LSM9DS1_RaspberryPi_Library/
# ...
echo "${RED}WARNING: Program will remove previous/old builds...${NC}"
# Clean libraries
#sudo make clean
# Make libraries
sudo make
# Install libraries
echo "${GREEN}[2] INSTALLING LSM9DS1 LIBRARIES${NC}"
sudo make install

echo "${GREEN}[3] INSTALL DEPENDENCIES OR LEVMAR SOLVER${NC}"
sudo apt install f2c liblapack-dev gfortran libblas-dev

echo "${GREEN}[4] MAKE LEVMAR SOLVER${NC}"
# Change to levmar directory
cd ../ ; cd levmar-2.6/
# ...
echo "${RED}WARNING: Program will remove previous/old builds...${NC}"
# Clean lavmar
#sudo make clean
# Build levmar
sudo make

# Copy levmar build to /usr/lib
echo "Creating liblevmar.a copy in /usr/local/lib"
sudo cp liblevmar.a /usr/local/lib

echo "${GREEN}[5] MAKE MAGNETO${NC}"
# Move to magneto C directory
cd ../../ ; cd C/
# ...
echo "${RED}WARNING: Program will remove previous/old builds...${NC}"
# Clean magneto
sudo make clean
# Make magneto
sudo make

echo "${LPURPLE}### PROGRAM COMPLETE ###################${NC}"
