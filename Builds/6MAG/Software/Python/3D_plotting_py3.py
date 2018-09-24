'''
*
* Position tracking of magnet based on Finexus
* https://ubicomplab.cs.washington.edu/pdfs/finexus.pdf
*
*   - 3 Modes of operations
*       (1) Point-by-Point (Data Sampling)
*       (2) 2D Static Plot (Data Sampling)
*       (3) 3D Static Plot (Data Sampling)
*       (4) 3D Continuous Live Plot
*
* VERSION: 1.3
*   - MODIFIED: Use MayaVI to perform plotting since it allows
*               for greater flexibility and drastically
*               improves plot update time (does NOT rerender plot
*               at each iteration ).
*   - ADDED   : Store data into a log file
*   - FIXED   : Corrected K values for multiple magnets
*   - ADDED   : Point-by-point
*
* KNOWN ISSUES:
*   - Minor loss in accuracy in 3D space
*
* AUTHOR                    :   Edward Nichols
* LAST CONTRIBUTION DATE    :   Jan. 25th, 2017 Year of Our Lord
* 
* AUTHOR                    :   Mohammad Odeh 
* LAST CONTRIBUTION DATE    :   Jan. 25th, 2018 Year of Our Lord
*
'''

# Tracking + Solver Modules
import  numpy                   as      np              # Import Numpy
from    mayavi                  import  mlab            # Data visualization
from    time                    import  sleep, clock    # Sleep for stability, clock for profiling
from    time                    import  time            # Time for timing (like duh!)
from    scipy.optimize          import  root            # Solve System of Eqns for (x, y, z)
from    scipy.linalg            import  norm            # Calculate vector norms (magnitude)
from    usbProtocol             import  createUSBPort   # Create USB port (serial comm. w\ Arduino)
from    threading               import  Thread          # Used to thread processes
from    queue                   import  Queue           # Used to queue input/output
import  os, platform                                    # Directory/file manipulation

# ************************************************************************
# =====================> DEFINE NECESSARY FUNCTIONS <====================*
# ************************************************************************


def argsort( seq ):
    '''
    Sort a list's elements from smallest to largest and
    return the sorted INDICES NOT VALUES!
    
    INPUTS:
        - seq: A list whose elements are to be sorted.

    OUTPUT:
        - A list containing the indices of the given list's elements
          arranged from the index of the element with the smallest
          value to the index of the element with the largest value
    '''
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key=seq.__getitem__)

# --------------------------

def bubbleSort( arr, N ):
    '''
    Sort a list's elements from smallest to largest.
    
    INPUTS:
        - arr: List to be sorted.
        - N  : Number of elements in said list that need to be sorted.
                (i.e list has 5 elements, if N=3, sort the first 3)

    OUTPUT:
        - A sorted list of size N.
    '''
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
    return( data )

# --------------------------

def getData( ser ):
    '''
    Pool the data from the MCU (wheteher it be a Teensy or an Arduino or whatever)
    The data consists of the magnetic field components in the x-, y-, and z-direction
    of all the sensors. The array must begin with '<' as the SOH signal, the compononents
    must be comma delimited, and must end with '>' as the EOT signal.
    
            >$\     <B_{1x}, B_{1y}, B_{1z}, ..., B_{1x}, B_{1y}, B_{1z}> 
    
    INPUTS:
        - ser: a serial object. Note that the serial port MUST be open before
               passing it the to function.

    OUTPUT:
        - Individual numpy arrays of all the magnetic field vectors.
    '''
    global CALIBRATING

    # Flush buffer
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    # Allow data to fill-in buffer
    # sleep(0.1)

    try:
        # Wait for the sensor to calibrate itself to ambient fields.
        while( True ):
            if(CALIBRATING == True):
                print( "Calibrating...\n" )
                CALIBRATING = False
            if ser.in_waiting > 0:  
                inData = ser.read()  
                if inData == '<':
                    break  

        # Read the actual data value. Stop at End of Data specifier '>'. 
        line = ''
        while( True ):
            if ser.in_waiting > 0:
                inData = ser.read()
                if inData == '>':
                    break
                line = line + inData

        # Split line into the constituent components
        col     = (line.rstrip()).split(",")
        if (len(col) == 18):
            #
            # Construct magnetic field array
            #

            # Sensor 1
            Bx = float( col[0] )
            By = float( col[1] )
            Bz = float( col[2] )
            B1 = np.array( ([Bx],[By],[Bz]), dtype='float64') # Units { G }

            # Sensor 2
            Bx = float( col[3] )
            By = float( col[4] )
            Bz = float( col[5] )
            B2 = np.array( ([Bx],[By],[Bz]), dtype='float64') # Units { G }

            # Sensor 3
            Bx = float( col[6] )
            By = float( col[7] )
            Bz = float( col[8] )
            B3 = np.array( ([Bx],[By],[Bz]), dtype='float64') # Units { G }

            # Sensor 4
            Bx = float( col[9]  )
            By = float( col[10] )
            Bz = float( col[11] )
            B4 = np.array( ([Bx],[By],[Bz]), dtype='float64') # Units { G }

            # Sensor 5
            Bx = float( col[12] )
            By = float( col[13] )
            Bz = float( col[14] )
            B5 = np.array( ([Bx],[By],[Bz]), dtype='float64') # Units { G }

            # Sensor 6
            Bx = float( col[15] )
            By = float( col[16] )
            Bz = float( col[17] )
            B6 = np.array( ([Bx],[By],[Bz]), dtype='float64' )# Units { G }
            
            # Return vectors
            return ( B1, B2, B3, B4, B5, B6 )
        else:
            return ( getData(ser) )

    except Exception as e:
        print( "Caught error in getData()"      )
        print( "Error type %s" %str(type(e))    )
        print( "Error Arguments " + str(e.args) )

# --------------------------

def LHS( root, K, norms ):
    '''
    Construct the left hand side (LHS) of the equations
    to numerically solve for.
    Recall that in order to solve a system numerically it
    must have the form of,
    
                >$\  f(x, y, z, ...) = LHS = 0
    
    INPUTS:
        - root  : a numpy array contating the initial guesses of the roots.
        - K     : K is a property of the magnet and has units of { G^2.m^6 }.
        - norms : An array/list of the vector norms of the magnetic field
                  vectors for all the sensors.

    OUTPUT:
        - An array of equations that are sorted corresponding to which
          3 sensors' equations are going to be used with the LMA solver.
          The sorting is based on which 3 sensors are closest to the magnet.
    '''
    
    # Extract x, y, and z
    x, y, z = root
    
    # Construct the (r) terms for each sensor
    # NOTE: Relative distance terms are in meters
    #     : Standing on sensor(n), how many units in
    #       the x/y/z direction should I march to get
    #       back to sensor1 (origin)?
    r1 = float( ( (x+0.000)**2. + (y+0.000)**2. + (z+0.00)**2. )**(1/2.) )  # Sensor 1 (ORIGIN)
    r2 = float( ( (x+0.000)**2. + (y-0.125)**2. + (z+0.00)**2. )**(1/2.) )  # Sensor 2
    r3 = float( ( (x-0.100)**2. + (y+0.050)**2. + (z+0.00)**2. )**(1/2.) )  # Sensor 3
    r4 = float( ( (x-0.100)**2. + (y-0.175)**2. + (z+0.00)**2. )**(1/2.) )  # Sensor 4
    r5 = float( ( (x-0.200)**2. + (y+0.000)**2. + (z+0.00)**2. )**(1/2.) )  # Sensor 5
    r6 = float( ( (x-0.200)**2. + (y-0.125)**2. + (z+0.00)**2. )**(1/2.) )  # Sensor 6

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
    sort = argsort( norms )             # Auxiliary function sorts norms from smallest to largest
    sort.reverse()                      # Python built-in function reverses elements of list
    f=[]                                # Declare vector to hold relevant functions

    for i in range(0, 3):               # Fill functions' array with the equations that correspond to
        f.append( Eqns[sort[i]] )       # the sensors with the highest norm, thus closest to magnet
        
    # Return vector
    return ( f )

# --------------------------

def findIG( magFields ):
    '''
    Dynamic search of initial guess for the LMA solver based on magnitude
    of the magnetic field relative to all the sensors.
    A high magnitude reading indicates magnet is close to some 3
    sensors, the centroid of the traingle created by said sensors
    is fed as the initial guess.
    
    INPUTS:
        - magfield: a numpy array containing all the magnetic field readings.

    OUTPUT:
        - A numpy array containing <x, y, z> values for the initial guess.
    '''
    
    # Define IMU positions on the grid
    #      / sensor 1: (x, y, z)
    #     /  sensor 2: (x, y, z)
    # Mat=      :          :
    #     \     :          :
    #      \ sensor 6: (x, y, z)
    IMU_pos = np.array(((0.0  , 0.0  ,   0.0) ,
                        (0.0  , 0.125,   0.0) ,
                        (0.100,-0.050,   0.0) ,
                        (0.100, 0.175,   0.0) ,
                        (0.200, 0.0  ,   0.0) ,
                        (0.200, 0.125,   0.0)), dtype='float64')

    # Read current magnetic field from MCU
    (H1, H2, H3, H4, H5, H6) = magFields

    # Compute L2 vector norms
    HNorm = [ float( norm(H1) ), float( norm(H2) ),
              float( norm(H3) ), float( norm(H4) ),
              float( norm(H5) ), float( norm(H6) ) ]
    
    # Determine which sensors to use based on magnetic field value (smallValue==noBueno!)
    sort = argsort( HNorm )             # Auxiliary function sorts norms from smallest to largest
    sort.reverse()                      # Python built-in function reverses elements of list

    IMUS = bubbleSort( sort, 3 )

    # Return the initial guess as the centroid of the detected triangle
    return ( np.array(((IMU_pos[IMUS[0]][0]+IMU_pos[IMUS[1]][0]+IMU_pos[IMUS[2]][0])/3.,
                       (IMU_pos[IMUS[0]][1]+IMU_pos[IMUS[1]][1]+IMU_pos[IMUS[2]][1])/3.,
                       (IMU_pos[IMUS[0]][2]+IMU_pos[IMUS[1]][2]+IMU_pos[IMUS[2]][2])/3. -0.01), dtype='float64') )

# --------------------------

def generate_cartesian_volume( fig, length = 250, spacing = 10 ):
    '''
    Generates a meshed cartesian volume that encapsulates the ROI.
    
    INPUTS:
        - fig    : Scene/figure to populate.
        - length : Length of axes ( generates a KxKxK sized cube ).
        - spacing: Spacing between consecutive lines.

    OUTPUT:
        - No return; generates a mesh on the render window.
    '''
    print( "Constructing cartesian volume ..." ),
    
    K = length + 1                                          # Number of lines to plot
    N = spacing                                             # Subdivisions (aka K/N lines are drawn)

    # Draw horizontal lines on the xy-, yz-, and xz-planes
    lvlC_H  = np.arange( 0, K, N )                          # Horizontal level curve
    lvlC_V  = np.zeros_like( lvlC_H )                       # Vertical level curve
    H, V    = np.meshgrid( lvlC_H, lvlC_V )                 # Mesh both arrays to a matrix (a grid)
    lvlC_0  = np.zeros_like( H )                            # Force everything into a 2D plane by setting the 3rd plane to 0

    for i in range (0, K, N):
        mlab.mesh( H, V+i, lvlC_0,
                   figure = fig,
                   representation = 'mesh',
                   tube_radius = 0.25,
                   color = (1., 1., 1.) )
        
        mlab.mesh( lvlC_0, H, V+i,
                   figure = fig,
                   representation = 'mesh',
                   tube_radius = 0.25,
                   color = (1., 1., 1.) )
        
        mlab.mesh( H, lvlC_0, V+i,
                   figure = fig,
                   representation = 'mesh',
                   tube_radius = 0.25,
                   color = (1., 1., 1.) )

    # Draw vertical lines on the xy-, yz-, and xz-planes
    lvlC_V  = np.arange( 0, K, N )                          # Vertical level curve
    lvlC_H  = np.zeros_like( lvlC_V )                       # Horizontal level curve
    H, V    = np.meshgrid( lvlC_H, lvlC_V )                 # Mesh both arrays to form a matrix (a grid)
    lvlC_0  = np.zeros_like( H )                            # Force everything into a 2D plane by setting the 3rd plane to 0

    for i in range (0, K, N):
        mlab.mesh( H+i, V, lvlC_0,
                   figure = fig,
                   representation = 'mesh',
                   tube_radius = 0.25,
                   color = (1., 1., 1.) )
        
        mlab.mesh( lvlC_0, H+i, V,
                   figure = fig,
                   representation = 'mesh',
                   tube_radius = 0.25,
                   color = (1., 1., 1.) )
        
        mlab.mesh( H+i, lvlC_0, V,
                   figure = fig,
                   representation = 'mesh',
                   tube_radius = 0.25,
                   color = (1., 1., 1.) )

    # Generate outline and label axes
    mlab.outline( extent = [0, K-1, 0, K-1, 0, K-1], figure = fig )
    mlab.axes( extent = [0, K-1, 0, K-1, 0, K-1],
               figure = fig,
               line_width = 1.0,
               x_axis_visibility=True,
               y_axis_visibility=True,
               z_axis_visibility=True )

    print( "SUCCESS!" )

# --------------------------

def read_STL( fig, STLfile, meshMode ):
    '''
    Read ASCII STL file and generate mesh.
    
    INPUTS:
        - fig     : Scene/figure to populate.
        - STLfile : A string contating the name/path of the STL file to mesh.
        - meshMode: Sets the meshing mode;
                    meshMode=='staticMesh'  for static  plots.
                    meshMode=='dynamicMesh' for dynamic plots.

    OUTPUT:
        - No return; generates a mesh on the render window.
    '''

    print( "Generating mesh of STL file ..." ),
    
    x=[]    # ...
    y=[]    # List to hold extracted vertices
    z=[]    # ...

    # Open STL file and read contents
    with open( STLfile,'r' ) as f:

        scaleFactor = 1.0                   # Define a scaling factor (if needed)
        for line in f:                      # Read line-by-line
            strarray=line.split()           # Split constituent parts into seperate entities
            if( strarray[0]=='vertex' ):    # Extract vertices
                x = np.append( x, np.double( strarray[1] )/scaleFactor )
                y = np.append( y, np.double( strarray[2] )/scaleFactor )
                z = np.append( z, np.double( strarray[3] )/scaleFactor )

        if( meshMode=='staticMesh' ):
            # 3D Track Mesh
            # Translate mesh to origin
            x = x + (75.00)/scaleFactor
            y = y + (87.50)/scaleFactor
            z = z + ( 50.00)/scaleFactor
            
        elif( meshMode=='dynamicMesh' ):
            # Standarized Patient Mesh
            # Translate mesh from origin to nipple (yay!)
            x = x + (275.00)/scaleFactor
            y = y - (125.00)/scaleFactor
            z = z - (150.00)/scaleFactor

            # Rotate STL mesh
            temp = np.copy(y)
            y = -1*np.copy(z)
            z = temp

        else: raise Exception
        
        # Identify triangles
        triangles = [ (i, i+1, i+2) for i in range(0, len(x), 3) ]

        # Generate mesh!
        mlab.triangular_mesh( x, y, z, triangles,
                              figure = fig,
                              representation = 'surface',
                              tube_radius = 1.0,
                              color = (1, 1, 1),
                              opacity = 0.75 )

        print( "SUCCESS!" )
        
# --------------------------

def compute_coordinate():
    '''
    Compute the magnet's position in cartesian space.
    
    INPUTS:
        - No inputs.

    OUTPUT:
        - position: The most current and updated position
                    of the magnet in cartesian space.
    '''

    global initialGuess                                             # Modify from within function
    start = time()                                                  # Call clock() for accurate time readings

    # Data acquisition
    (H1, H2, H3, H4, H5, H6) = getData(IMU)                         # Get data from MCU
    
    # Compute norms
    HNorm = [ float(norm(H1)), float(norm(H2)),                     #
              float(norm(H3)), float(norm(H4)),                     # Compute L2 vector norms
              float(norm(H5)), float(norm(H6)) ]                    #
    
    # Solve system of equations
    sol = root(LHS, initialGuess, args=(K, HNorm), method='lm',     # Invoke solver using the
               options={'ftol':1e-10, 'xtol':1e-10, 'maxiter':1000, # Levenberg-Marquardt 
                        'eps':1e-8, 'factor':0.001})                # Algorithm (aka LMA)

    # Store solution in array
    position = np.array( (sol.x[0]*1000,                            # x-axis
                          sol.x[1]*1000,                            # y-axis
                          sol.x[2]*1000,                            # z-axis
                          time()-start  ), dtype='float64' )        # time

    # Check value
    if( position[2] < 0 ): position[2] = -1*position[2]             # Make sure z-value
    else: pass                                                      # ... is ALWAYS +ve
    
    # Print solution (coordinates) to screen
    print( "(x, y, z, t): (%.3f, %.3f, %.3f, %.3f)" %( position[0],
                                                       position[1],
                                                       position[2],
                                                       position[3] ) )
    
    # Check if solution makes sense
    if (abs(sol.x[0]*1000) > 500) or (abs(sol.x[1]*1000) > 500) or (abs(sol.x[2]*1000) > 500):
        initialGuess = findIG( getData(IMU) )                       # Determine initial guess based on magnet's location
        return( compute_coordinate() )                              # Recursive call of function()
        
    # Update initial guess with current position and feed back to solver
    else:
        initialGuess = np.array( (sol.x[0]+dx, sol.x[1]+dx,         # Update the initial guess as the
                                  sol.x[2]+dx), dtype='float64' )   # current position and feed back to LMA
                                 
        return( position )                                          # Return position
            
# --------------------------

def storeData( data ):
    '''
    Store computed position co-ordinates into a .txt file
    
    INPUTS:
        - data: A list containing all the computed co-ordinate points
    '''
    
    print( "Storing data log under data.txt ..." ) ,

    # Unzip data into x, y, z
    x, y, z, t = data[0], data[1], data[2], data[3]

    # Setup paths!
    if platform.system()=='Windows':

        # Define useful paths
        homeDir = os.getcwd()
        dst     = homeDir + '\\output'
        dataFile= dst + '\\data.txt'

    elif platform.system()=='Linux':

        # Define useful paths
        homeDir = os.getcwd()
        dst = homeDir + '/output'
        dataFile= dst + '/data.txt'
    
    # Check if directory exists
    if ( os.path.exists(dst)==False ):
        # Create said directory
        os.makedirs(dst)

    # Write into file
    with open( dataFile, "a" ) as f:
        for i in range( 0, len(x) ):
                f.write(str(x[i]) + "," + str(y[i]) + "," + str(z[i]) + "," + str(t[i]) + "\n")

    print( "SUCCESS!" )

# --------------------------

@mlab.animate(delay=25)
def animate():
    '''
    Callback function to update and animate the plot.
    
    INPUTS:
        - No inputs.

    OUTPUT:
        - No return; does internal calls to update plot.
    '''
    
    f = mlab.gcf()                                      # Get engine handle of figure
    
    while( True ):                                      # Loop 43va
        try:
            # Update
            pos = compute_coordinate()                  # Get updated magnet position

            # Draw
            plt.mlab_source.set( x = pos[0],            # Update last drawn point ...
                                 y = pos[1],            # ... on graph with the ...
                                 z = pos[2] )           # ... current position.
            yield

        except KeyboardInterrupt:
            mlab.close( all=True )                      # Close all figures and scenes
            
# --------------------------

def plot_2D( points, a=0, b=251 ):
    '''
    Perfom a 2D plot.
    
    INPUTS:
        - points: numpy array of points to plot in the order of (x, y, z).
        - a     : placeholder for now
        - b     : placeholder for now

    OUTPUT:
        - No return; generates a 2D plot.
    '''
    
    x, y = points                                       # Store data into arrays
    z = np.zeros_like(x)                                # We don't want th

    scene = mlab.figure( size= (1000, 800),             # Create scene
                         fgcolor=(0, 0, 0),             # Set foreground color
                         bgcolor=(1, 1, 1) )            # Set background color

    nodes = mlab.points3d( x, y, z,                     # ...
                           figure = scene,              # Insert collected data to plot
                           scale_factor=5.0 )           # ...
    
    xlab = mlab.xlabel( "x" )                           # Set x-axis label
    ylab = mlab.ylabel( "y" )                           # Set y-axis label
    
    mlab.axes( extent = [0, b-1, 0, b-1, 0, 0.5],       # Set extent of axes
               figure = scene,                          # The figure to populate
               y_axis_visibility=False)                 # Remove the z-axis (designated y for some MayaVi reason)

    scene.scene.z_plus_view()                           # Look at it from the top!
    scene.scene.parallel_projection = True              # 2D projection of 3D plane

    mlab.show()
            
# --------------------------
        
# ************************************************************************
# ===========================> SETUP PROGRAM <===========================
# ************************************************************************

# Useful variables
global CALIBRATING
global initialGuess

CALIBRATING = True                                      # Boolean to indicate that device is calibrating

##K           = 1.09e-6                                   # Big magnet's constant             (K) || Units { G^2.m^6}
##K           = 2.46e-7                                   # Spherical magnet's constant       (K) || Units { G^2.m^6}
##K           = 1.87e-7                                   # Small magnet's constant (w\hole)  (K) || Units { G^2.m^6}
K           = 1.29e-7                                   # Small magnet's constant  (flat)   (K) || Units { G^2.m^6}
dx          = 1e-7                                      # Differential step size (Needed for solver)
calcPos     = []                                        # Empty array to hold calculated positions


# Establish connection with Arduino
DEVC = "Arduino"                                        # Device Name (not very important)
PORT = 4                                                # Port number (VERY important)
BAUD = 115200                                           # Baudrate    (VERY VERY important)

# Error handling in case serial communcation fails (1/2)
try:
    IMU = createUSBPort( DEVC, PORT, BAUD )             # Create serial connection
    if IMU.is_open == False:                            # Make sure port is open
        IMU.open()
    print( "Serial Port OPEN" )

    initialGuess = findIG( getData(IMU) )               # Determine initial guess based on magnet's location

# Error handling in case serial communcation fails (2/2)
except Exception as e:
    print( "Could NOT open serial port" )
    print( "Error type %s" %str(type(e)) )
    print( "Error Arguments " + str(e.args) )
    sleep( 2.5 )
    quit()                                              # Shutdown entire program

# ************************************************************************
# =========================> MAKE IT ALL HAPPEN <=========================
# ************************************************************************

# Choose mode of operation
print( "Choose plotting mode:" )                        # ...
print( "1. Point-by-Point (Data Sampling)." )           # Inform user of ...
print( "2. 2D Static Plot (Data Sampling)." )           # all the possible ...
print( "3. 3D Static Plot (Data Sampling)" )            # plotting modes.
print( "4. 3D Continuous Live Plot." )                  # ...

mode = raw_input(">\ ")                                 # Wait for user input

print( "\n******************************************" )
print( "*NOTE: Press Ctrl-C to save data and exit."   )
print( "******************************************\n" )
sleep( 1.0 )                                            # Allow user to read note
#clock()                                                # Call clock() for accurate time readings

# --------------------------------------------------------------------------------------

# If "Point-by-Point" mode was selected:
if ( mode == '1' ):

    x, y = np.array([]), np.array([])                   # Initialize empty numpy arrays
    z, t = np.array([]), np.array([])                   # for x, y, z, and t
    
    while( True ):                                      # Loop 43va
        try:
            print( "Place magnet at desired location." )# Inform user to place magnet
            sleep( 1.0 )                                # Allow user time to react

            var = raw_input( "Ready? (Y/N): " )         # Prompt user if ready or nah!

            if( var=='Y' or var=='y' ):

                print( "Collecting data for 20s..." )
                
                startTime = time()
                while( time() - startTime < 20 ):
                    # Update
                    pos = compute_coordinate()          # Get updated magnet position
                    
                    x = np.append( x, pos[0] )          # Append computed values
                    y = np.append( y, pos[1] )          # of x, y, z, and t 
                    z = np.append( z, pos[2] )          # to their respective
                    t = np.append( t, pos[3] )          # arrays.

                print( "SUCCESS!" )                     # Inform that points were captured.

            else: pass                                  # In case user is not ready, repeat loop
            
        except KeyboardInterrupt:
            print( '' )                                 # Start with a newline for aesthetics
            
            # Store data points in text file
            storeData( (x, y, z, t) )                   # Zip into one list
            
            # Setup MayaVI environment
            scene = mlab.figure( size=(1000, 800) )     # Create window
            generate_cartesian_volume( scene )          # Generate mesh of volume

            # Draw
            nodes = mlab.points3d( x, y, z,             # ...
                                   figure = scene,      # Insert collected data to plot
                                   scale_factor=0.5 )   # ...

            # Impose properties
            colors = 1.0 * (x + y)/(max(x)+max(y))      # Rainbow color the plotted points
            nodes.glyph.scale_mode = 'scale_by_vector'
            nodes.mlab_source.dataset.point_data.scalars = colors

            mlab.show()                                 # Show figure

            break                                       # Break from loop!
    
# --------------------------------------------------------------------------------------

# If "2D Static Plot" mode was selected:
if ( mode == '2' ):
    x, y = np.array([]), np.array([])                   # Initialize empty numpy arrays
    
    while( True ):                                      # Loop 43va
        try:
            # Update
            pos = compute_coordinate()                  # Get updated magnet position
            
            x = np.append( x, pos[0] )
            y = np.append( y, pos[1] )

        except KeyboardInterrupt:
            listly = (x, y)                             # Pack numpy array in a list
            plot_2D( listly )                           # Plot!
            break                                       # Break out of loop.

# --------------------------------------------------------------------------------------

# If "3D Static Plot" mode was selected:
if ( mode == '3' ):
    
    x, y = np.array([]), np.array([])                   # Initialize empty numpy arrays
    z, t = np.array([]), np.array([])                   # for x, y, z, and t
    
    while( True ):                                      # Loop 43va
        try:
            # Update
            pos = compute_coordinate()                  # Get updated magnet position
            
            x = np.append( x, pos[0] )                  # Append computed values
            y = np.append( y, pos[1] )                  # of x, y, z, and t 
            z = np.append( z, pos[2] )                  # to their respective
            t = np.append( t, pos[3] )                  # arrays.
            
        except KeyboardInterrupt:
            print( '' )                                 # Start with a newline for aesthetics
            
            # Store data points in text file
            storeData( (x, y, z, t) )                   # Zip into one list
            
            # Setup MayaVI environment
            scene = mlab.figure( size=(1000, 800) )     # Create window
            generate_cartesian_volume( scene )          # Generate mesh of volume
            STLfile = "butts.stl"                       # Path to STL file
            read_STL( scene, STLfile, 'staticMesh' )    # Read STL file

            # Draw
            nodes = mlab.points3d( x, y, z,             # ...
                                   figure = scene,      # Insert collected data to plot
                                   scale_factor=5.0 )   # ...

            # Impose properties
            colors = 1.0 * (x + y)/(max(x)+max(y))      # Rainbow color the plotted points
            nodes.glyph.scale_mode = 'scale_by_vector'
            nodes.mlab_source.dataset.point_data.scalars = colors

            mlab.show()                                 # Show figure

            break                                       # Break from loop!
        
# --------------------------------------------------------------------------------------

# If "3D Live Plot" mode was selected:
elif ( mode == '4' ):

    # Setup MayaVI environment
    scene = mlab.figure( size=(1000, 800) )             # Create window
    generate_cartesian_volume( scene )                  # Generate mesh of volume
    STLfile = "SP_PH02_Torso (ASCII).stl"               # Path to STL file
    read_STL( scene, STLfile, 'dynamicMesh' )           # Read STL file

    # Start the plot with the points given by the initial guess
    plt = mlab.points3d( initialGuess[0], initialGuess[1], initialGuess[2],
                         figure = scene, resolution=100, scale_factor=35.0 )

    # Let the show begin!
    animate()
    mlab.show()

