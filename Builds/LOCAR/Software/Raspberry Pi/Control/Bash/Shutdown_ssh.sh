#!/bin/bash
echo "beginning shutdown process"
echo "establishing ssh conection 1"
echo -e "\e[4m192.168.4.15\e[0m"

sudo sshpass -p "raspberry" ssh -o StrictHostKeyChecking=no pi@192.168.4.15 "sudo shutdown -h now"
echo -e "\e[31mShutdown\e[0m"

echo "establishing ssh conection 2"
echo -e "\e[4m192.168.4.18\e[0m"

sudo sshpass -p "raspberry" ssh -o StrictHostKeyChecking=no pi@192.168.4.18 "sudo shutdown -h now"
echo -e "\e[31mShutdown\e[0m"

echo -e "\e[92mSSH shutdown complete\e[0m"
sek=10
echo -e "\e[31mShutting down in $sek seconds"
while [ $sek -ge 1 ]
do
  echo -ne "Shutting down in $sek... \r"
  sleep 1
  sek=$[$sek-1 ]
done
echo
echo "Shutting Down"
sudo shutdown now
$SHELL