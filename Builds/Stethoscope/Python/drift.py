'''
* NOTE: the current method as it stands has a limitation in which
*       the magnet has to be placed at a predefined initial position
*       for the solver to successfully converge (find x, y, and z)
*
* Calculate drift percentage. This is later used to determine
* which sensor to trigger at certain magnetic field values.
*
* VERSION: 0.0.1
*   - First working version.
*   - FIXED: Resolved buffer issue by switching from Arduino to Teensy
*     for the data acquisition and communications.
*   - FIXED: Added a check to verify that solutions (distances) make
*     physical sense. If check fails, the code readjusts calculations.
*
* KNOWN ISSUES:
*   - Small grid size
*   - Calculations are accurate to around +/-3mm
*
* AUTHOR  :   Mohammad Odeh
* DATE    :   Sep. 25th, 2017 Year of Our Lord
*
'''

# Import Modules
import  numpy               as      np              # Import Numpy
from    time                import  sleep           # Sleep for stability
from    scipy.linalg        import  norm            # Calculate vector norms (magnitude)
from    usbProtocol         import  createUSBPort   # Create USB port (serial comm. w\ Arduino)
import  argparse                                    # Feed in arguments to the program

# ************************************************************************
# =====================> CONSTRUCT ARGUMENT PARSER <=====================
# ************************************************************************
ap = argparse.ArgumentParser()

ap.add_argument("-d", "--debug", action='store_true',
                help="invoke flag to enable debugging")

args = vars( ap.parse_args() )

#args["debug"] = False

# ************************************************************************
# =====================> DEFINE NECESSARY FUNCTIONS <=====================
# ************************************************************************

# ****************************************************
# Define function to pool & return data from Arduino
# ****************************************************
def getData(ser):
    global CALIBRATING

    # Flush buffer
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    # Allow data to fill-in buffer
    sleep(0.1)

    try:
        # Read incoming data and seperate
        line = ser.readline()[:-1]
        col = line.split(",")

        # Wait for the sensor to calibrate itself to ambient fields.
        while( len(col) < 12 ):
            line = ser.readline()[:-1]
            col = line.split(",")
            if(CALIBRATING == True):
                print( "Calibrating...\n" )
                CALIBRATING = False

        # Construct magnetic field array
        else:
            # Sensor 1
            Bx=float(col[0])
            By=float(col[1])
            Bz=float(col[2])
            B1 = np.array( ([Bx],[By],[Bz]), dtype='float64') # Units { G }

            # Sensor 2
            Bx=float(col[3])
            By=float(col[4])
            Bz=float(col[5])
            B2 = np.array( ([Bx],[By],[Bz]), dtype='float64') # Units { G }

            # Sensor 3
            Bx=float(col[6])
            By=float(col[7])
            Bz=float(col[8])
            B3 = np.array( ([Bx],[By],[Bz]), dtype='float64') # Units { G }

            # Sensor 4
            Bx=float(col[9] )
            By=float(col[10])
            Bz=float(col[11])
            B4 = np.array( ([Bx],[By],[Bz]), dtype='float64') # Units { G }
            
            # Return vectors
            return (B1, B2, B3, B4)

    except Exception as e:
        print( "Caught error in getData()"      )
        print( "Error type %s" %str(type(e))    )
        print( "Error Arguments " + str(e.args) )

# ************************************************************************
# ===========================> SETUP PROGRAM <===========================
# ************************************************************************

# Useful variables
global CALIBRATING

CALIBRATING = True                              # Boolean to indicate that device is calibrating
READY       = False                             # Give time for user to palce magnet

# Establish connection with Arduino
DEVC = "Arduino"
PORT = 29
BAUD = 115200
try:
    IMU = createUSBPort( DEVC, PORT, BAUD )
    if IMU.is_open == False:
        IMU.open()
    print( "Serial Port OPEN" )

except Exception as e:
    print( "Could NOT open serial port" )
    print( "Error type %s" %str(type(e)) )
    print( "Error Arguments " + str(e.args) )
    sleep( 5 )
    quit()


# ************************************************************************
# =========================> MAKE IT ALL HAPPEN <=========================
# ************************************************************************

# Start iteration
while( True ):
    # Pool data from Arduino
    (H1, H2, H3, H4) = getData(IMU)

    # Inform user that system is almost ready
    if(READY == False):
        # Store initial baseline readings
        initB1 = H1
        initB2 = H2
        initB3 = H3
        initB4 = H4
        
        # Set the device to ready!!
        READY = True
        
    # Compute L2 vector norms
    HNorm = [float(norm(H1)), float(norm(H2)), float(norm(H3)), float(norm(H4))]

    # Print solution (coordinates) to screen
    print( "    Sensor 1        Sensor 2        Sensor 3        Sensor 4" )
    print( "   ==========      ==========      ==========      ==========" )
    print( ">>> BASELINE:" )
    print( "x:  %8.5f       %9.5f       %9.5f       %9.5f" %(initB1[0], initB2[0], initB3[0], initB4[0]) )
    print( "y:  %8.5f       %9.5f       %9.5f       %9.5f" %(initB1[1], initB2[1], initB3[1], initB4[1]) )
    print( "z:  %8.5f       %9.5f       %9.5f       %9.5f" %(initB1[2], initB2[2], initB3[2], initB4[2]) )
    print( '' )
    
    print( ">>> CURRENT :" )
    print( "x:  %8.5f       %9.5f       %9.5f       %9.5f" %(H1[0], H2[0], H3[0], H4[0]) )
    print( "y:  %8.5f       %9.5f       %9.5f       %9.5f" %(H1[1], H2[1], H3[1], H4[1]) )
    print( "z:  %8.5f       %9.5f       %9.5f       %9.5f" %(H1[2], H2[2], H3[2], H4[2]) )
    print( "\n\n" )


    # Sleep for stability
    sleep( 2.5 )

# ************************************************************************
# =============================> DEPRECATED <=============================
# ************************************************************************
#
