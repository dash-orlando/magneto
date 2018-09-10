"""
To read a STL file and plot in mayavi
First created by Junwei Huang @ Toronto, Feb 26, 2013
"""

import numpy as np
from mayavi import mlab

STLfile="SP_PH02_Torso (ASCII).stl"
f=open(STLfile,'r')

x=[]
y=[]
z=[]

for line in f:
    strarray=line.split()
    if strarray[0]=='vertex':
        x = np.append( x, np.double(strarray[1]) )
        y = np.append( y, np.double(strarray[2]) )
        z = np.append( z, np.double(strarray[3]) )

triangles=[(i, i+1, i+2) for i in range(0, len(x),3)]

mlab.triangular_mesh(x, y, z, triangles)
mlab.show()
