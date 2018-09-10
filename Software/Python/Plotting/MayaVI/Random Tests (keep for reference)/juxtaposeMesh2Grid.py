from mayavi import mlab
import numpy as np
import math

mlab.figure(size=(1000, 800))

K = 251     # Number of lines to plot
N = 10       # Subdivisions (aka K/N lines are drawn)

# Draw horizontal lines on the xy-, yz-, and xz-planes
lvlCurve_H = np.arange( 0, K, N )                       # Horizontal level curve
lvlCurve_V = np.zeros_like( lvlCurve_H )                # Vertical level curve
H, V = np.meshgrid( lvlCurve_H, lvlCurve_V )            # Mesh both arrays to form a matrix (a grid)
lvlCurve_0 = np.zeros_like( H )                         # Force everything into a 2D plane by setting the 3rd plane to 0

for i in range (0, K, N):
    mlab.mesh( H, V+i, lvlCurve_0, representation='mesh',
               tube_radius = 0.25, color=(1., 1., 1.) )
    mlab.mesh( lvlCurve_0, H, V+i, representation='mesh',
               tube_radius = 0.25, color=(1., 1., 1.) )
    mlab.mesh( H, lvlCurve_0, V+i, representation='mesh',
               tube_radius = 0.25, color=(1., 1., 1.) )

# Draw vertical lines on the xy-, yz-, and xz-planes
lvlCurve_V = np.arange(0, K, N)                         # Vertical level curve
lvlCurve_H = np.zeros_like(lvlCurve_V)                  # Horizontal level curve
H, V = np.meshgrid( lvlCurve_H, lvlCurve_V )            # Mesh both arrays to form a matrix (a grid)
lvlCurve_0 = np.zeros_like( H )                         # Force everything into a 2D plane by setting the 3rd plane to 0

for i in range (0, K, N):
    mlab.mesh( H+i, V, lvlCurve_0, representation='mesh',
               tube_radius = 0.25, color=(1., 1., 1.) )
    mlab.mesh( lvlCurve_0, H+i, V, representation='mesh',
               tube_radius = 0.25, color=(1., 1., 1.) )
    mlab.mesh( H+i, lvlCurve_0, V, representation='mesh',
               tube_radius = 0.25, color=(1., 1., 1.) )
    

# Setup cartesian space
mlab.outline( extent=[0, K-1, 0, K-1, 0, K-1] )
mlab.axes( extent=[0, K-1, 0, K-1, 0, K-1],
           line_width = 1.0,
           x_axis_visibility=True,
           y_axis_visibility=True,
           z_axis_visibility=True )


STLfile="SP_PH02_Torso (ASCII).stl"
f=open(STLfile,'r')

x=[]
y=[]
z=[]

scaleFactor = 1.0
for line in f:
    strarray=line.split()
    if strarray[0]=='vertex':
        x = np.append( x, np.double(strarray[1])/scaleFactor )
        y = np.append( y, np.double(strarray[2])/scaleFactor )
        z = np.append( z, np.double(strarray[3])/scaleFactor )

# Snap to origin
##x = x + 50
##y = y + 30
##z = z - 50

# Translate mesh from origin to nipple (yay!)
x = x + (275.00)/scaleFactor
y = y - (125.00)/scaleFactor
z = z - (150.00)/scaleFactor

# Rotate STL mesh
temp = np.copy(y)
y = -1*np.copy(z)
z = temp

triangles=[(i, i+1, i+2) for i in range(0, len(x),3)]

mlab.triangular_mesh( x, y, z, triangles,
                      representation='fancymesh',
                      tube_radius=1.0 )
mlab.show()
