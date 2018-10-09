"""
usbProtocol.py

The following module has been created to manage the bluetooth interface between the control system and the connected devices

Michael Xynidis
Fluvio L Lobo Fenoglietto
09/01/2016


"""

# Import Libraries and/or Modules
import  os, serial, time
#from    timeStamp           import  *

# Create USB Port
def createUSBPort( deviceName, portNumber, baudrate):
    #print fullStamp() + " createUSBPort()"
    usbObject = serial.Serial(
        port = "COM" + str(portNumber),
        baudrate = baudrate)
    time.sleep(1)
    #usbConnectionCheck(usbObject,deviceName,portNumber,baudrate,attempts)
    usbObject.close()
    return usbObject
