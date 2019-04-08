# Setup for Raspberry Pi to Work with Opencv, PiCamera, and Neopixel

## Install opencv 3.4 for python 3 with bash script or follow along

remeber to change and link virtualenv to install
```
cd /usr/local/lib/python3.5/site-packages/
sudo mv cv2.cpython-35m-arm-linux-gnueabihf.so cv2.so
cd ~/.virtualenvs/cv/lib/python3.5/site-packages/
ln -s /usr/local/lib/python3.5/dist-packages/cv2/python-3.5/cv2.so cv2.so
```

#Run the standard updates
```
sudo apt-get update
sudo apt-get upgrade
sudo pip3 install --upgrade setuptools
```

#Enable I2C and SPI and camera
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

#Install Python libraries
```
pip3 install RPI.GPIO
pip3 install adafruit-blinka
```
test with blinkatest.py script

#Python Installation of NeoPixel Library
```
sudo pip3 install adafruit-circuitpython-neopixel
```
try running led test code (needs root access)
```
sudo python3 led_test.py
```
if LED's look odd try reversing pixel color order from RGBW tp GRBW

