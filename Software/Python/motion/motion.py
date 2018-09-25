"""
Motion Test Script

Script designed to generate GCODE for a given 3D path

Fluvio L Lobo Fenoglietto
"""

def gcode_gen( out_name, x, y, z ):
    """
    Given a 3D path described by its coordinates in x, y, and z,
    the function generates a GCODE
    """
    array_len = len(x)                                                          # len(y) or len(z)
    ext = ".gcode"
    file_name = out_name + ext
    file = open( file_name, "w" )
    
    for i in range(0, 10):                                                      # write all the data from the data arrays
        print( 'X{0:.2f} Y{0:.2f} Z{0:.2f}\n'.format(x[i], y[i], z[i]))
        file.write( 'X{0:.2f} Y{0:.2f} Z{0:.2f}\n'.format(x[i], y[i], z[i]))

    file.close()
