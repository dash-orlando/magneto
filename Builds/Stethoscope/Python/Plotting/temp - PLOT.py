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
from    time                import  sleep, time     # Sleep for stability, clock for profiling
from    scipy.optimize      import  root            # Solve System of Eqns for (x, y, z)
from    scipy.linalg        import  norm            # Calculate vector norms (magnitude)
from    Queue               import  Queue       # Last in First out queue
from    threading           import  Thread          # Multithread data
from    ctypes              import  *               # Import ctypes (VERY IMPORTANT)
import  os, platform                                # Directory/file manipulation

# ************************************************************************
# =====================> DEFINE NECESSARY FUNCTIONS <====================*
# ************************************************************************

def loadLib():
    ''' Load library and prime with ctypes '''
    global lib
    path = "/home/pi/LSM9DS1_RaspberryPi_Library/lib/liblsm9ds1cwrapper.so"
    lib = cdll.LoadLibrary(path)

    lib.lsm9ds1_create.argtypes = [c_uint]
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


# ------------------------------------------------------------------------

def setupMux():
    ''' Setup multiplexer '''
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(23, GPIO.OUT)
    GPIO.setup(24, GPIO.OUT)
    GPIO.setup(25, GPIO.OUT)

# ------------------------------------------------------------------------

def setSensor( sensorIndex ):
    ''' Switch between all the sensors '''
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

# ------------------------------------------------------------------------

def setupIMU():
    ''' Setup IMUS and callibrate them'''
    global IMU_Base
    global imu
    global imu_LOW

    low1 = 0x1c
    low2 = 0x6a

    high1 = 0x1e
    high2 = 0x6b
    
    IMU_Base = np.empty((6,3), dtype='float64') # Construct matrix of size  (6x3)

    # Setup HIGH sensors
    imu = lib.lsm9ds1_create(1) # Create an instance
    for i in range(0, 3):
        setSensor( i )                          # Select the IMU
        lib.lsm9ds1_begin(imu)                  # Initialize it

        if lib.lsm9ds1_begin(imu) == 0:         # In case it fails
            print("Failed to communicate with LSM9DS1.")
            quit()

        else:                                   # In case it doesn't, configure
            CALIBRATION_INDEX = 25             # Average over this many readings
            lib.lsm9ds1_calibrateMag(imu)       # Call built-in calibration routine
            lib.lsm9ds1_setMagScale(imu, 16)    # Set scale to +/-16Gauss
            lib.lsm9ds1_calibrateMag(imu)       # Call built-in calibration routine

            cmx, cmy, cmz = 0, 0, 0

            # Perform user-built calibration to further clear noise
            for j in range(0, CALIBRATION_INDEX):
                lib.lsm9ds1_readMag(imu)

                cmx += lib.lsm9ds1_calcMag(imu, lib.lsm9ds1_getMagX(imu))
                cmy += lib.lsm9ds1_calcMag(imu, lib.lsm9ds1_getMagY(imu))
                cmz += lib.lsm9ds1_calcMag(imu, lib.lsm9ds1_getMagZ(imu))

            # Average all the readings
            IMU_Base[i][0] = cmx/CALIBRATION_INDEX
            IMU_Base[i][1] = cmy/CALIBRATION_INDEX
            IMU_Base[i][2] = cmz/CALIBRATION_INDEX
            print( "Correction constant for sensor %d is:" %(i+1) )
            print( "x: %.5f, y: %.5f, z: %.5f\n" %(IMU_Base[i][0], IMU_Base[i][1], IMU_Base[i][2]) )

    # Setup LOW sensors
    imu_LOW = lib.lsm9ds1_create(0) # Create an instance
    for i in range(0, 3):
        setSensor( i )                          # Select the IMU
        lib.lsm9ds1_begin(imu_LOW)                  # Initialize it

        if lib.lsm9ds1_begin(imu_LOW) == 0:         # In case it fails
            print("Failed to communicate with LSM9DS1.")
            quit()

        else:                                   # In case it doesn't, configure
            CALIBRATION_INDEX = 25             # Average over this many readings
            lib.lsm9ds1_calibrateMag(imu_LOW)       # Call built-in calibration routine
            lib.lsm9ds1_setMagScale(imu_LOW, 16)    # Set scale to +/-16Gauss
            lib.lsm9ds1_calibrateMag(imu_LOW)       # Call built-in calibration routine

            cmx, cmy, cmz = 0, 0, 0

            # Perform user-built calibration to further clear noise
            for j in range(0, CALIBRATION_INDEX):
                lib.lsm9ds1_readMag(imu_LOW)
                
                cmx += lib.lsm9ds1_calcMag(imu_LOW, lib.lsm9ds1_getMagX(imu_LOW))
                cmy += lib.lsm9ds1_calcMag(imu_LOW, lib.lsm9ds1_getMagY(imu_LOW))
                cmz += lib.lsm9ds1_calcMag(imu_LOW, lib.lsm9ds1_getMagZ(imu_LOW))

            # Average all the readings
            IMU_Base[i+3][0] = cmx/CALIBRATION_INDEX
            IMU_Base[i+3][1] = cmy/CALIBRATION_INDEX
            IMU_Base[i+3][2] = cmz/CALIBRATION_INDEX
            print( "Correction constant for sensor %d is:" %(i+4) )
            print( "x: %.5f, y: %.5f, z: %.5f\n" %(IMU_Base[i+3][0], IMU_Base[i+3][1], IMU_Base[i+3][2]) )

# ------------------------------------------------------------------------        

def argsort(seq):
    ''' Sort list from lowest to highest. Returns the indices of the respective values in a list '''
    ''' i.e. Given: [6, 20, 9, 18] || Returns: [1, 3, 2, 0] '''
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key=seq.__getitem__)

# ------------------------------------------------------------------------

def bubbleSort(arr, N):
    ''' Sort list elements from smallest to largest '''
    ''' i.e. Given: t = [6, 20, 9, 18] || bubbleSort(t, 3) = [6, 9, 20]'''
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

# ------------------------------------------------------------------------

def calcMag( N, Q ):
    ''' Collect readings from IMU '''
    B = np.empty((N,3), dtype='float64')                # Construct matrix of size  (Nx3)
    while(True):
        for i in range(0, 3):
            setSensor( i )                                  # Select sensor ( i )

            while lib.lsm9ds1_magAvailable(imu) == 0:       # While no data is available,
                pass                                        # do nothing

            lib.lsm9ds1_readMag(imu)                        # Read values from sensor
            lib.lsm9ds1_readMag(imu_LOW)
            
            mx = lib.lsm9ds1_calcMag(imu, lib.lsm9ds1_getMagX(imu))
            my = lib.lsm9ds1_calcMag(imu, lib.lsm9ds1_getMagY(imu))
            mz = lib.lsm9ds1_calcMag(imu, lib.lsm9ds1_getMagZ(imu))

            mx_LOW = lib.lsm9ds1_calcMag(imu_LOW, lib.lsm9ds1_getMagX(imu_LOW))
            my_LOW = lib.lsm9ds1_calcMag(imu_LOW, lib.lsm9ds1_getMagY(imu_LOW))
            mz_LOW = lib.lsm9ds1_calcMag(imu_LOW, lib.lsm9ds1_getMagZ(imu_LOW))

            if ( i == 0 ):
                B[i] = np.array( (mx_LOW, my_LOW, mz_LOW), dtype='float64' )   # Units { G }
                B[i+3] = np.array( (mx, my, mz), dtype='float64' )   # Units { G }
            else:
                B[i] = np.array( (mx, my, mz), dtype='float64' )   # Units { G }
                B[i+3] = np.array( (mx_LOW, my_LOW, mz_LOW), dtype='float64' )   # Units { G }

        # Return array
        Q.put_nowait( B - IMU_Base )

# ------------------------------------------------------------------------

def findIG( Q ):
    ''' Guess the magnet's initial position '''
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
    H = Q.get()

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

# ------------------------------------------------------------------------

def LHS( root, K, norms ):

    # Extract x, y, and z
    x, y, z = root
    
    # Construct the (r) terms for each sensor
    # NOTE: Relative distance terms are in meters
    #     : Standing on sensor(n), how many units in
    #       the x/y/z direction should I march to get
    #       back to sensor1 (origin)?
    r1 = float( ( (x+0.000)**2. + (y-0.125)**2. + (z+0.00)**2. )**(1/2.) )  # Sensor 1
    r2 = float( ( (x-0.100)**2. + (y-0.175)**2. + (z+0.00)**2. )**(1/2.) )  # Sensor 2
    r3 = float( ( (x-0.200)**2. + (y-0.125)**2. + (z+0.00)**2. )**(1/2.) )  # Sensor 3
    r4 = float( ( (x+0.000)**2. + (y+0.000)**2. + (z+0.00)**2. )**(1/2.) )  # Sensor 4 (ORIGIN)
    r5 = float( ( (x-0.100)**2. + (y+0.050)**2. + (z+0.00)**2. )**(1/2.) )  # Sensor 5
    r6 = float( ( (x-0.200)**2. + (y-0.000)**2. + (z+0.00)**2. )**(1/2.) )  # Sensor 6

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

def plotPosCONT(calculated):
     
    data = (calculated)
    print( "Passed on %d data points to plotPosCONT" %len(data) )
    
    # Create plot
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, facecolor="1.0")


    # major ticks every 5, minor ticks every 1                                      
    major_ticks = np.arange(-10, 236, 5)                                              
    minor_ticks = np.arange(-10 ,236, 1)                                               

    ax.set_xticks(major_ticks)                                                       
    ax.set_xticks(minor_ticks, minor=True)                                           
    ax.set_yticks(major_ticks)                                                       
    ax.set_yticks(minor_ticks, minor=True)

    # Set xy-axes scale + labels
    ax.set_xlim([-10, 235])
    ax.set_ylim([-10, 235])
    ax.set_xlabel('Distance (mm)')
    ax.set_ylabel('Distance (mm)')

    # Add a grid                                                       
    ax.grid(which='both')                                                            

    # Modify transperancy settings for the grids:                               
    ax.grid(which='minor', alpha=0.2)                                                
    ax.grid(which='major', alpha=0.5)

    # Extract data
    x_calc = []
    y_calc = []
    for i in range(0,len(calculated)):
        x_calc.append(calculated[i][0])
        y_calc.append(calculated[i][1])
    ax.scatter(x_calc, y_calc, alpha=0.8, color='g', s=30, label="Calculated")

    
    plt.title('Calculated Position')
    plt.legend(loc=2)
    plt.show()

# ************************************************************************
# ===========================> SETUP PROGRAM <===========================
# ************************************************************************

# Useful variables
K           = 1.09e-6                           # Magnet's constant (K) || Units { G^2.m^6}
dx          = 1e-7                              # Differential step size (Needed for solver)
H           = np.empty((6,3), dtype='float64')  # Construct matrix of size  (6x3)
NSENS       = 6                                 # Number of sensors used
calcPos = [] 

# Start sensors
loadLib()
setupMux()
setupIMU()

Q_calcMag = Queue( maxsize=0 )              # LIFO queue qith infinite size

# Start pooling data from serial port
t_calcMag = Thread( target=calcMag, args=(NSENS, Q_calcMag,) )
t_calcMag.daemon = True
t_calcMag.start()

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
    print( "Place magnet on track" )
    sleep( 2.5 )
    print( "Ready in 3" )
    sleep( 1.0 )
    print( "Ready in 2" )
    sleep( 1.0 )
    print( "Ready in 1" )
    sleep( 1.0 )
    print( "GO!" )
    initialGuess = findIG( Q_calcMag )
    while ( True ):
        try:
            startTime = time()
            
            H = Q_calcMag.get_nowait()
    
            # Compute L2 vector norms
            HNorm = [ float(norm(H[0])), float(norm(H[1])),
                      float(norm(H[2])), float(norm(H[3])),
                      float(norm(H[4])), float(norm(H[5])) ]

            # Invoke solver (using Levenberg-Marquardt)
            sol = root(LHS, initialGuess, args=(K, HNorm), method='lm',
                       options={'ftol':1e-10, 'xtol':1e-10, 'maxiter':500,
                                'eps':1e-8, 'factor':0.001})

            # Print solution (coordinates) to screen
            pos = [sol.x[0]*1000, sol.x[1]*1000, sol.x[2]*1000, float(time()-startTime)]
            #print( "(x, y, z): (%.3f, %.3f, %.3f) Time: %.3f" %(pos[0], pos[1], pos[2], pos[3]) )
            

            # Check if solution makes sense
            if (abs(sol.x[0]*1000) > 500) or (abs(sol.x[1]*1000) > 500) or (abs(sol.x[2]*1000) > 500):
                # Determine initial guess based on magnet's location
                #print("NOT STORED\n\n")
                initialGuess = findIG( Q_calcMag )
                
            # Update initial guess with current position and feed back to solver
            else:
                calcPos.append(pos)
                initialGuess = np.array( (sol.x[0]+dx, sol.x[1]+dx, sol.x[2]+dx), dtype='float64' )
                #print("STORED\n\n")

        # Save data on EXIT
        except KeyboardInterrupt:
            print( "Plotting %i datapoints" %len(calcPos) )
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
                        
            plotPosCONT(calcPos)
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
