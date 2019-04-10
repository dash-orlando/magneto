#!/bin/bash

############## WELCOME #############
# Get command line argument for verbose
echo "Welcome to OpenCV 3.4 Installation Script for Raspbian Stretch"
echo "This script is a modified version from LearnOpenCV.com"
echo "By using this script you agree to surrender your first born to the"
echo "Thunder GOD"
echo "Now lets begin"

echo "Preparing system for installation..."
sudo apt-get -y purge wolfram-engine
sudo apt-get -y purge libreoffice*
sudo apt-get -y clean
sudo apt-get -y autoremove

######### VERBOSE ON ##########

# Step 0: Take inputs
echo "OpenCV installation"

cvVersion="3.4"

# Clean build directories
rm -rf opencv/build
rm -rf opencv_contrib/build

# Save current working directory
cwd=$(pwd)

# Step 1: Update packages
echo "Updating packages"

sudo apt-get -y update
sudo apt-get -y upgrade
echo "================================"

echo "Complete"

# Step 2: Install OS libraries
echo "Installing OS libraries"

sudo apt-get -y remove x264 libx264-dev

## Install dependencies
sudo apt-get -y install build-essential checkinstall cmake pkg-config yasm
sudo apt-get -y install git gfortran
sudo apt-get -y install libjpeg8-dev libjasper-dev libpng12-dev

sudo apt-get -y install libtiff5-dev

sudo apt-get -y install libtiff-dev

sudo apt-get -y install libavcodec-dev libavformat-dev libswscale-dev libdc1394-22-dev
sudo apt-get -y install libxine2-dev libv4l-dev
cd /usr/include/linux
sudo ln -s -f ../libv4l1-videodev.h videodev.h
cd $cwd

sudo apt-get -y install libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev
sudo apt-get -y install libgtk2.0-dev libtbb-dev qt5-default
sudo apt-get -y install libatlas-base-dev
sudo apt-get -y install libmp3lame-dev libtheora-dev
sudo apt-get -y install libvorbis-dev libxvidcore-dev libx264-dev
sudo apt-get -y install libopencore-amrnb-dev libopencore-amrwb-dev
sudo apt-get -y install libavresample-dev
sudo apt-get -y install x264 v4l-utils

# Optional dependencies
sudo apt-get -y install libprotobuf-dev protobuf-compiler
sudo apt-get -y install libgoogle-glog-dev libgflags-dev
sudo apt-get -y install libgphoto2-dev libeigen3-dev libhdf5-dev doxygen
echo "================================"

echo "Complete"


# Step 3: Install Python libraries
echo "Install Python libraries"

sudo apt-get -y install python3-dev python3-pip python3-venv
sudo -H pip3 install -U pip numpy
sudo apt-get -y install python3-testresources

############ For Python 3 ############
sudo sed -i 's/CONF_SWAPSIZE=100/CONF_SWAPSIZE=1024/g' /etc/dphys-swapfile
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start
pip install numpy
######################################

echo "================================"
echo "Complete"

# Step 4: Download opencv and opencv_contrib
#echo "Downloading opencv and opencv_contrib"
#git clone https://github.com/opencv/opencv.git
#cd opencv
#git checkout "$cvVersion"

#cd ..

#git clone https://github.com/opencv/opencv_contrib.git
#cd opencv_contrib
#git checkout "$cvVersion"

#cd ..
echo "================================"
echo "Complete"

# Step 5: Compile and install OpenCV with contrib modules
echo "================================"
echo "Compiling and installing OpenCV with contrib modules"
cd opencv
mkdir build
cd build

cmake -D CMAKE_BUILD_TYPE=RELEASE \
            -D CMAKE_INSTALL_PREFIX=/usr/local \
            -D INSTALL_PYTHON_EXAMPLES=ON \
            -D WITH_TBB=ON \
            -D WITH_V4L=ON \
        -D WITH_QT=ON \
        -D WITH_OPENGL=ON \
        -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
        -D BUILD_EXAMPLES=ON ..

make -j$(nproc)
make install

cd

sudo sed -i 's/CONF_SWAPSIZE=1024/CONF_SWAPSIZE=100/g' /etc/dphys-swapfile
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start
echo "sudo modprobe bcm2835-v4l2" >> ~/.profile
echo "Finally!"
echo "OpenCV 3.4 install complete!"
