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

"""
FUNCTIONS
"""

def createUSBPort( deviceName, portPrefix, portNumber, baudrate):
    """
    CREATE USB PORT
        input;
            deviceName (string) --name of the input device (for reference)
            portPrefix (string) --prefix based on the operating system of the control system/computer
                                = /dev/ttyACM --Linux
                                = COM --Windows
            portNumber (num)    --communication port number
            baudrate   (num)    --communication baudrate (bps)
            
        output;
            usbObject  (object) --serial object
    """
    #print fullStamp() + " createUSBPort()"
    usbObject = serial.Serial(
        port = portPrefix + str(portNumber),
        baudrate = baudrate)
    time.sleep(1)
    #usbConnectionCheck(usbObject,deviceName,portNumber,baudrate,attempts)
    usbObject.close()
    return usbObject
