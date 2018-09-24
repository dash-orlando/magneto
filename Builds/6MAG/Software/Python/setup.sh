#!/bin/bash/
##########################
# Installation of Packages
##########################

## Run update
echo ">> Updating OS"
#sudo apt-get update -y

## Bootstrap pip
echo ">> Downloading  pip"
#sudo curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
echo ">>> Installing pip for python2"
#sudo python get-pip.py
echo ">>> Installing pip for python3"
#sudo python3 get-pip.py

## Upgrading pip
echo ">>> Upgrading pip for python2"
#sudo python -m pip install -U pip
echo ">>> Upgrading pip for python3"
#sudo python3 -m pip install -U pip

## Installing numpy using pip
echo ">> Installing numpy"
echo ">>> Installing numpy for python2"
#sudo python -m pip install numpy
echo ">>> Installing numpy for python3"
#sudo python3 -m pip install numpy

## Installing scipy using pip
echo ">> Installing scipy for python2"
#sudo python -m pip install scipy
#sudo python3 -m pip install scipy

## Python-dev packages (needed for Vtk and Mayavi)
echo ">> Installing Python-Dev"
#sudo apt-get install python-dev -y
#sudo apt-get install python3-dev -y

## Installing Vtk
echo ">> Installing Vtk"
#sudo python -m pip install vtk
#sudo python3 -m pip install vtk

## Installing MayaVi
echo ">> Installing MayaVi"
#sudo python -m pip install mayavi
#sudo python3 -m pip install mayavi

## Install PyQt support
echo ">>Installing PyQt support"
sudo apt-get install python-qt4 -y

## Install Pyserial
echo ">> Installing Pyserial for USB Communication"
#sudo python -m pip install pyserial
#sudo python3 -m pip install pyserial


