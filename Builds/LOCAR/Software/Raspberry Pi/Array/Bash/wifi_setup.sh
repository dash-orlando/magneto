#!/bin/bash
#
# Automated WiFi Setup for Array Pis
#
# Fluvio L. Lobo Fenoglietto 03/12/2019
#

# Formatting Def. =================================================== #
RED='\033[0;31m'	# RED
GREEN='\033[0;32m'	# GREEN
LPURPLE='\033[1;35m'	# LIGTH PURPLE
NC='\033[0m'		# No COLOR

# EXECUTION ========================================================= #
echo "${LPURPLE}# STARTING WiFi SETUP FOR ARRAY PI ##############${NC}"
echo "${LPURPLE}-------------------------------------------------${NC}"
echo "${GREEN} The following program will force the Pi to connect to a default WiFi Network. Changes are not permanent and can be reverted. ${NC}"
echo "${LPURPLE}-------------------------------------------------${NC}"

# 1. Create local copy of the original wap config. file
echo "${GREEN} 1. Creating original copy of 'wpa_supplicant.conf'${NC}"
sudo mv /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant_orig.conf
sudo cp wpa_supplicant_mod.conf /etc/wpa_supplicant/wpa_supplicant.conf

# 2. Restart WiFi Connections
echo "${GREEN} 2. Restarting Pi in 5 sec.${NC}"
echo "${LPURPLE}# PROGRAM COMPLETED #############################${NC}"
sleep 5
sudo reboot

