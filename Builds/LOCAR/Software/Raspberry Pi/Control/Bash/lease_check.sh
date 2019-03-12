#!/bin/bas
#
# Simplified Check for iP Address Leases
#
# Fluvio L Lobo Fenoglietto 03/12/2019
#

# Formatting Def. =================================================== #
RED='\033[0;31m'	# RED
GREEN='\033[0;32m'	# GREEN
LPURPLE='\033[1;35m'	# LIGTH PURPLE
NC='\033[0m'		# No COLOR

# EXECUTION ========================================================= #
echo "${LPURPLE}# CURRENT LEASES ################################${NC}"
echo "${LPURPLE}-------------------------------------------------${NC}"
echo "${GREEN} The following iP address have been leased thus far...${NC}"
echo "${LPURPLE}-------------------------------------------------${NC}"

while IFS="" read -r p || [ -n "$p" ]
do
  printf '%s\n' "$p"
done < /var/lib/misc/dnsmasq.leases

