# Python Streaming and Lighting Scripts

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

