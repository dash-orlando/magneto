# Python Streaming and Lighting On Raspberry Pi

The raspberry pi is set to run a virtual environment called "magneto" with opencv and other libraries.

## Installation
clone this repo and make note of its directory for later linking to virtual environment
such as 
`"/home/pi/pd3d/magneto/Builds/LOCAR/Software/Raspberry Pi/Control/Python"`

change `/home/pi/pd3d/` as needed based on where you cloned in commands that ask for full path

### Step 1: Prepare system
purge unneeded programs
```
sudo apt-get -y purge wolfram-engine
sudo apt-get -y purge libreoffice*
sudo apt-get -y clean
sudo apt-get -y autoremove
```
standard updates
```
sudo apt-get update
sudo apt-get upgrade
sudo pip3 install --upgrade setuptools
```
tools for GPIO
```
sudo apt-get install -y python-smbus
sudo apt-get install -y i2c-tools
```
prerequisites for opencv
```
sudo apt-get install libhdf5-dev libhdf5-serial-dev
sudo apt-get install libqtwebkit4 libqt4-test
```

### Step 2: Enable I2C and SPI and camera
enable in config
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
you should see response `/dev/i2c-1 /dev/spidev0.0 /dev/spidev0.1`

### Step 3: Setup virtual environment and install libraries
intall pip if not installed already
```
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
```
install virtualenv and virtualenvwrapper
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
>>We will be using `mkvirtualenv [-a project_path] [-r requirements_file] [virtualenv options] ENVNAME`
and `setvirtualenvproject`
>>for creating our environment

change ~/.profile
use nano to add these lines to the end of the file`nano ~/.profile`
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
>**NOTE** use `source ~/.profile` each time you open the terminal to allow workon commands

**for easier install create the virtual environment with -r argument with the requirements.txt
from the `/controls/python/` directory**

Using -r requirements.txt to install libraries
>change the directory to the scripts folder in the magneto repo
**make sure your directory is correct for your Pi**

```
cd "/home/pi/pd3d/magneto/Builds/LOCAR/Software/Raspberry Pi/Control/Python"

mkvirtualenv magneto -p python3 -r requirements.txt -a "/home/pi/pd3d/magneto/Builds/LOCAR
/Software/RaspberryPi/Control/Python"
```

>`-r` pip installs all libraries with their respective versions
>
>`-a` sets the project directory, so when workon is called it auto cd's to that location

Install libraries from scratch
```
mkvirtualenv magneto -p python3
cd "/home/pi/pd3d/magneto/Builds/LOCAR/Software/Raspberry Pi/Control/Python"
setvirtualenvproject
pip3 install RPI.GPIO
pip3 install adafruit-blinka
pip3 install adafruit-circuitpython-neopixel
pip3 install numpy
pip3 install picamera
pip3 install opencv-contrib-python==3.4.5.20
```

### Step 4: Test functionality
Test Camera
```
raspistill -o output.jpg
```
should display a preview of the image, and then after a few seconds, snap a picture

Test cv2
```
workon magneto
python
>>> import cv2
>>> cv2.__version__
'3.4.5.20'
```
if you see this you should have it working properly

Test I2C and SPI
run blinkatest.py script

`python3 blinkatest.py`

Test LED's
try running led test code (needs root access)

`sudo python3 led_test.py`

**NOTE** if LED's look odd try reversing pixel color order from RGBW to GRBW
>it should function in a sequence of red, green, blue, then a rainbow wave


## Execution
>**NOTE** all scripts with neopixel lighting need to be run as ROOT with sudo command
>
>**IMPORTANT** there is a "Stream Start.desktop" file in the `/Control/Bash` folder, drag this to the desktop to run the program via executable

### Double click **Stream Start** on desktop to run
press `q` to exit stream

adjust brightness of LED ring via slider bar

### Or run via terminal for additional options

ensure system variable are set correctly for terminal, run 
```
source ~/.profile
```

to switch to the magneto virtual environment run the **workon** command
```
workon magneto
```
>if this worked properly you should now see _magneto_ in front of the cwd

>like such, `(magneto) pi@raspberrypi:~/pd3d/magneto/Builds/LOCAR/Software/Raspberry Pi/Control
/Python`
>
>this should change the directory to the scripts folder, if not change the directory yourself
```
cd "/home/pi/pd3d/magneto/Builds/LOCAR/Software/Raspberry Pi/Control/Python"
```

now run the _pi_camera.py_ script **WITH SUDO**
```
sudo python3 pi_camera.py
```

### Operation
a screen with the video stream and a slider should appear
>the slider controls brightness of the LED's, from off to full brightnessof (0-255)

to **shutdown** or "quit" the script press the `q` or `Q` key while focused on the stream window

you can run the script along with these arguments to change the window size
>**NOTE** by default the script runs with a re-sizable window
>
>use`-f` to run fullscreen 
>
>use`-half` to run half screen
>> **NOTE** the default native resolution is 1920x1080 if the screen used is different you need to run
>>`-res` argument to input the screen resolution **ex:** ```-res 1920 1080```
>
>use`-c` for custom window size with`-x width` and `-y height` (in pixels)

## Troubleshooting
if LED lights are buggy do full restart of pi
