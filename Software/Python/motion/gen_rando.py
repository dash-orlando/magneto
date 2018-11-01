"""
Generate a gcode with a random number generator

Fluvio L Lobo Fenoglietto
"""


from    paths           import *
from    gcode_gen       import *

import  numpy       as      np


# inputs
printer = np.array([150,150,150])
limits = printer/2
steps = 20                              # number of positions/iterations

position, offsets, limits, printer = random_walk( printer, limits, steps)

out_name = "rand_walk_s20_t10"
gcode_gen_3( out_name, position[:,0], position[:,1], position[:,2], offsets, 3600, 10000, 1 )
"""
# generate random multipliers
rand_multipliers = np.random.rand(3,1)

x_rm = rand_multipliers[0]              # random multiplier per axis
y_rm = rand_multipliers[1]
z_rm = rand_multipliers[2]


### function starts here ###
# determine offsets
offsets = np.zeros(3)
for i in range( 0, len(printer) ):
    offsets[i] = ( printer[i] - limits[i] )/2

# create positions
position = np.zeros((steps, 3))
for i in range( 0, steps ):

    # generate random multipliers
    rm = np.random.rand(3,1)

    # generate positions
    for j in range( 0, len(rm) ):
        position[i,j] = limits[j]*rm[j] + offsets[j]
"""
