'''
*
* LSM9DS1 class for python based on:
* https://github.com/akimach/LSM9DS1_RaspberryPi_Library.git
*
* VERSION: 1.6
*   - ADDED   : Multithreading for faster performance
*
* KNOWN ISSUES:
*   - None ATM
*
* Author        :   Mohammad Odeh
* Date          :   Nov. 21st, 2017 Year of Our Lord
* Last Modified :   Jan.  9th, 2018 Year of Our Lord
*
'''
import  numpy               as      np              # Import Numpy
import  RPi.GPIO            as      GPIO            # Use GPIO pins
from    threading           import  Thread          # Multithread for faster performance
from    time                import  sleep, time     # Sleep for stability
from    ctypes              import  *               # Import ctypes (VERY IMPORTANT)

class TheGreatMoesException(Exception):

    def __init__(self):
        Exception.__init__(self, "Number of sensors must be 1 OR an even integer. All hail Moe!")

# ------------------------------------------------------------------------

class IMU(object):

    def __init__( self, path, nSensors, pins ):
        '''
        LSM9DS1 IMU sensor.

        INPUTS:
            - path    : Absolute path to library as a string
            - nSensors: An integer type number of sensors to use
            - pins    : A list containing the BCM number of GPIO
                        pins to use for the multiplexer select lines
        '''

        # Load library and prime ctypes
        self.lib = cdll.LoadLibrary( path )
        self.lib.create.argtypes = [c_uint]
        self.lib.create.restype = c_void_p

        self.lib.begin.argtypes = [c_void_p]
        self.lib.begin.restype = None

        self.lib.calibrateMag.argtypes = [c_void_p]
        self.lib.calibrateMag.restype = None

        self.lib.magAvailable.argtypes = [c_void_p]
        self.lib.magAvailable.restype = c_int

        self.lib.readMag.argtypes = [c_void_p]
        self.lib.readMag.restype = c_int

        self.lib.getMagX.argtypes = [c_void_p]
        self.lib.getMagX.restype = c_float
        self.lib.getMagY.argtypes = [c_void_p]
        self.lib.getMagY.restype = c_float
        self.lib.getMagZ.argtypes = [c_void_p]
        self.lib.getMagZ.restype = c_float

        self.lib.calcMag.argtypes = [c_void_p, c_float]
        self.lib.calcMag.restype = c_float

        # Setup the multiplexer (enable pins)
        self.setupMux( pins )

        # Record the number of sensors being used
        self.nSensors = nSensors
        
        # Check if number of sensors is valid
        if( (nSensors != 1) and (nSensors%2 != 0) ):
            raise TheGreatMoesException
        
        # Create necessary matrices
        else:
            self.IMU_Base = np.zeros( (nSensors, 3), dtype='float64' )  # Baseline readings (to be subtracted)
            self.IMU_Raw  = np.zeros( (nSensors, 3), dtype='float64' )  # Raw readings (non calibrated)
            self.exp_avg  = np.zeros( (nSensors, 3), dtype='float64' )  # Exponential moving average array
            self.IMU = []

# ------------------------------------------------------------------------

    def setupMux( self, pins ):
        '''
        Setup multiplexer

        INPUTS:
            - pins: GPIO pins used for controlling select lines

        OUTPUT:
            - NON
        '''
        
        self.S0, self.S1, self.S2 = pins
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.S0, GPIO.OUT)
        GPIO.setup(self.S1, GPIO.OUT)
        GPIO.setup(self.S2, GPIO.OUT)

# ------------------------------------------------------------------------

    def selectSensor( self, sensorIndex, debounce=0.005 ):
        '''
        Switch between all the sensors

        INPUTS:
            - sensorIndex: index of the sensor pair

        OUTPUT:
            - NON
        '''
        
        # Line 1, 000
        if ( sensorIndex == 0 ):
            GPIO.output(self.S0, GPIO.LOW)
            GPIO.output(self.S1, GPIO.LOW)
            GPIO.output(self.S2, GPIO.LOW)
            sleep( debounce )
            
        # Line 2, 001
        elif ( sensorIndex == 1 ):
            GPIO.output(self.S0, GPIO.HIGH)
            GPIO.output(self.S1, GPIO.LOW)
            GPIO.output(self.S2, GPIO.LOW)
            sleep( debounce )

        # Line 3, 010
        elif ( sensorIndex == 2 ):
            GPIO.output(self.S0, GPIO.LOW)
            GPIO.output(self.S1, GPIO.HIGH)
            GPIO.output(self.S2, GPIO.LOW)
            sleep( debounce )
            
        # Line 4, 011
        elif ( sensorIndex == 3):
            GPIO.output(self.S0, GPIO.HIGH)
            GPIO.output(self.S1, GPIO.HIGH)
            GPIO.output(self.S2, GPIO.LOW)
            sleep( debounce )

        # Line 5, 100
        elif ( sensorIndex == 4):
            GPIO.output(self.S0, GPIO.LOW)
            GPIO.output(self.S1, GPIO.LOW)
            GPIO.output(self.S2, GPIO.HIGH)
            sleep( debounce )

        # Line 6, 101
        elif (sensorIndex == 5):
            GPIO.output(self.S0, GPIO.HIGH)
            GPIO.output(self.S1, GPIO.LOW)
            GPIO.output(self.S2, GPIO.HIGH)
            sleep( debounce )

        else:
            print("Invalid Index")
        
# ------------------------------------------------------------------------

    def start( self, mScl=16, N_avg=50 ):
        '''
        Create, set scale, and calibrate IMUS in one go.

        INPUTS:
            - mScl : can be 4, 8, 12, or 16
            - N_avg: number of readings to average over

        OUTPUT:
            - NON
        '''
        
        print( "Starting %i IMUs" %self.nSensors )
        self.create()
        self.setMagScale( mScl )
        self.calibrateMag( N_avg )

# ------------------------------------------------------------------------

    def create( self ):
        '''
        Create an IMU object.

        INPUTS:
            - NON

        OUTPUT:
            - NON
        '''
        
        print( "Creating IMU objects..." ) ,
        
        # A list containing the sensors will alternate between HIGH
        # and LOW addresses (HIGH==even #s, LOW==odd #s)
        
        agAddrHi, mAddrHi = 0x6b, 0x1e
        agAddrLo, mAddrLo = 0x6b, 0x1c
        
        for i in range(0, self.nSensors):

            # Store HIGH I2C Address in even indices
            if( i%2 == 0 ):
                self.IMU.append( self.lib.create(agAddrHi, mAddrHi) )

            # Store LOW I2C Address in odd indices
            else:
                self.IMU.append( self.lib.create(agAddrLo, mAddrLo) )

            # Start the sensor
            if( self.lib.begin( self.IMU[i] ) == 0 ):
                print( "FAILED TO COMMUNICATE!" )
                quit()
                
        print( "DONE!" )
        
# ------------------------------------------------------------------------

    def setMagScale( self, mScl=16 ):
        '''
        Set scale of magnetic field readings

        INPUTS:
            - mScl: can be 4, 8, 12, or 16
        '''
        
        print( "Setting scale..." ) ,
        
        for i in range( 0, (self.nSensors/2) ):
            self.selectSensor( i )                          # Switch the select line
            
            self.lib.setMagScale( self.IMU[2 * i], mScl )   # Set Hi scale to mScl
            self.lib.setMagScale( self.IMU[2*i+1], mScl )   # Set Lo scale to mScl

        print( "DONE!" )
        
# ------------------------------------------------------------------------

    def calibrateMag( self, N_avg=50 ):
        '''
        Calibrate sensor using built-in function + average readings.

        INPUTS:
            - N_avg: number of readings to average over
        '''

        hold = np.zeros((self.nSensors,3), dtype='float64') # Temporary matrix for intermediate calculations
        for i in range( 0, (self.nSensors/2) ):

            self.selectSensor( i )                          # Switch the select line
            print( "Sensor pair %d selected" %(i+1) )
            
            print( "Performing built-in calibration routine..." ) ,
            self.lib.calibrateMag( self.IMU[2 * i] )        # Call built-in calibration routine
            self.lib.calibrateMag( self.IMU[2*i+1] )        # Call built-in calibration routine
            print( "DONE!" )
            
            cmxHi, cmyHi, cmzHi = 0, 0, 0                   # Temporary calibration ...
            cmxLo, cmyLo, cmzLo = 0, 0, 0                   # ... variables for Hi & Lo

            # Perform user-built calibration to further clear noise
            print( "Performing user-defined calibration routine..." ) ,
            for j in range(0, N_avg):
                self.lib.readMag( self.IMU[2 * i] )         # Read Hi I2C magnetic field
                self.lib.readMag( self.IMU[2*i+1] )         # Read Lo I2C magnetic field
                
                xHi = self.lib.calcMag( self.IMU[2 * i], self.lib.getMagX(self.IMU[2 * i]) )
                yHi = self.lib.calcMag( self.IMU[2 * i], self.lib.getMagY(self.IMU[2 * i]) )
                zHi = self.lib.calcMag( self.IMU[2 * i], self.lib.getMagZ(self.IMU[2 * i]) )

                xLo = self.lib.calcMag( self.IMU[2*i+1], self.lib.getMagX(self.IMU[2*i+1]) )
                yLo = self.lib.calcMag( self.IMU[2*i+1], self.lib.getMagY(self.IMU[2*i+1]) )
                zLo = self.lib.calcMag( self.IMU[2*i+1], self.lib.getMagZ(self.IMU[2*i+1]) )

                hold[2 * i] = np.array( (xHi, yHi, zHi),    # Store readings for Hi I2C
                                         dtype='float64' )  # (filtered then averaged for IMU_Base)
                hold[2*i+1] = np.array( (xLo, yLo, zLo),    # Store readings for Lo I2C
                                         dtype='float64' )  # (filtered then averaged for IMU_Base)

                hold[2 * i] = self.ema_filter( (2 * i),     # Apply filter on Hi readings
                                               hold[2 * i],
                                               first_run=True )
                hold[2*i+1] = self.ema_filter( (2*i+1),     # Apply filter on Lo readings
                                               hold[2*i+1],
                                               first_run=True )

                cmxHi += hold[2 * i][0]                     # ...
                cmyHi += hold[2 * i][1]                     # Sum all Hi readings
                cmzHi += hold[2 * i][2]                     # ...

                cmxLo += hold[2*i+1][0]                     # ...
                cmyLo += hold[2*i+1][1]                     # Sum all Lo readings
                cmzLo += hold[2*i+1][2]                     # ...
            
            self.IMU_Base[2 * i][0] = cmxHi/N_avg           # Average the readings for ...
            self.IMU_Base[2 * i][1] = cmyHi/N_avg           # ... Hi I2C and store in ...
            self.IMU_Base[2 * i][2] = cmzHi/N_avg           # ... the calibration matrix.

            self.IMU_Base[2*i+1][0] = cmxLo/N_avg           # Average the readings for ...
            self.IMU_Base[2*i+1][1] = cmyLo/N_avg           # ... Lo I2C and store in ...
            self.IMU_Base[2*i+1][2] = cmzLo/N_avg           # ... the calibration matrix.

            print( "DONE!" )
            
            print( "Correction constant for Hi sensor %i is:" %(i+1) )
            print( "x: %.5f, y: %.5f, z: %.5f\n" %(self.IMU_Base[2 * i][0],
                                                   self.IMU_Base[2 * i][1],
                                                   self.IMU_Base[2 * i][2]) )

            print( "Correction constant for Lo sensor %i is:" %(i+1) )
            print( "x: %.5f, y: %.5f, z: %.5f\n" %(self.IMU_Base[2*i+1][0],
                                                   self.IMU_Base[2*i+1][1],
                                                   self.IMU_Base[2*i+1][2]) )

# ------------------------------------------------------------------------

    def calcMag( self, multithreading=True ):
        '''
        Calibrated magnitude readings.
        
        INPUTS:
            - multithreading: True (default) enables multithreading

        OUTPUT:
            - Calibrated/smoothed magnetic field readings
        '''
        start = time()
        for i in range(0, (self.nSensors/2) ):

            self.selectSensor( i )                                  # Switch the select line

            # If multithreading is flagged
            if( multithreading ):
                t_calcHi = Thread ( target=self.__calcHi,           # Create a thread for the Hi IMU
                                    args=(i, ) )                    # ...
                t_calcLo = Thread ( target=self.__calcLo,           # Create a thread for the Lo IMU
                                    args=(i, ) )                    # ...
                
                t_calcHi.daemon = True                              # Set thread as daemon
                t_calcLo.daemon = True                              # Set thread as daemon
                
                t_calcHi.start()                                    # Start threads for ...
                t_calcLo.start()                                    # ... Hi & Lo IMUs

            # If multithreading is set to False
            else:
                self.__calcHi( i )                                  # Call private method to read Hi IMU
                self.__calcLo( i )                                  # Call private method to read Lo IMU
            
        print( time()-start )
        
        return(self.IMU_Raw - self.IMU_Base)                        # Return CALIBRATED readings
    
# ------------------------------------------------------------------------

    def __calcHi( self, i ):
        '''
        Private method that returns calibrated magnitude
        readings for Hi sensor.
        
        INPUTS:
            - i: index at which the select line is

        OUTPUT:
            - NON
        '''
        
        self.lib.readMag( self.IMU[2 * i] )                     # Read Hi I2C magnetic field

        mxHi = self.lib.calcMag( self.IMU[2 * i], self.lib.getMagX(self.IMU[2 * i]) )
        myHi = self.lib.calcMag( self.IMU[2 * i], self.lib.getMagY(self.IMU[2 * i]) )
        mzHi = self.lib.calcMag( self.IMU[2 * i], self.lib.getMagZ(self.IMU[2 * i]) )

        self.IMU_Raw[2 * i] = np.array( (mxHi, myHi, mzHi),     # Store RAW readings for Hi I2C
                                        dtype='float64' )       # Units { G }
        self.ema_filter( (2 * i), self.IMU_Raw[2 * i] )         # Apply EMA Filter

# ------------------------------------------------------------------------

    def __calcLo( self, i ):
        '''
        Private method that returns calibrated magnitude
        readings for Lo sensor.
        
        INPUTS:
            - i: index at which the select line is

        OUTPUT:
            - NON
        '''

        self.lib.readMag( self.IMU[2*i+1] )                     # Read Lo I2C magnetic field

        mxLo = self.lib.calcMag( self.IMU[2*i+1], self.lib.getMagX(self.IMU[2*i+1]) )
        myLo = self.lib.calcMag( self.IMU[2*i+1], self.lib.getMagY(self.IMU[2*i+1]) )
        mzLo = self.lib.calcMag( self.IMU[2*i+1], self.lib.getMagZ(self.IMU[2*i+1]) )
        
        self.IMU_Raw[2*i+1] = np.array( (mxLo, myLo, mzLo),     # Store RAW readings for Lo I2C
                                        dtype='float64' )       # Units { G }
        self.ema_filter( (2*i+1), self.IMU_Raw[2*i+1] )         # Apply EMA Filter

# ------------------------------------------------------------------------

    def ema_filter( self, ndx, current_val, ALPHA=0.25, first_run=False ):
        '''
        Exponential Moving Average for further smoothing of data.
        Recall that the exponential moving average has the form of: 

            s_n = ALPHA*x_n + ( 1-ALPHA )*s_{n-1}
            where 0 < ALPHA < 1 is the smoothing factor
            High ALPHA: NO smoothing.
            Low ALPHA : YES smoothing.
            VERY Low ALPHA: GREAT smoothing but less responsive to recent changes.

        INPUTS:
            - ndx        : index of readings (which IMU's readings)
            - current_val: readings to be smoothed
            - ALPHA      : Alpha value
            - first_run  : If True, then the function operates under calibration mode

        OUTPUT:
            - Smoothed data readings
        '''
        
        # Filter data
        self.exp_avg[ndx] = ALPHA*current_val + (1 - ALPHA)*self.exp_avg[ndx]

        # Put back filtered data into the correct matrix\index
        if( first_run ):
            return( self.exp_avg[ndx] )
        else:
            self.IMU_Raw[ndx]  = self.exp_avg[ndx]
            
# ------------------------------------------------------------------------

##path = "/home/pi/LSM9DS1_RaspberryPi_Library/lib/liblsm9ds1cwrapper.so"
##nSensors = 6
##muxPins = [22, 23, 24]
##
##imus = IMU(path, nSensors, muxPins)
##imus.start()
##while( True ):
##    val = imus.calcMag()
##    for i in range( 0, len(val)/2 ):
##        print( "PAIR #%i" %(i+1) )
##        print( "    Hi: %.5f, %.5f, %.5f" %(val[2 * i][0], val[2 * i][1], val[2 * i][2]) )
##        print( "    Lo: %.5f, %.5f, %.5f" %(val[2*i+1][0], val[2*i+1][1], val[2*i+1][2]) )
##    print( "" )
##
