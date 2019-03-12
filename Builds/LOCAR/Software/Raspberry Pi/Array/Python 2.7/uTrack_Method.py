'''
Position tracking of magnet

Author: Danny, Moe
Date: Aug. 4th, 2017th year of our Lord
'''

# Import Modules
import  serial, random
import  numpy           as      np
from    time            import  sleep, time
from    math            import  *
from    scipy.optimize  import  fsolve
##from    sympy           import  nsolve
from    usbProtocol     import  createUSBPort

######################################################
#                   FUNCTION DEFINITIONS
######################################################

#

# Function to print obtained values:
def printVals(H1, H2, angle, virPos1, virPos2, realPos1, realPos2):
    
    start = time()
    for i in range(len( H1[0] )):
        print( "\n=======================================" )
        print( "============ITERATION: %4i============" %i )
        print( "=======================================\n" )
        print( "ANGLES:" )
        print( "=======================================" )
        print( "Value of alpha : %.5f" %(angle[0][i]) )
        print( "Value of beta  : %.5f" %(angle[1][i]) )
        print( "Value of gamma : %.5f" %(angle[2][i]) )
        print( "Value of gamma': %.5f\n" %(angle[3][i]) )
        
        print( "SENSOR ONE 1:" )
        print( "=======================================" )
        print( "H_x_1 = %.5f" %H1[0][i])
        print( "H_y_1 = %.5f" %H1[1][i])
        print( "H_z_1 = %.5f\n" %H2[2][i])

        print( "Virtual x_1: %.4f" %virPos1[0][i] )
        print( "Virtual y_1: %.4f" %virPos1[1][i] )
        print( "Real x_1: %.4f" %realPos1[0][i] )
        print( "Real y_1: %.4f" %realPos1[1][i] )
        print( "Real z_1: %.4f\n" %realPos1[2][i] )
        
        print( "SENSOR TWO 2:" )
        print( "=======================================" )
        print( "H_x_2 = %.5f" %H2[0][i])
        print( "H_y_2 = %.5f" %H2[1][i])
        print( "H_z_2 = %.5f\n" %H2[2][i])

        print( "Virtual x_2: %.4f" %virPos2[0][i] )
        print( "Virtual y_2: %.4f" %virPos2[1][i] )
        print( "Real x_2: %.4f" %realPos2[0][i] )
        print( "Real y_2: %.4f" %realPos2[1][i] )
        print( "Real z_2: %.4f\n" %realPos2[2][i] )
    print( "Time to print %i iterations: %.3f" %( len(H1[0]), time()-start) )
    
# Solve matrices for location
def solveMatrix(a, b, y, p, loc_x, loc_y, sensor):

    a11 = cos(b)*cos(y)
    a12 = -cos(b)*sin(y)
    a13 = sin(b)
    a21 = cos(a)*sin(y)+cos(y)*sin(a)*sin(b)
    a22 = cos(a)*cos(y)-sin(a)*sin(b)*sin(y)
    a23 = -cos(b)*sin(a)
    a31 = sin(a)*sin(y)-cos(a)*cos(y)*sin(b)
    a32 = cos(y)*sin(a)+cos(a)*sin(b)*sin(y)
    a33 = cos(a)*cos(b)

    location = []
    
    if sensor == 1:
        T = np.mat(((a11, a12, a13),
                    (a21, a22, a23),
                    (a31, a32, a33)), dtype='f')

        T_inverse   = np.linalg.inv(T)
        virLocation = np.array( ([loc_x],
                                 [loc_y],
                                 [0]    ), dtype='f')

##        reLoc[0] = (T_inverse*virLocation).item(0)
##        reLoc[1] = (T_inverse*virLocation).item(1)
##        reLoc[2] = (T_inverse*virLocation).item(2)
        reLoc = T_inverse*virLocation

        return reLoc.item(0), reLoc.item(1), reLoc.item(2)
        
    elif sensor == 2:
        T = np.mat(((a11*cos(p)+a12*sin(p), -a11*sin(p)+a12*cos(p), a13),
                    (a21*cos(p)+a22*sin(p), -a21*sin(p)+a22*cos(p), a23),
                    (a31*cos(p)+a32*sin(p), -a31*sin(p)+a32*cos(p), a33)), dtype='f')

        T_inverse   = np.linalg.inv(T)
        virLocation = np.array( ([loc_x],
                                 [loc_y],
                                 [0]    ), dtype='f')

##        reLoc[0] = (T_inverse*virLocation).item(0)
##        reLoc[1] = (T_inverse*virLocation).item(1)
##        reLoc[2] = (T_inverse*virLocation).item(2)
        reLoc = T_inverse*virLocation

        return reLoc.item(0), reLoc.item(1), reLoc.item(2)

# Pool data from Arduino
def getData(ser):
    global B_x_1, B_y_1, B_z_1  # IMU readings from sensor 1
    global B_x_2, B_y_2, B_z_2  # IMU readings from sensor 2
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    try:
        line = ser.readline()[:-1]
        col = line.split(",")

        #Throwing out bad data. Waiting for the sensor to calibrate itself to ambient fields. 
        if len(col) < 6:
            print "Waiting..."
            return False

        else:
            #Casting the split input values as floats.
            B_x_1=float(col[0])
            B_y_1=float(col[1])
            B_z_1=float(col[2])
            B_x_2=float(col[3])
            B_y_2=float(col[4])
            B_z_2=float(col[5])
            return True

    except Exception as e:
        print( "Caught error in getData()"      )
        print( "Error type %s" %str(type(e))    )
        print( "Error Arguments " + str(e.args) )

### Define equations:
# Hx
def H_X( aa, bb, yy, phi, B_x, B_y, B_z, sensor ):
    if sensor == 1:
        # Equation for sensor 1
        return( (B_x*( cos(bb)*cos(yy) ) - B_y*( cos(bb)*sin(yy) ) + B_z*( sin(bb) )) )

    elif sensor == 2:
        a_11 = cos(bb)*cos(yy)
        a_12 = -cos(bb)*sin(yy)
        a_13 = sin(bb)
        # Equation for sensor 2
        return( B_x*( a_11*cos(phi) + a_12*sin(phi) ) + B_y*(a_12*cos(phi)-a_11*sin(phi)) + B_z*(a_13) )

# Hy
def H_Y( aa, bb, yy, phi, B_x, B_y, B_z, sensor ):
    if sensor == 1:
        # Equation for sensor 1
        return( (B_x*( cos(aa)*sin(yy)+cos(yy)*sin(aa)*sin(bb) ) +
                 B_y*( cos(aa)*cos(yy)-sin(aa)*sin(bb)*sin(yy) ) -
                 B_z*( cos(bb)*sin(aa) ) ) )

    elif sensor == 2:
        # Equation for sensor 2
        a_21 = cos(aa)*sin(yy)+cos(yy)*sin(aa)*sin(bb)
        a_22 = cos(aa)*cos(yy)-sin(aa)*sin(bb)*sin(yy)
        a_23 = -cos(bb)*sin(aa)
        return( B_x*(a_21*cos(phi)+a_22*sin(phi)) + B_y*(a_22*cos(phi)-a_21*sin(phi)) + B_z*(a_23) )

# Hz
def H_Z( aa, bb, yy, phi, B_x, B_y, B_z, sensor ):
    if sensor == 1:
        # Equation for sensor 1
        return( (B_x*( sin(aa)*sin(yy)-cos(aa)*cos(yy)*sin(bb) ) +
                 B_y*( cos(yy)*sin(aa)+cos(aa)*sin(bb)*sin(yy) ) +
                 B_z*( cos(aa)*cos(bb) ) ) )

    elif sensor == 2:
        # Equation for sensor 2
        a_31 = sin(aa)*sin(yy)-cos(aa)*cos(yy)*sin(bb)
        a_32 = cos(yy)*sin(aa)+cos(aa)*sin(bb)*sin(yy)
        a_33 = cos(aa)*cos(bb)
        return( (B_x*( a_31*cos(phi) + a_32*sin(phi) ) +
                 B_y*( a_32*cos(phi) - a_31*sin(phi) ) +
                 B_z*( a_33 ) ) )

# LHS of [H] of sensor 1
def LHS_1( x0, beta, gamma, B_x, B_y, B_z ):

    alpha = x0
    return( (B_x*( sin(alpha)*sin(gamma)-cos(alpha)*cos(gamma)*sin(beta) ) +
             B_y*( cos(gamma)*sin(alpha)+cos(alpha)*sin(beta)*sin(gamma) ) +
             B_z*( cos(alpha)*cos(gamma) ) ) )

# LHS of [H] of sensor 2
def LHS_2( x0, aa, bb, yy, B_x, B_y, B_z ):

    phi = x0
    a_31 = sin(aa)*sin(yy)-cos(aa)*cos(yy)*sin(bb)
    a_32 = cos(yy)*sin(aa)+cos(aa)*sin(bb)*sin(yy)
    a_33 = cos(aa)*cos(bb)
    return( (B_x*( a_31*cos(phi) + a_32*sin(phi) ) +
             B_y*( a_32*cos(phi) - a_31*sin(phi) ) +
             B_z*( a_33 ) ) )

# Location in virtual space
def location_virtual (p, H_x, H_y):
    x, y = p
    return ( (K*(2*x*x+y*y)/pow(sqrt(x*x+y*y), 5) - H_x), (K*(3*x*y)/pow(sqrt(x*x+y*y), 5) - H_y) )

######################################################
#                   SETUP PROGRAM
######################################################

# Magnetic field vector components
global B_x_1, B_y_1, B_z_1  # IMU readings from sensor 1
global B_x_2, B_y_2, B_z_2  # IMU readings from sensor 2
global K
K   = 19.081e-4

distance_apart = 0.350

### Declare arrays to store values:
# Computed values of H
H_1 = [[] for i in range(3)]        # [0]:Hx    || [1]:Hy   || [2]:Hz
H_2 = [[] for i in range(3)]        # [0]:Hx    || [1]:Hy   || [2]:Hz
# Numerically evaluated angles
angles = [[] for i in range(4)]     # [0]:alpha || [1]:beta || [2]:gamma || [3]:phi
# Location in virtual space
virLoc_1 = [[] for i in range(2)]   # [0]:x     || [1]:y
virLoc_2 = [[] for i in range(2)]   # [0]:x     || [1]:y
# Location in our real physical meaningful(less?) world
reaLoc_1 = [[] for i in range(3)]   # [0]:x     || [1]:y    || [3]:z
reaLoc_2 = [[] for i in range(3)]   # [0]:x     || [1]:y    || [3]:z

# Establish connection with Arduino
try:
    ser = createUSBPort( "Arduino", 6, 115200 )
    if ser.is_open == False:
        ser.open()
    print( "Serial Port OPEN" )

except Exception as e:
    print( "Could NOT open serial port" )
    print( "Error type %s" %str(type(e)) )
    print( " Error Arguments " + str(e.args) )
    sleep( 5 )
    quit()

### Sensor 1 readings
##B_x_1 = random.random()*5
##B_y_1 = random.random()*5
##B_z_1 = random.random()*5
##print( "Sensor 1 readings:" )
##print( B_x_1, B_y_1, B_z_1 )

### Sensor 2 readings
##B_x_2 = random.random()*5
##B_y_2 = random.random()*5
##B_z_2 = random.random()*5
##print( "\nSensor 2 readings:" )
##print( B_x_2, B_y_2, B_z_2 )


######################################################
#                   START PROGRAM
######################################################

check = getData(ser)
while check == False:
    check = getData(ser)

print( "READY in 5seconds" )
sleep(1)
print( "Ready in 4seconds" )
sleep(1)
print( "Ready in 3seconds" )
sleep(1)
print( "Ready in 2seconds" )
sleep(1)
print( "Ready in 1seconds" )
sleep(1)
print( "GO!" )

loop = True
while(loop==True):
    # Get one more "fresh" set of readings
    getData(ser)
        
    ### Sensor 1 readings
    print( "Sensor 1 readings:" )
    print( B_x_1, B_y_1, B_z_1 )

    ### Sensor 2 readings
    print( "Sensor 2 readings:" )
    print( B_x_2, B_y_2, B_z_2 )
    # Start iteration
    start = time()
    N=3600
    for i in range(0,N,1):
        for j in range(0,N,1):
            bb=i*np.pi/1800.
            yy=j*np.pi/1800.
            
            # Find angle alpha that imposes constraint 1 (sensor 1)
            try:
                aa = fsolve(LHS_1, 0.1, args=(bb, yy, B_x_1, B_y_1, B_z_1) )
                sen1_constraint1 = LHS_1(aa, bb, yy, B_x_1, B_y_1, B_z_1)
            except Exception as e:
                print( "Caught ERROR:\n%r" %type(e) )
                pass

            # Check if constraint 1 is met (sensor 1)
            if (sen1_constraint1 <= 1e-6) and (sen1_constraint1 >= -1e-6):
                H_x_1 = H_X(aa, bb, yy, 0, B_x_1, B_y_1, B_z_1, 1)
                H_y_1 = H_Y(aa, bb, yy, 0, B_x_1, B_y_1, B_z_1, 1)
                H_z_1 = H_Z(aa, bb, yy, 0, B_x_1, B_y_1, B_z_1, 1)

                # Obtain (x, y) in "virtual" space (sensor 1)
                try:
                    x_1 , y_1 = fsolve(location_virtual, (0.1,0.1), args=(H_x_1, H_y_1) )
                except:
                    pass

                # Find angle phi that imposes constraint 1 (sensor 2)
                try:
                    phi = fsolve(LHS_2, 0.1, args=(aa, bb, yy, B_x_2, B_y_2, B_z_2))
                    sen2_constraint1 = LHS_2(phi, aa, bb, yy, B_x_2, B_y_2, B_z_2)
                except Exception as e:
                    print( "Caught ERROR:\n%r" %type(e) )
                    pass
                
                # Check if constraint 1 is met (sensor 2)
                if (sen2_constraint1 <= 1e-6) and (sen2_constraint1 >= -1e-6):
                    H_x_2 = H_X(aa, bb, yy, phi, B_x_2, B_y_2, B_z_2, 2)
                    H_y_2 = H_Y(aa, bb, yy, phi, B_x_2, B_y_2, B_z_2, 2)
                    H_z_2 = H_Z(aa, bb, yy, phi, B_x_2, B_y_2, B_z_2, 2)

                    # Obtain (x, y) in "virtual" space (sensor 2)
                    try:
                        x_2 , y_2 = fsolve(location_virtual, (0.1,0.1), args=(H_x_2, H_y_2))
                    except:
                        pass

                    
                    # Convert values back to real space by multiplying with
                    # the inverse of the transformation matrices
                    xx_1, yy_1, zz_1 = solveMatrix(aa, bb, yy, phi, x_1, y_1, 1)
                    xx_2, yy_2, zz_2 = solveMatrix(aa, bb, yy, phi, x_2, y_2, 2)

                    # Find difference
                    dx = xx_1 - xx_2
                    dy = yy_2 - yy_1
                    dz = zz_2 - zz_1

                    # Print differences
##                    print( "x=%.6f" %dx )
##                    print( "y=%.6f" %dy )
##                    print( "z=%.6f" %dz )
                    
                    # Impose 2nd constraint
                    if (dz <= 1e-3 ) and (dz >= -1e-3):
                        #print( "Imposed z=%.6f" %dz )
                        if (dy <= 1e-3) and (dy >= -1e-3):
                            #print( "Imposed y=%.6f" %dy )
                            if ((dx - distance_apart) <= 1e-3) and ((dx - distance_apart) >= -1e-3):
                                #print( "Imposed x=%.6f" %dx )
                                print( "ACTUAL LOCATION AT (%.3f, %.3f, %.3f)" %(xx_1, yy_1, zz_1) )
                                print( "Found at indices i: %.3f AND j: %.3f" %(i, j) )
                        
                    
                    
                    
                    # Append values to array for printing
                    H_1[0].append(H_x_1)
                    H_1[1].append(H_y_1)
                    H_1[2].append(H_z_1)
                    H_2[0].append(H_x_2)
                    H_2[1].append(H_y_2)
                    H_2[2].append(H_z_2)
                    angles[0].append((aa*180/np.pi))
                    angles[1].append((bb*180/np.pi))
                    angles[2].append((yy*180/np.pi))
                    angles[3].append((phi*180/np.pi))
                    virLoc_1[0].append(x_1)
                    virLoc_1[1].append(y_1)
                    virLoc_2[0].append(x_2)
                    virLoc_2[1].append(y_2)
                    reaLoc_1[0].append(xx_1)
                    reaLoc_1[1].append(yy_1)
                    reaLoc_1[2].append(zz_1)
                    reaLoc_2[0].append(xx_2)
                    reaLoc_2[1].append(yy_2)
                    reaLoc_2[2].append(zz_2)
                    continue
            
    end = time() - start
    print( "Time to complete %r iterations: %.5f" %(N*N, end) )
    print( "Solutions found: %i\n" %len(H_1[0]) )
    loop = false
##    sleep( 2.5 )
##
##    print( "SENSOR ONE 1:" )
##    print( "=======================================" )
##    print( "Real x_1: %.4f" %reaLoc_1[0][-1] )
##    print( "Real y_1: %.4f" %reaLoc_1[1][-1] )
##    print( "Real z_1: %.4f\n" %reaLoc_1[2][-1] )
##    
##    print( "SENSOR TWO 2:" )
##    print( "=======================================" )
##    print( "Real x_2: %.4f" %reaLoc_2[0][-1] )
##    print( "Real y_2: %.4f" %reaLoc_2[1][-1] )
##    print( "Real z_2: %.4f\n" %reaLoc_2[2][-1] )

##    # Reset arrays
##    for i in range (0,3):
##        del H_1[i][:]
##        del H_2[i][:]
##        if i > 1:
##            pass
##        else:
##            del virLoc_1[i][:]
##            del virLoc_2[i][:]
##        del reaLoc_1[i][:]
##        del reaLoc_2[i][:]
##        if i == 2:
##            del angles[i+1][:]
##        else:
##            del angles[i][:]    

##printVals( H_1, H_2, angles, virLoc_1, virLoc_2, reaLoc_1, reaLoc_2)


### List equations:
##H_x = B_x*( cos(bb)*cos(yy) )                         - B_y*( cos(bb)*sin(yy) )                         + B_z*( sin(bb) )
##H_y = B_x*( cos(aa)*sin(yy)+cos(yy)*sin(aa)*sin(bb) ) + B_y*( cos(aa)*cos(yy)-sin(aa)*sin(bb)*sin(yy) ) - B_z*( cos(bb)*sin(aa) )
##H_z = B_x*( sin(aa)*sin(yy)-cos(aa)*cos(yy)*sin(bb) ) + B_y*( cos(yy)*sin(aa)+cos(aa)*sin(bb)*sin(yy) ) + B_z*( cos(aa)*cos(bb) )




######################################################
#                   DEPRACATED
######################################################
'''
# Angle of projection to xy-plane
angle_project = atan(B_z/sqrt( (B_x*B_x) + (B_y*B_y) ) )
print( angle_project*180/3.1415927 )

================================================================================

aa, bb, yy = 0, np.pi, np.pi/2

# Transformation matrix
T_x = np.mat  ( ((  1       ,   0       ,   0       ),
                (   0       , cos(aa)   , -sin(aa)  ),
                (   0       , sin(aa)   ,  cos(aa)  )), dtype='f')

T_y = np.mat  ( (( cos(bb)  ,   0       , sin(bb)   ),
                (   0       ,   1       ,   0       ),
                ( -sin(bb)  ,   0       , cos(bb)   )), dtype='f')

T_z = np.mat  ( (( cos(yy)  , -sin(yy)  ,   0       ),
                (  sin(yy)  ,  cos(yy)  ,   0       ),
                (   0       ,   0       ,   1       )), dtype='f')


T_xyz = np.mat(((           cos(bb)*cos(yy)                 ,               -cos(bb)*sin(yy)            ,   sin(bb)             ),
                (   cos(aa)*sin(yy)+cos(yy)*sin(aa)*sin(bb) , cos(aa)*cos(yy)-sin(aa)*sin(bb)*sin(yy)   ,   -cos(bb)*sin(aa)    ),
                (   sin(aa)*sin(yy)-cos(aa)*cos(yy)*sin(bb) , cos(yy)*sin(aa)+cos(aa)*sin(bb)*sin(yy)   ,   cos(aa)*cos(bb)     )), dtype='f')

print( "T_x:" )
print( T_x )
print( "\nT_y:" )
print( T_y )
print( "\nT_z:" )
print( T_z )

T = T_x * T_y * T_z
print( "\nT:" )
print( T )

print( "\nT_xyz:" )
print( T_xyz )

================================================================================

soln = nsolve(  [B_x*( sin(aa)*sin(yy)-cos(aa)*cos(yy)*sin(bb) ) +
                 B_y*( cos(yy)*sin(aa)+cos(aa)*sin(bb)*sin(yy) ) +
                 B_z*( cos(aa)*cos(bb) )],
                [aa],
                [1] )
print( soln )

================================================================================

# Solve matrices for location
def solveMatrix(a, b, y, p, sensor):

    a11 = cos(b)*cos(y)
    a12 = -cos(b)*sin(y)
    a13 = sin(b)
    a21 = cos(a)*sin(y)+cos(y)*sin(a)*sin(b)
    a22 = cos(a)*cos(y)-sin(a)*sin(b)*sin(y)
    a23 = -cos(b)*sin(a)
    a31 = sin(a)*sin(y)-cos(a)*cos(y)*sin(b)
    a32 = cos(y)*sin(a)+cos(a)*sin(b)*sin(y)
    a33 = cos(a)*cos(b)

    if sensor == 1:
        T = np.mat(((a11, a12, a13),
                    (a21, a22, a23),
                    (a31, a32, a33)), dtype='f')

        T_inverse = np.linalg.inv(T)

    elif sensor == 2:
        T = np.mat(((a11*cos(p)+a12*sin(p), -a11*sin(p)+a12*cos(p), a13),
                    (a21*cos(p)+a22*sin(p), -a21*sin(p)+a22*cos(p), a23),
                    (a31*cos(p)+a32*sin(p), -a31*sin(p)+a32*cos(p), a33)), dtype='f')

        T_inverse = np.linalg.inv(T)
        
'''
