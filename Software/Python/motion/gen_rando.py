"""
Generate a gcode with a random number generator

Fluvio L Lobo Fenoglietto
"""


from    paths           import *
from    gcode_gen       import *

import  numpy       as      np


# inputs
holder_offset = np.array([2.50, 60.00, 0])
printer = np.array([150,150,75]) + holder_offset
climits = printer/3
steps = 20                              # number of positions/iterations

position, climits, printer = random_cwalkwr( printer,
                                           climits,
                                           steps )


gcode_gen_cwalk( 'cwalkwr_test_2z75',
                 position[:,0],
                 position[:,1],
                 position[:,2],
                 printer,
                 3600,
                 5000,
                 1 )

