'''
*
* Position tracking of magnet based on Finexus
* https://ubicomplab.cs.washington.edu/pdfs/finexus.pdf
*
* VERSION: 0.2
*   - 2 Modes of operations
*       (1) Continuous sampling
*       (2) Guided Point-by-Point
*   - Plot stuff
*   - Standoffs, raising three of the sensors to .1m
*
* KNOWN ISSUES:
*   - Z-axis still sucks.
*   - Refresh Rate is 3 to 4 Hz. [REALLY REALLY REALLY LOW; Target for "Real-Time" is 30Hz]
*   - 
*
* AUTHOR                    :   Edward Nichols
* LAST CONTRIBUTION DATE    :   Oct. 17th, 2017 Year of Our Lord
* 
* AUTHOR                    :   Mohammad Odeh 
* LAST CONTRIBUTION DATE    :   Oct. 17th, 2017 Year of Our Lord
*
'''

# Import Modules
import  numpy               as      np              # Import Numpy
import  RPi.GPIO            as      GPIO            # Use GPIO pins
import  matplotlib.pyplot   as      plt             # Plot data
from    time                import  sleep, clock    # Sleep for stability, clock for profiling
from    scipy.optimize      import  root            # Solve System of Eqns for (x, y, z)
from    scipy.linalg        import  norm            # Calculate vector norms (magnitude)
from    ctypes              import  *               # Import ctypes (VERY IMPORTANT)
import  os, platform                                # Directory/file manipulation

# ************************************************************************
# =====================> LOAD CTYPES AND SETUP MUX <=====================*
# ************************************************************************
NPINS = 3
NSENS = 6

# Setup IMU settings
path = "/home/pi/LSM9DS1_RaspberryPi_Library/lib/liblsm9ds1cwrapper.so"
lib = cdll.LoadLibrary(path)

lib.lsm9ds1_create.argtypes = []
lib.lsm9ds1_create.restype = c_void_p

lib.lsm9ds1_begin.argtypes = [c_void_p]
lib.lsm9ds1_begin.restype = None

lib.lsm9ds1_calibrate.argtypes = [c_void_p]
lib.lsm9ds1_calibrate.restype = None

lib.lsm9ds1_magAvailable.argtypes = [c_void_p]
lib.lsm9ds1_magAvailable.restype = c_int

lib.lsm9ds1_readMag.argtypes = [c_void_p]
lib.lsm9ds1_readMag.restype = c_int

lib.lsm9ds1_getMagX.argtypes = [c_void_p]
lib.lsm9ds1_getMagX.restype = c_float
lib.lsm9ds1_getMagY.argtypes = [c_void_p]
lib.lsm9ds1_getMagY.restype = c_float
lib.lsm9ds1_getMagZ.argtypes = [c_void_p]
lib.lsm9ds1_getMagZ.restype = c_float

lib.lsm9ds1_calcMag.argtypes = [c_void_p, c_float]
lib.lsm9ds1_calcMag.restype = c_float

# Setup multiplexer
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(25, GPIO.OUT)


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
# Define function to calculate corrected magnt field *
# ****************************************************
def calcMag( imu, IMU_Base ):

    B = np.array(((0.0, 0.0, 0.0) ,
                  (0.0, 0.0, 0.0) ,
                  (0.0, 0.0, 0.0) ,
                  (0.0, 0.0, 0.0) ,
                  (0.0, 0.0, 0.0) ,
                  (0.0, 0.0, 0.0)), dtype='float64')
    
    # Loop over sensors and construct magnetic field
    for i in range(0, NSENS):
        setSensor( i )
        while lib.lsm9ds1_magAvailable(imu) == 0:
            pass
        lib.lsm9ds1_readMag(imu)

        cmx = lib.lsm9ds1_calcMag(imu, lib.lsm9ds1_getMagX(imu))
        cmy = lib.lsm9ds1_calcMag(imu, lib.lsm9ds1_getMagY(imu))
        cmz = lib.lsm9ds1_calcMag(imu, lib.lsm9ds1_getMagZ(imu))

        #
        # Construct magnetic field array
        #
        B[i][0] = float(cmx - IMU_Base[i][0])   #
        B[i][1] = float(cmy - IMU_Base[i][1])   # Units { G }
        B[i][2] = float(cmz - IMU_Base[i][2])   #
    
    # Return matrix
    return ( B ) 

# ****************************************************
# Define function to construct equations to solve for
# ****************************************************
def LHS( root, K, norms ):
 
    # Extract x, y, and z
    x, y, z = root
    
    # Construct the (r) terms for each sensor
    # NOTE: Relative distance terms are in meters
    #     : Standing on sensor(n), how many units in
    #       the x/y/z direction should I march to get
    #       back to sensor1 (origin)?
    r1 = float( ( (x+0.000)**2. + (y-0.125)**2. + (z-0.000)**2. )**(1/2.) )  # Sensor 1
    r2 = float( ( (x-0.100)**2. + (y-0.175)**2. + (z-0.000)**2. )**(1/2.) )  # Sensor 2
    r3 = float( ( (x-0.200)**2. + (y-0.125)**2. + (z-0.000)**2. )**(1/2.) )  # Sensor 3
    r4 = float( ( (x+0.000)**2. + (y+0.000)**2. + (z-0.000)**2. )**(1/2.) )  # Sensor 4 (ORIGIN)
    r5 = float( ( (x-0.100)**2. + (y+0.050)**2. + (z-0.000)**2. )**(1/2.) )  # Sensor 5
    r6 = float( ( (x-0.200)**2. + (y-0.000)**2. + (z-0.000)**2. )**(1/2.) )  # Sensor 6

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
    sort = argsort(norms)               # Auxiliary function sorts norms from smallest to largest
    sort.reverse()                      # Python built-in function reverses elements of list
    f=[]                                # Declare vector to hold relevant functions

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
    IMU_pos = np.array(((0.0  , 0.125,   0.0) ,
                        (0.100, 0.175,   0.0) ,
                        (0.200, 0.125,   0.0) ,
                        (0.0  , 0.0  ,   0.0) ,
                        (0.100,-0.050,   0.0) ,
                        (0.200, 0.0  ,   0.0)), dtype='float64')

    # Read current magnetic field from MCU
    H = magFields

    # Compute L2 vector norms
    HNorm = [ float(norm(H[0])), float(norm(H[1])),
              float(norm(H[2])), float(norm(H[3])),
              float(norm(H[4])), float(norm(H[5])) ]
    
    # Determine which sensors to use based on magnetic field value (smallValue==noBueno!)
    sort = argsort(HNorm)               # Auxiliary function sorts norms from smallest to largest
    sort.reverse()                      # Python built-in function reverses elements of list

    IMUS = bubbleSort(sort, 3)

    # Return the initial guess as the centroid of the detected triangle
    return ( np.array(((IMU_pos[IMUS[0]][0]+IMU_pos[IMUS[1]][0]+IMU_pos[IMUS[2]][0])/3.,
                       (IMU_pos[IMUS[0]][1]+IMU_pos[IMUS[1]][1]+IMU_pos[IMUS[2]][1])/3.,
                       (IMU_pos[IMUS[0]][2]+IMU_pos[IMUS[1]][2]+IMU_pos[IMUS[2]][2])/3. -0.01), dtype='float64') )

# Switch between the multiplexer channels (sensors)
# =========================    Set Sensor      ========================
# Set the value on the multiplexer to set the sensor to use
def setSensor( sensorIndex ):
    # Sensor 1, 000
    if ( sensorIndex == 0 ):
        GPIO.output(23, GPIO.LOW)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.LOW)

    # Sensor 2, 001
    elif ( sensorIndex == 1 ):
        GPIO.output(23, GPIO.HIGH)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.LOW)

    # Sensor 3, 010
    elif ( sensorIndex == 2 ):
        GPIO.output(23, GPIO.LOW)
        GPIO.output(24, GPIO.HIGH)
        GPIO.output(25, GPIO.LOW)

    # Sensor 4, 011
    elif ( sensorIndex == 3):
        GPIO.output(23, GPIO.HIGH)
        GPIO.output(24, GPIO.HIGH)
        GPIO.output(25, GPIO.LOW)

    # Sensor 5, 100
    elif ( sensorIndex == 4):
        GPIO.output(23, GPIO.LOW)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.HIGH)

    # Sensor 6, 101
    elif (sensorIndex == 5):
        GPIO.output(23, GPIO.HIGH)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.HIGH)

    else:
        print("Invalid Index")

# ****************************************************
#           Plot actual vs measured position         *
# ****************************************************
def plotPos(actual, calculated):
     
    data = (actual, calculated)
     
    # Create plot
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, facecolor="1.0")


    # major ticks every 5, minor ticks every 1                                      
    major_ticks = np.arange(20, 116, 5)                                              
    minor_ticks = np.arange(20 ,116, 1)                                               

    ax.set_xticks(major_ticks)                                                       
    ax.set_xticks(minor_ticks, minor=True)                                           
    ax.set_yticks(major_ticks)                                                       
    ax.set_yticks(minor_ticks, minor=True)

    # Set xy-axes scale + labels
    ax.set_xlim([30, 115])
    ax.set_ylim([20, 105])
    ax.set_xlabel('Distance (mm)')
    ax.set_ylabel('Distance (mm)')

    # Add a grid                                                       
    ax.grid(which='both')                                                            

    # Modify transperancy settings for the grids:                               
    ax.grid(which='minor', alpha=0.2)                                                
    ax.grid(which='major', alpha=0.5)

    # Extract data
    x_actual = []
    y_actual = []
    x_calc = []
    y_calc = []
    for i in range(0,len(actual)):
        x_actual.append(actual[i][0])
        y_actual.append(actual[i][1])
        x_calc.append(calculated[i][0])
        y_calc.append(calculated[i][1])
    ax.scatter(x_actual, y_actual, alpha=0.8, color='r', s=30, label="Actual")
    ax.scatter(x_calc, y_calc, alpha=0.8, color='g', s=30, label="Calculated")

    # Annotate data points
    for i, j, k, l in zip(x_calc, y_calc, x_actual, y_actual):
        ax.annotate('($\Delta x=%.2f, \Delta y=%.2f$)'%(abs(i-k),abs(j-l)), xy=(i, j+0.5))
    
    plt.title('Actual vs Calculated Position')
    plt.legend(loc=2)
    plt.show()

# ************************************************************************
# ===========================> SETUP PROGRAM <===========================
# ************************************************************************

# Useful variables
READY       = False                             # Give time to user
K           = 1.09e-6                           # Magnet's constant (K) || Units { G^2.m^6}
dx          = 1e-7                              # Differential step size (Needed for solver)
calcPos     = []                                # Empty array to hold calculated positions

initialGuess= np.array((0.10, 0.01, -0.01), 
                        dtype='float64' )       # Initial position/guess

# Averaged base readings (to be subtracted from subsequent RAW readings)
IMU_Base = np.array(((0.0, 0.0, 0.0) ,
                     (0.0, 0.0, 0.0) ,
                     (0.0, 0.0, 0.0) ,
                     (0.0, 0.0, 0.0) ,
                     (0.0, 0.0, 0.0) ,
                     (0.0, 0.0, 0.0)), dtype='float64')

# Initialize all sensors
for i in range(0, 6):
    setSensor( i )                          # Select the IMU
    imu = lib.lsm9ds1_create()              # Create an instance
    lib.lsm9ds1_begin(imu)                  # Initialize it

    if lib.lsm9ds1_begin(imu) == 0:         # In case it fails
        print("Failed to communicate with LSM9DS1.")
        quit()

    else:                                   # In case it doesn't, configure
        CALIBRATION_INDEX = 50              # Average over this many readings
        lib.lsm9ds1_setMagScale(imu, 16)    # Set scale to +/-16Gauss
        lib.lsm9ds1_calibrateMag(imu)       # Call built-in calibration routine

        cmx, cmy, cmz = 0, 0, 0

        # Perform user-built calibration to further clear noise
        for j in range(0, CALIBRATION_INDEX):
            lib.lsm9ds1_readMag(imu)

            cmx += lib.lsm9ds1_calcMag(imu, lib.lsm9ds1_getMagX(imu))
            cmy += lib.lsm9ds1_calcMag(imu, lib.lsm9ds1_getMagY(imu))
            cmz += lib.lsm9ds1_calcMag(imu, lib.lsm9ds1_getMagZ(imu))

        IMU_Base[i][0] = cmx/CALIBRATION_INDEX
        IMU_Base[i][1] = cmy/CALIBRATION_INDEX
        IMU_Base[i][2] = cmz/CALIBRATION_INDEX
        print( "Correction constant for sensor %d is:" %(i+1) )
        print( "x: %.5f, y: %.5f, z: %.5f\n" %(IMU_Base[i][0], IMU_Base[i][1], IMU_Base[i][2]) )
        
# ************************************************************************
# =========================> MAKE IT ALL HAPPEN <=========================
# ************************************************************************

# Choose mode of operation
print( "Choose plotting mode:" )
print( "1. Continuous." )
print( "2. Point-by-Point." )
mode = raw_input(">\ ")

# If continuous mode was selected:
if ( mode == '1' ):
    print( "\n******************************************" )
    print( "*NOTE: Press Ctrl-C to save data and exit." )
    print( "******************************************\n" )
    while ( True ):
        try:
            # Inform user that system is almost ready
            if(READY == False):
                print( "Place magnet on track" )
                sleep( 2.5 )
                print( "Ready in 3" )
                sleep( 1.0 )
                print( "Ready in 2" )
                sleep( 1.0 )
                print( "Ready in 1" )
                sleep( 1.0 )
                print( "GO!" )
                start = clock()

                # Set the device to ready!!
                READY = True

            # Get magnetic field readings
            H = calcMag( imu, IMU_Base )    # Returns data as a matrix

                
            # Compute L2 vector norms
            HNorm = [ float(norm(H[0])), float(norm(H[1])),
                      float(norm(H[2])), float(norm(H[3])),
                      float(norm(H[4])), float(norm(H[5])) ]

            ### QUESTION FOR MOE:
            #Why do you sort HNorm everywhere but here when you pass it to LMA?
            
            # Invoke solver (using Levenberg-Marquardt)
            sol = root(LHS, initialGuess, args=(K, HNorm), method='lm',
                       options={'ftol':1e-10, 'xtol':1e-10, 'maxiter':1000,
                                'eps':1e-8, 'factor':0.001})

            # Print solution (coordinates) to screen
            pos = [sol.x[0]*1000, sol.x[1]*1000, sol.x[2]*1000, float(clock())]
            #print( "(x, y, z): (%.3f, %.3f, %.3f) Time: %.3f" %(pos[0], pos[1], pos[2], pos[3]) )
            

            # Check if solution makes sense
            if (abs(sol.x[0]*1000) > 500) or (abs(sol.x[1]*1000) > 500) or (abs(sol.x[2]*1000) > 500):
                # Determine initial guess based on magnet's location
                #print("NOT STORED\n\n")
                initialGuess = findIG( calcMag(imu, IMU_Base) )
                
            # Update initial guess with current position and feed back to solver
            else:
                calcPos.append(pos)
                initialGuess = np.array( (sol.x[0]+dx, sol.x[1]+dx, sol.x[2]+dx), dtype='float64' )
                #print("STORED\n\n")

        # Save data on EXIT
        except KeyboardInterrupt:
            if platform.system()=='Linux':

                # Define useful paths
                homeDir = os.getcwd()
                dst     = homeDir + '/output'
                dataFile= dst + '/data1.txt'

            # Check if directory exists
            if ( os.path.exists(dst)==False ):
                # Create said directory
                os.makedirs(dst)

            for i in range( 0, len(calcPos) ):
                    with open(dataFile, "a") as f:
                        f.write(str(calcPos[i][0]) + "," + str(calcPos[i][1]) + "," + str(calcPos[i][2]) + "," + str(calcPos[i][3]) + "\n")
            break

# --------------------------------------------------------------------------------------

# Else if point-by-point mode was selected:
elif ( mode == '2' ):
    actualPos = [ [50 ,  25],   # Array of points on grid to plot against
                  [50 ,  50],
                  [50 ,  75],
                  [50 , 100],
                  [75 ,  25],
                  [75 ,  50],
                  [75 ,  75],
                  [75 , 100],
                  [100,  25],
                  [100,  50],
                  [100,  75],
                  [100, 100] ]
    i=0
    while (i is not(len(actualPos))):
        
        print( "Place magnet at " + str(actualPos[i]) + "mm" )
        sleep( 1.5 )

        var = raw_input("Ready? (Y/N): ")

        if (var=='y' or var=='Y'):
            print( "Collecting data!" )

            # Pool data from Arduino
            (H1, H2, H3, H4, H5, H6) = getData(IMU)
            (H1, H2, H3, H4, H5, H6) = getData(IMU)
            initialGuess = findIG(getData(IMU))
            
            # Compute L2 vector norms
            HNorm = [ float(norm(H1)), float(norm(H2)),
                      float(norm(H3)), float(norm(H4)),
                      float(norm(H5)), float(norm(H6)) ]
            
            # Invoke solver (using Levenberg-Marquardt)
            sol = root(LHS, initialGuess, args=(K, HNorm), method='lm',
                       options={'ftol':1e-10, 'xtol':1e-10, 'maxiter':1000,
                                'eps':1e-8, 'factor':0.001})

            # Print solution (coordinates) to screen
            pos = [sol.x[0]*1000, sol.x[1]*1000]
            #print( "Calc: %.3f, %.3f" %(pos[0], pos[1]) )
            
            # Sleep for stability
            sleep( 0.1 )

            # Check if solution makes sense
            if (abs(sol.x[0]*1000) > 500) or (abs(sol.x[1]*1000) > 500) or (abs(sol.x[2]*1000) > 500):
                # Determine initial guess based on magnet's location
                print("NOT STORED\n\n")
                initialGuess = findIG(getData(IMU))
                
            # Update initial guess with current position and feed back to solver
            else:
                calcPos.append(pos)
                i=i+1
                print("STORED\n\n")
            

    plotPos(actualPos, calcPos)

# --------------------------------------------------------------------------------------

else:
    print( "Really?? Restart script 'cause I ain't doing it for you" )
# ************************************************************************
# =============================> DEPRECATED <=============================
# ************************************************************************
#
