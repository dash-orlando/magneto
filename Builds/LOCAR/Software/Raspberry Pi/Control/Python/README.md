# Python Streaming and Lighting On Raspberry Pi

## Installation
clone this repo and make note of its directory for later linking to virtual environment
such as ```"/home/pi/pd3d/magneto/Builds/LOCAR/Software/Raspberry Pi/Control/Python/scripts"```
### Prepare system
```
sudo apt-get -y purge wolfram-engine
sudo apt-get -y purge libreoffice*
sudo apt-get -y clean
sudo apt-get -y autoremove
```
### Run the standard updates
```
sudo apt-get update
sudo apt-get upgrade
sudo pip3 install --upgrade setuptools
```
### Enable I2C and SPI and camera
run
```
sudo apt-get install -y python-smbus
sudo apt-get install -y i2c-tools
```
then enable in config
```
sudo raspi-config
```
go to interfacing options (5)
and enable camera, SPI, and I2C
then reboot 
```
sudo reboot
```
then verify with
```
ls /dev/i2c* /dev/spi*
```
you should see response ```/dev/i2c-1 /dev/spidev0.0 /dev/spidev0.1```

### Install pip if needed
```
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
```
### Install prerequisites
```
sudo apt-get install libhdf5-dev libhdf5-serial-dev
sudo apt-get install libqtwebkit4 libqt4-test
```
### Install virtualenv and virtualenvwrapper
```
pip3 install virtualenv virtualenvwrapper
```
>**NOTE** basic __virtualenvwrapper__ commands
>>Create an environment with ```mkvirtualenv ENVNAME``` .
>>
>>Activate an environment (or switch to a different one) with ```workon ENVNAME``` .
>>
>>Deactivate an environment with ```deactivate``` .
>>
>>Remove an environment with ```rmvirtualenv ENVNAME``` .
>>
>>We will be using ```mkvirtualenv [-a project_path] [-r requirements_file] [virtualenv options] ENVNAME```
>>for creating our environment

### Change ~/.profile
use nano to add these lines to the end of the file```nano ~/.profile```
```
# virtualenv and virtualenvwrapper
export WORKON_HOME=$HOME/.virtualenvs
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
source /usr/local/bin/virtualenvwrapper.sh
```
then source it
```
source ~/.profile
```
### Create virtual environment
**for easier install create the virtual environment with -r argument with the requirements.txt
from the _controls/python/_ directory**
>change the directory to the scripts folder in the magneto repo
>**make sure your directory is correct for your Pi**
>
>```cd "/home/pi/pd3d/magneto/Builds/LOCAR/Software/Raspberry Pi/Control/Python/scripts"```
>
>```mkvirtualenv magneto -p python3 -r requirements.txt -a "/home/pi/pd3d/magneto/Builds/LOCAR```
```/Software/RaspberryPi/Control/Python/scripts"```
>
>-r pip installs all libraries with their respective versions
>
>-a sets the project dir, so when workon is called it auto cd's to that location
**If you want to install libraries from scratch**
```
mkvirtualenv magneto -p python3
```
### Install Python libraries
```
pip3 install RPI.GPIO
pip3 install adafruit-blinka
pip3 install adafruit-circuitpython-neopixel
pip3 install numpy
pip3 install picamera
pip3 install opencv-contrib-python==3.4.5.20
```
test with blinkatest.py script
try running led test code (needs root access)
```
sudo python3 led_test.py
```
>**NOTE**if LED's look odd try reversing pixel color order from RGBW tp GRBW

the raspberry pi is set to run a virtual environment with open cv and other libraries called "magneto"

## Execution
>**NOTE** all scripts with neopixel lighting need to be run as ROOT with sudo command

ensure system variable are set correctly for terminal, run 
```
source ~/.profile
```

to switch to the magneto virtual environment run the **workon** command
```
workon magneto
```
>if this worked properly you should now see _magneto_ in front of the cwd

>like such, ```(magneto) pi@raspberrypi:~/pd3d/magneto/Builds/LOCAR/Software/Raspberry Pi/Control
/Python/scripts```
>
>this should change the directory to the scripts folder, if not change the directory yourself
```
cd "/home/pi/pd3d/magneto/Builds/LOCAR/Software/Raspberry Pi/Control/Python/scripts"
```

now run the _pi_camera.py_ script **WITH SUDO**
```
sudo python3 pi_camera.py
```

### Operation
a screen with the video stream and a slider should appear
>the slider controls brightness of the LED's, from off to full brightnessof (0-255)

you can run the script along with these arguments to change the window size
>**NOTE** by default the script runs with a re-sizable window
>
>use```-f``` to run **fullscreen** 
>
>use```-half``` to run half screen
>> **NOTE** the default native resolution is 1920x1080 if the screen used is different you need to run
>>```-res``` argument to input the screen resolution **ex:** ```-res 1920 1080```
>
>use```-c``` for custom window size with```-x width``` and ```-y height``` (in pixels)

