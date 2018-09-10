'''
Position tracking of magnet

Author: Danny, Moe
Date: Aug. 4th, 2017th year of our Lord
'''

# Import Modules
import  serial, math
import  numpy           as      np
import  pyqtgraph       as      pg
from    pyqtgraph.Qt    import  QtGui, QtCore, USE_PYSIDE, USE_PYQT5
from    pyqtgraph.ptime import  time
from    UISetup         import  Ui_Form
from    threading       import  Thread
from    Queue           import  Queue
from    usbProtocol     import  createUSBPort
from    time            import  sleep

######################################################
#                   FUNCTION DEFINITIONS
######################################################

# Define plot updating function, called once as part of Qt application event loop
def update():
    global data, curve, p
    try:
        p.clear()
        curve = pg.ScatterPlotItem( x=data[0],
                                    y=data[1],
                                    pen='w',
                                    brush='b',
                                    size=ui.sizeSpin.value(),
                                    pxMode=ui.pixelModeCheck.isChecked() )
        p.addItem(curve)
        p.repaint()

    except Exception as e:
        print( "Caught error in update()"       )
        print( "Error type %s" %str(type(e))    )
        print( "Error Arguments " + str(e.args) )
            
# Define getData (pool data from Arduino), started as a thread; always updating values to queue Q_getData
def getData( Q_getData ):

    #Sample size of Arduino data per refresh.
    n = 25
    
    #Declaring arrays to store calculated values. 
    valu0=[]
    valu1=[]

    #Entering the calculation loop. Reading a line of input data (6 comma separated values) and splitting them into an array.
    while True:

        try: 
            line = ser.readline()[:-1]
            col = line.split(",")

            #Throwing out bad data. Waiting for the sensor to calibrate itself to ambient fields. 
            if len(col) < 6:
                print "Waiting..."

            else:
                #Casting the split input values as floats.
                imux0=float(col[0])
                imuy0=float(col[1])
                imuz0=float(col[2])
                imux1=float(col[3])
                imuy1=float(col[4])
                imuz1=float(col[5])

                #Doing math to find the magnitude of the magnetic field, B, from the POV of each IMU
                imuB0 = math.sqrt( math.pow(imux0,2) + math.pow(imuy0,2) + math.pow(imuz0,2) )
                imuB1 = math.sqrt( math.pow(imux1,2) + math.pow(imuy1,2) + math.pow(imuz1,2) )

                #Each sensor has its own empirically derived calibration curve:
                #Sensor0: [AbsoluteDistance_to_Sensor0] = 95.01*[Magnitude_B0]^(-0.308)
                #Sensor1: [AbsoluteDistance_to_Sensor0] = 105.41*[Magnitude_B1]^(-0.325)
                
                #Calculating distance from IMUx using the value of Bx
                factorB0 = math.pow(imuB0,0.308)
                factorB1 = math.pow(imuB1,0.325)

                #The radial distance of the magnet from each Sensor, result
                d0 = 95.01/factorB0      #Radial distance from first sensor
                d1 = 105.41/factorB1     #Radial distance from second sensor
                #Really accurate! ^_^

                #Calculating angle above the x-axis, Theta from known values
                #length_apart is the minimum distance between the center of the two IMU sensors in [millimeters], given by design.

                length_apart    =   225
                # If in the left quadrant
                if d0 < d1:
                    cosnum          =   math.pow(length_apart, 2) + math.pow(d0, 2) - math.pow(d1, 2)
                    cosden          =   2*d1*length_apart
                    thetarad        =   np.arccos(cosnum/cosden)
                    #theta           =   math.degrees(thetarad)

                    # Calculate distances
                    x = float( d0 * math.cos(thetarad) )
                    y = float( d0 * math.sin(thetarad) )
                
                # If in the right quadrant
                elif d0 > d1:
                    cosnum          =   math.pow(length_apart, 2) + math.pow(d1, 2) - math.pow(d0, 2)
                    cosden          =   2*d0*length_apart
                    thetarad        =   np.arccos(cosnum/cosden)
                    #theta           =   math.degrees(thetarad)

                    # Calculate distances
                    x = float( length_apart - d1 * math.cos(thetarad))
                    y = float( d1 * math.sin(thetarad)   )

                else:
                    pass

##                cosine0 = (math.pow(length_apart, 2) + math.pow(d0, 2) - math.pow(d1, 2)) / (2*d1*length_apart)
##                sine0   = math.sqrt(1-math.pow(cosine0, 2))


                if (math.isnan(x) == False) and (math.isnan(y) == False):
                    valu0.append(x)
                    valu1.append(y)
                
                if ( len(valu0) and len(valu1) ) == n:
                    # Place data in queue for retrieval
                    Q_getData.put( [valu0, valu1] )
                    print( "x: %r, y: %r" %(valu0[0], valu1[0]) )
                    print( "d0: %r, d1: %r" %(d0, d1) )
                    # Reset arrays
                    del valu0[:]
                    del valu1[:]

        except Exception as e:
            print( "Caught error in getData()"      )
            print( "Error type %s" %str(type(e))    )
            print( "Error Arguments " + str(e.args) )

# Define function to update from pooled data
def queueBuffers( Q_getData, Q_stuff ):
    try:
        while True:
            #print ("Waiting for values")
            # Fetch data from stack
            if Q_getData.qsize() > 0:
                #print ("Got values")
                data = Q_getData.get()
                Q_stuff.put( data )

    except Exception as e:
        print( "Caught error in queueBuffers()" )
        print( "Error type %s" %str(type(e)) )
        print( " Error Arguments " + str(e.args) )

######################################################
#                   SETUP PROGRAM
######################################################
# Setup UI
app = QtGui.QApplication([])
win = QtGui.QWidget()
win.setWindowTitle( 'ScatterPlot' )
ui = Ui_Form()
ui.setupUi(win)
win.show()

# Setup Plot
p = ui.plot
p.setRange(xRange=[0, 225], yRange=[0,150])

# Establish connection with Arduino
try:
    ser = createUSBPort( "Arduino", 39, 115200 )
    if ser.is_open == False:
        ser.open()
    print( "Serial Port OPEN" )

except Exception as e:
    print( "Could NOT open serial port" )
    print( "Error type %s" %str(type(e)) )
    print( " Error Arguments " + str(e.args) )
    sleep( 5 )
    quit()

# Setup queues for data communication
Q_getData   = Queue( maxsize=0 )    #Pooled data from arduino
Q_stuff     = Queue( maxsize=0 )    #

sleep( 2.5 )      # Delay for stability

# Retrieve data
t_getData = Thread( target=getData, args=( Q_getData, ) )
t_getData.start()

# Update plot
t_queueBuffers = Thread( target=queueBuffers, args=( Q_getData, Q_stuff,) )
t_queueBuffers.start()

# Plot data
while Q_stuff.qsize() == 0:
    doStuff = True

# Fetch data from stack
if Q_stuff.qsize() > 0:
    #print ("Got stuff")
    sleep( 2.5 )            # For stability
    data = Q_stuff.get()
    
# Call for update
timer = QtCore.QTimer()
timer.timeout.connect( update )
timer.start(0)

######################################################
#                   START PROGRAM
######################################################

## Start Qt event loop.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()




        
