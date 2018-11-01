"""
Paths

Module containing 3D functions generating 3D paths

Fluvio L Lobo Fenoglietto
"""

"""
Import Modules and Libraries
"""
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt



def helix():
    """
    Generates a default parametric helix obtained from the matplotlib examples
    """

    mpl.rcParams['legend.fontsize'] = 10
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    theta = np.linspace(0, 2*np.pi, 100)
    z = np.linspace(0, 1, 100)
    r = z + 1
    x = r * np.sin(theta)
    y = r * np.cos(theta)
    ax.plot(x, y, z, label='parametric curve')
    ax.legend()
    plt.show()
    
    return x, y, z, r, theta

def unit_helix():
    """
    Generates a unit helix
    """

    mpl.rcParams['legend.fontsize'] = 10
    fig = plt.figure()
    ax = fig.gca(projection='3d')


    t = np.linspace(0, 1, 1000)
    #z = np.linspace(0, 1, 100)
    #r = z + 1
    x = np.cos(t)
    y = np.sin(t)
    ax.plot(x, y, t, label='parametric curve')
    ax.legend()
    plt.show()
    
    return x, y, t

def prog_helix( max_x, max_y, max_z ):
    """
    Generates a helix based on the maximum ranges in x, y, and z, given by;
        x --> ( -max_x, max_x )
        y --> ( -max_y, max_y )
        z --> (      0, max_z )
    """

    mpl.rcParams['legend.fontsize'] = 10
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    z = np.linspace(0, max_z, 5000)
    x = max_x*np.cos(z)
    y = max_y*np.sin(z)
    ax.plot(x, y, z, label='parametric curve')
    ax.legend()
    plt.show()
    
    return x, y, z 


def random_walk( printer, limits, steps):
    """
    Generates a random motion based on the printer volume and input limits
    Movements are differentiated by a time interval

        printer   --> Print volume of the printer (x_max, y_max, z_max)
        limits    --> Maximum travel for the random walk (x_limit, y_limit, z_limit)
        steps     --> Number of random steps to be calculated
        intervals --> Time pause between positions
    """

    # generate random multipliers
    rand_multipliers = np.random.rand(3,1)
    x_rm = rand_multipliers[0]                                                          # random multiplier per axis
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

    #return
    return position, offsets, limits, printer
    
def random_cwalk( printer, limits, steps):
    """
    Generates a random motion based on the printer volume and input limits
    Movements are differentiated by a time interval
    Movements are relative to the center of the build plate

        printer   --> Print volume of the printer (x_max, y_max, z_max)
        limits    --> Maximum travel for the random walk (x_limit, y_limit, z_limit)
        steps     --> Number of random steps to be calculated
        intervals --> Time pause between positions
    """

    # generate random multipliers
    rand_multipliers = np.random.rand(3,1)
    x_rm = rand_multipliers[0]                                                          # random multiplier per axis
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

    #return
    return position, offsets, limits, printer    
    
