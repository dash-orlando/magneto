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

echo -e "\e[92mshutdown complete"
echo "you may close the terminal now"
$SHELL