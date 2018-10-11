"""
Generate a gcode with a random number generator

Fluvio L Lobo Fenoglietto
"""


from    paths       import rando
from    motion      import *

import  numpy       as      np


# inputs
printer = np.array([300,300,400])
limits = printer/2
steps = 20                              # number of positions/iterations

# generate random multipliers
rand_multipliers = np.random.rand(3,1)

x_rm = rand_multipliers[0]              # random multiplier per axis
y_rm = rand_multipliers[1]
z_rm = rand_multipliers[2]

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

