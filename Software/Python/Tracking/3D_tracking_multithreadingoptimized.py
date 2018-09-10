'''
* This version has been reduced to support the Finexus setup, in an attempt to replicate their reported accurate Z positioning.
*
* Position tracking of magnet based on Finexus
* https://ubicomplab.cs.washington.edu/pdfs/finexus.pdf
*
* VERSION: 0.2.2.c
*   - MODIFIED: 4 sensors in operation.
*
*
* AUTHOR  :   Edward Nichols
* DATE    :   Oct. 18th, 2017 Year of Our Lord
* 
* AUTHOR  :   Mohammad Odeh 
* DATE    :   Oct. 17th, 2017 Year of Our Lord
*
'''

# Import Modules
import  numpy               as      np                      # Import Numpy
import  matplotlib.pyplot   as      plt                     # Plot data
import  Queue               as      qu                      # Queue for multithreading sync
import  argparse                                            # Feed in arguments to the program
import  os, platform                                        # To open and write to a file
from    threading           import  Thread                  # Multithreading
from    time                import  sleep, time, clock      # Sleep for stability
from    scipy.optimize      import  root                    # Solve System of Eqns for (x, y, z)
from    scipy.linalg        import  norm                    # Calculate vector norms (magnitude)
from    usbProtocol         import  createUSBPort           # Create USB port (serial comm. w\ Arduino)


# ************************************************************************
# =====================> CONSTRUCT ARGUMENT PARSER <=====================*
# ************************************************************************
ap = argparse.ArgumentParser()

ap.add_argument("-d", "--debug", action='store_true',
                help="invoke flag to enable debugging")
ap.add_argument("-vp", "--visualize-position", action='store_true',
                help="invoke flag to visualize position")
ap.add_argument("-plt", "--plot", action='store_true',
                help="invoke flag to visualize position")

args = vars( ap.parse_args() )

args["debug"]   = False
args["plot"]    = False
args["visualize-position"] = True

# ************************************************************************
# =====================> DEFINE NECESSARY FUNCTIONS <====================*
# ************************************************************************

# ****************************************************
# Define function to sort from lowest->highest value *
# -------------------------------------------------- *
# INPUT :   - A list                                 *
# OUTPUT:   - A list containing the indices of the   *
#             given list's elements arranged from    *
#             the index of the element with the      *
#             smallest value to the index of the     *
#             element with the largest value         *
# ****************************************************
def argsort(seq):
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key=seq.__getitem__)

# ****************************************************
# Sort a list's elements from smallest to largest    *
# -------------------------------------------------- *
# INPUT :   - List to be sorted                      *
#           - Number of elements in said list that   *
#               you want to sort                     *
# OUTPUT:   - A sorted list of size (N)              *
# ****************************************************
def bubbleSort(arr, N):
    data = []
    for i in range(0, N):
        data.append( arr[i] )

    for i in range(0, len(data)):
        for j in range(0, len(data)-i-1):
            if (data[j] > data[j+1]):
                temp = data[j]
                data[j] = data[j+1]
                data[j+1] = temp
            else:
                continue
    return (data)

# ****************************************************
# Define function to pool & return data from Arduino *
# ****************************************************
def getData(ser, Q_getData):
    global CALIBRATING

##Synchronization issues are evident. May need to look into parallelizations, or threading. 
##    samplerate = 0.015
##    sleep(samplerate)
    
    while (True):
        try:
            # Flush buffer
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            
            # Read incoming data and seperate
            line    = ser.readline()[:-1]
            col     = line.split(", ")

            # Wait for the sensor to calibrate itself to ambient fields.
            while( not( len(col) == 18 ) ):
                line    = ser.readline()[:-1]
                col     = line.split(", ")

                if(CALIBRATING == True):
                    print( "Calibrating...\n" )
                    CALIBRATING = False

            # Construct magnetic field array
            else:
                # Sensor 1
                Bx = float(col[0])
                By = float(col[1])
                Bz = float(col[2])
                B1 = np.array( ([Bx],[By],[Bz]), dtype='float64') # Units { G }

                # Sensor 2
                Bx = float(col[3])
                By = float(col[4])
                Bz = float(col[5])
                B2 = np.array( ([Bx],[By],[Bz]), dtype='float64') # Units { G }

                # Sensor 3
                Bx = float(col[6])
                By = float(col[7])
                Bz = float(col[8])
                B3 = np.array( ([Bx],[By],[Bz]), dtype='float64') # Units { G }

                # Sensor 4
                Bx = float(col[9] )
                By = float(col[10])
                Bz = float(col[11])
                B4 = np.array( ([Bx],[By],[Bz]), dtype='float64') # Units { G }

                # Sensor 5
                Bx = float(col[12])
                By = float(col[13])
                Bz = float(col[14])
                B5 = np.array( ([Bx],[By],[Bz]), dtype='float64') # Units { G }

                # Sensor 6
                Bx = float(col[15])
                By = float(col[16])
                Bz = float(col[17])
                B6 = np.array( ([Bx],[By],[Bz]), dtype='float64') # Units { G }


            # Put the data in the Queue, no matter what. "Pipelining".
                Q_getData.put( (B1, B2, B3, B4, B5, B6) )

        except Exception as e:
            print( "Caught error in getData()"      )
            print( "Error type %s" %str(type(e))    )
            print( "Error Arguments " + str(e.args) )

# ****************************************************
# Define function to construct equations to solve for
# ****************************************************
def LHS( root, K, norms ):
    global PRINT
    
    # Extract x, y, and z
    x, y, z = root
    
    # Construct the (r) terms for each sensor
    # NOTE: Relative distance terms are in meters
    #     : Standing on sensor(n), how many units in
    #       the x/y/z direction should I march to get
    #       back to sensor1 (origin)?
    r1 = float( ( (x+0.000)**2. + (y+0.050)**2. + (z-0.100)**2. )**(1/2.) )  # Sensor 1
    r2 = float( ( (x+0.000)**2. + (y-0.075)**2. + (z-0.100)**2. )**(1/2.) )  # Sensor 2
    r3 = float( ( (x+0.000)**2. + (y+0.050)**2. + (z+0.100)**2. )**(1/2.) )  # Sensor 3 
    r4 = float( ( (x+0.000)**2. + (y-0.075)**2. + (z+0.100)**2. )**(1/2.) )  # Sensor 4
    r5 = float( ( (x+0.000)**2. + (y+0.000)**2. + (z+0.000)**2. )**(1/2.) )  # Sensor 5 (Origin)
    r6 = float( ( (x+0.062)**2. + (y+0.000)**2. + (z+0.000)**2. )**(1/2.) )  # Sensor 6 (Had to measure it with a caliper! The Standoff is meant to be on the ground, not on another sensor!)

    # Construct the equations
    Eqn1 = ( K*( r1 )**(-6.) * ( 3.*( z/r1 )**2. + 1 ) ) - norms[0]**2.     # Sensor 1
    Eqn2 = ( K*( r2 )**(-6.) * ( 3.*( z/r2 )**2. + 1 ) ) - norms[1]**2.     # Sensor 2
    Eqn3 = ( K*( r3 )**(-6.) * ( 3.*( z/r3 )**2. + 1 ) ) - norms[2]**2.     # Sensor 3
    Eqn4 = ( K*( r4 )**(-6.) * ( 3.*( z/r4 )**2. + 1 ) ) - norms[3]**2.     # Sensor 4
    Eqn5 = ( K*( r5 )**(-6.) * ( 3.*( z/r5 )**2. + 1 ) ) - norms[4]**2.     # Sensor 5
    Eqn6 = ( K*( r6 )**(-6.) * ( 3.*( z/r6 )**2. + 1 ) ) - norms[5]**2.     # Sensor 6

    # Construct a vector of the equations
    Eqns = [Eqn1, Eqn2, Eqn3, Eqn4, Eqn5, Eqn6]

    # Determine which sensors to use based on magnetic field value (smallValue==noBueno!)
    sort = argsort(norms)               # Auxiliary function sorts norms from smallest to largest, by index.
    sort.reverse()                      # Python built-in function reverses elements of list.
    f=[]                                # Declare vector to hold relevant functions.

    for i in range(0, 3):               # Fill functions' array with the equations that correspond to
        f.append(Eqns[sort[i]])         # the sensors with the highest norm, thus closest to magnet
        
    # Return vector
    return ( f )

# ****************************************************
# Determine initial guess based on magnitude of      *
# magnetic field relative to all the sensors         *
# ****************************************************
def findIG(magFields):
    # Define IMU positions on the grid
    #      / sensor 1: (x, y, z)
    #     /  sensor 2: (x, y, z)
    # Mat=      :          :
    #     \     :          :
    #      \ sensor 6: (x, y, z)
    IMU_pos = np.array(((0.000  ,  -0.050  ,  0.100) ,
                        (0.000  ,   0.075  ,  0.100) ,
                        (0.000  ,  -0.050  ,  0.100) ,
                        (0.000  ,   0.075  ,  0.100) ,
                        (0.000  ,   0.000  ,  0.000) ,
                        (0.062  ,   0.000  ,  0.000)), dtype='float64')

    # Read current magnetic field from MCU
    (H1, H2, H3, H4, H5, H6) = magFields

    # Compute L2 vector norms
    HNorm = [ float(norm(H1)), float(norm(H2)),
              float(norm(H3)), float(norm(H4)),
              float(norm(H5)), float(norm(H6)) ]
    
    # Determine which sensors to use based on magnetic field value (smallValue==noBueno!)
    sort = argsort(HNorm)               # Auxiliary function sorts norms from smallest to largest
    sort.reverse()                      # Python built-in function reverses elements of list

    IMUS = bubbleSort(sort, 3)

    # Return the initial guess as the centroid of the detected triangle
    return ( np.array(((IMU_pos[IMUS[0]][0]+IMU_pos[IMUS[1]][0]+IMU_pos[IMUS[2]][0])/3.,
                       (IMU_pos[IMUS[0]][1]+IMU_pos[IMUS[1]][1]+IMU_pos[IMUS[2]][1])/3.,
                       (IMU_pos[IMUS[0]][2]+IMU_pos[IMUS[1]][2]+IMU_pos[IMUS[2]][2])/3. ), dtype='float64') )

# ************************************************************************
# ===========================> SETUP PROGRAM <===========================
# ************************************************************************

# Useful variables
global CALIBRATING

CALIBRATING = True                              # Boolean to indicate that device is calibrating
READY       = False                             # Give time for user to place magnet

##This measurement was redone to reflect the changes on the imposed C.S. for LMA
K           = 4.24e-7             # Magnet's constant (K) || Units { G^2.m^6}
#K           = 1.09e-6 
dx          = 1e-7                # Differential step size (Needed for solver)
calcPos     = []                  # Empty array to hold calculated positions

# Create a queue for retrieving data from the thread.
Q_getData = qu.Queue( maxsize=0 )

# Establish connection with Arduino
DEVC = "Arduino"                                # Device Name (not very important)
PORT = 6                                        # Port number (VERY important)
BAUD = 115200                                   # Baudrate    (VERY VERY important)

# Error handling in case serial communcation fails (1/2).
try:
    IMU = createUSBPort( DEVC, PORT, BAUD )     # Create serial connection
    if IMU.is_open == False:                    # Make sure port is open
        IMU.open()
    print( "Serial Port OPEN" )

    # Determine initial guess based on magnet's location.
    initialGuess = np.array( (0.005, 0.050, -0.050), dtype='float64')

# Error handling in case serial communcation fails (2/2).
except Exception as e:
    print( "Could NOT open serial port" )
    print( "Error type %s" %str(type(e)) )
    print( "Error Arguments " + str(e.args) )
    sleep( 2.5 )
    quit()                                      # Shutdown entire program

# Start the thread to pool data from the serial port.
t_getData = Thread ( target=getData, args=(IMU, Q_getData, ) )
t_getData.daemon = True
t_getData.start()


# ************************************************************************
# =========================> MAKE IT ALL HAPPEN <=========================
# ************************************************************************

# Start iteration
while( True ):
    try:
        # Pull data from queue.
        if ( Q_getData.qsize() > 0 ):
            # Inform user that system is almost ready
            if(READY == False):
                print( "Place the magnet in the range!");
                print( "Ready in 3" )
                sleep( 1.0 )
                print( "Ready in 2" )
                sleep( 1.0 )
                print( "Ready in 1" )
                sleep( 1.0 )
                print( "GO!" )
                # Set the device to ready!!
                READY = True

            startTime=clock()
            #Wait until there's something in the queue.
            (H1, H2, H3, H4, H5, H6) = Q_getData.get( True )

            # Compute L2 vector norms
            HNorm = [ float(norm(H1)), float(norm(H2)),
                      float(norm(H3)), float(norm(H4)),
                      float(norm(H5)), float(norm(H6)) ]

        ##QUESTION FOR MOE:
        ##If everything is being sorted, and reduced to the data of 3 sensors,
        ##why don't you do that here when passing LMA arg=HNorm?

            # Invoke solver (using Levenberg-Marquardt)
            sol = root(LHS, initialGuess, args=(K, HNorm), method='lm',
                       options={'ftol':1e-10, 'xtol':1e-10, 'maxiter':1000,
                                'eps':1e-8, 'factor':0.001})

            # Print solution (coordinates) to screen
            print( "Current position (x , y , z):" )
            ## The Coordinate System for within the LMA algorithm is aligned with the magnet's North pole, s.t. X -> North
            ## We want the displayed output to reflect a more convenient C.S., so we impose a further mapping on print:
            ## X is given by LMA's -Z or -1 * sol.x[2]
            ## Y is given by LMA's  Y or sol.x[1]
            ## Z is given by LMA's  X or sol.x[0]
            pos = [-1*sol.x[2]*1000, sol.x[1]*1000, sol.x[0]*1000]
            print( "(%.5f , %.5f , %.5f)mm" %(pos[0], pos[1], pos[2]) )
            print( "t= %.5f" %(clock()-startTime) )

            # Check if solution makes sense
            if (abs(sol.x[0]*1000) > 250) or (abs(sol.x[1]*1000) > 250) or (abs(sol.x[2]*1000) > 250):
                #print( "Invalid solution. Resetting Calculations" )
                # Determine initial guess based on magnet's location.
                initialGuess = findIG( Q_getData.get() )  
            # Update initial guess with current position and feed back to solver
            else:    
                initialGuess = np.array( (sol.x[0]+dx, sol.x[1]+dx, sol.x[2]+dx), dtype='float64' )
                calcPos.append(pos)
            
        # Save data on EXIT (Ctrl-C)
    except KeyboardInterrupt: 
        if platform.system()=='Windows':

            # Define useful paths
            homeDir = os.getcwd()
            dst     = homeDir + '\\output'
            dataFile= dst + '\\data.txt'

        # Check if directory exists
        if ( os.path.exists(dst)==False ):
            # Create said directory
            os.makedirs(dst)

        for i in range( 0, len(calcPos) ):
                with open(dataFile, "a") as f:
                    f.write(str(calcPos[i][0]) + "," + str(calcPos[i][1]) + "," + str(calcPos[i][2]) + "\n")
        break
