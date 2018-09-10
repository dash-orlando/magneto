"""
bluetoothProtocol.py

The following module has been created to manage the bluetooth interface between the control system and the connected devices

Michael Xynidis
Fluvio L Lobo Fenoglietto
09/01/2016

Modified by : Mohammad Odeh
Date        : May 31st, 2017
Changes     : Modified protocol to use PyBluez instead of PySerial
"""

# Import Libraries and/or Modules
import bluetooth
"""
        Implementation of the "bluetooth" module may require the installation of the python-bluez package
        >> sudp apt-get install python-bluez
"""
import  os, time, serial
import  protocolDefinitions as definitions
from    timeStamp           import *

# Find RF Device
#   This function uses the hardware of the peripheral device or control system to scan/find bluetooth enabled devices
#   This function does not differenciate among found devices
#   Input   ::  None
#   Output  ::  {array, list} "availableDeviceNames", "availableDeviceBTAddresses"
def findDevices():
    print( fullStamp() + " findDevices()" )
    
    devices = bluetooth.discover_devices( duration=5, lookup_names=True)
    Ndevices = len(devices)                                                                 # Number of detected devices
    availableDeviceNames = []                                                               # Initialized arrays/lists for device names...
    availableDeviceBTAddresses = []                                                         # ...and their bluetooth addresses

    for i in range(0,Ndevices):                                                             # Populate device name and bluetooth address arrays/lists with a for-loop

        availableDeviceNames.append(devices[i][1])
        availableDeviceBTAddresses.append(devices[i][0])
        
    print( fullStamp() + " Devices found (names): " + str(availableDeviceNames) )           # Print the list of devices found
    print( fullStamp() + " Devices found (addresses): " + str(availableDeviceBTAddresses) ) # Print the list of addresses for the devices found

    return availableDeviceNames, availableDeviceBTAddresses                                # Return arrays/lists of devices and bluetooth addresses

# Identify Smart Device - Specific
#   This function searches through the list of detected devices and finds the specific smart device corresponding to the input name
#   Input   ::  {string}     "smartDeviceAddress"
#   Output  ::  {array/list} "smartDeviceNames", "smartDeviceBTAddresses"
def findSmartDevice( address_device2find ):
    print( fullStamp() + " findSmartDevice()" )
    
    devices = bluetooth.discover_devices( duration=5, lookup_names=True )
    availableDeviceName = []
    availableDeviceBTAddress = []

    for i in range( 0, len(devices) ):
        if devices[i][0] == address_device2find:
            availableDeviceName.append(devices[i][1])
            availableDeviceBTAddress.append(devices[i][0])
            
            print( fullStamp() + " Found device with name: " + str(availableDeviceName) )
            print( fullStamp() + " Found device with address: " + str(availableDeviceBTAddress) )

            return availableDeviceName, availableDeviceBTAddress

    print( fullStamp() + " Device with address " + address_device2find + " not found" )
    return 0, 0

#   Create Port
def createBTPort( bt_addr, port ):
    print( fullStamp() + " createBTPort()" )
    if bluetooth.is_valid_address(bt_addr) is True:                 # Check if address is valid
        socket = bluetooth.BluetoothSocket( bluetooth.RFCOMM )      # Create a BT socket
        socket.connect( (bt_addr, port) )                           # Connect to socket
        time.sleep(1)
        BTconnectionCheck( socket )
        return(socket)
    else:
        print( fullStamp() + " Invalid BT address" )
        return 0

#   Connection Check
def BTconnectionCheck( socket ):
    outByte = definitions.ENQ
    socket.send(outByte)
    inByte = socket.recv(1)     # recv(buffersize)

    if inByte == definitions.ACK:
        print( fullStamp() + " ACK Connection Established" )
    
    elif inByte == definitions.NAK:
        print( fullStamp() + " NAK device NOT READY" )

    else:
        print( fullStamp() + " Please troubleshoot devices" )

#   Why not?
def closeBTPort( socket ):
    print( fullStamp() + " closeBTPort()" )
    socket.close()
    print( fullStamp() + " Port Closed" )



# ==========================================================================================
# ================================== PySerial Stuff ========================================
def createPort(deviceName,portNumber,deviceBTAddress,baudrate,attempts):
    print fullStamp() + " createPort()"
    portRelease("rfcomm",portNumber)                                                        # The program performs a port-release to ensure that the desired rf port is available
    portBind("rfcomm",portNumber,deviceBTAddress)
    rfObject = serial.Serial(
        port = "/dev/rfcomm" + str(portNumber),
        baudrate = baudrate,
        bytesize = serial.EIGHTBITS,
        parity = serial.PARITY_NONE,
        stopbits = serial.STOPBITS_ONE)
    time.sleep(1)
    connectionCheck(rfObject,deviceName,portNumber,deviceBTAddress,baudrate,attempts)
    rfObject.close()
    return(rfObject)

#   Connection Check
def connectionCheck(rfObject,deviceName,portNumber,deviceBTAddress,baudrate,attempts):
    outByte = definitions.ENQ                                                               # Send SOH (Start of Heading) byte - see protocolDefinitions.py
    rfObject.write(outByte)
    inByte = rfObject.read(size=1)
    if inByte == definitions.ACK:                                                           # Check for ACK / NAK response
        print fullStamp() + " ACK Connection Established"
        rfObject.close()
        return rfObject
    
    elif inByte == definitions.NAK:
        print fullStamp() + " NAK device NOT READY"

    else:
        rfObject.close()
        if attempts is not 0:
            return createPort(deviceName,portNumber,deviceBTAddress,baudrate,attempts-1,q)
        elif attempts is 0:
            print fullStamp() + " Attempts limit reached"
            print fullStamp() + " Please troubleshoot devices"

# Port Bind
#   This function binds the specified bluetooth device to a rfcomm port
#   Input   ::  {string} port type, {int} port number, {string} bluetooth address of device
#   Output  ::  None -- Terminal messages
def portBind(portType, portNumber, deviceBTAddress):
    print fullStamp() + " Connecting device to " + portType + str(portNumber)               # Terminal message, program status
    os.system("sudo " + portType + " bind /dev/" + portType + str(portNumber) + " " + deviceBTAddress)     # Bind bluetooth device to control system

# Port Release
#   This function releases the specified communication port (serial) given the type and the number
#   Input   ::  {string} "portType", {int} "portNumber"
#   Output  ::  None -- Terminal messages
def portRelease(portType, portNumber):
    print fullStamp() + " Releasing " + portType + str(portNumber)                          # Terminal message, program status
    os.system("sudo " + portType + " release " + str(portNumber))                           # Releasing port through terminal commands
