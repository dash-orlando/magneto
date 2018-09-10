##from __future__   import absolute_import, division, print_function
from    mayavi      import  mlab
import  numpy       as      np
import  math

# ======================================================================= #
# ====================== FLOATING BOX FIELD STUFF ======================= #
# ======================================================================= #
##### Make the data (aka box of scatter points that float around to define our space)
####dims    =   np.array((128, 128, 128))
####vol     =   np.array((0., 6, 0, 6, 0, 6))
####origin  =   vol[::2]
####spacing =  (vol[1::2] - origin)/(dims -1)
####xmin, xmax, ymin, ymax, zmin, zmax = vol
####x, y, z = np.ogrid[ xmin:xmax:dims[0]*1j,
####                    ymin:ymax:dims[1]*1j,
####                    zmin:zmax:dims[2]*1j ]
####x, y, z = [t.astype('f') for t in (x, y, z)]
####x = x.flatten()
####y = y.flatten()
####z = z.flatten()
####scalars = (x*y*z)
####
####mlab.points3d(x, y, z)
####mlab.show()

##K = 11
##xx = np.arange(0, K, 1)
##yy = np.arange(0, K, 1)
##
##x, y = np.meshgrid(xx, yy)
##x, y = x.flatten(), y.flatten()
##z = np.zeros(K*K)
##
##colors = 1.0 * (x + y)/(max(x)+max(y))    # Rainbow color
####colors = 0.0 * (x + y)/(max(x)+max(y))      # Dark blue color
##
##nodes = mlab.points3d(x, y, z, opacity=0.1, scale_factor=0.5)
##nodes.glyph.scale_mode = 'scale_by_vector'
##nodes.mlab_source.dataset.point_data.scalars = colors
##
##for i in range( K ):
##    nodes = mlab.points3d(x, y, z+i, opacity=0.1, scale_factor=0.5)
##    nodes.glyph.scale_mode = 'scale_by_vector'
##    nodes.mlab_source.dataset.point_data.scalars = colors
##
##mlab.outline(extent=[0, 10, 0, 10, 0, 10])
##mlab.axes( extent=[0, 10, 0, 10, 0, 10],
##           line_width = 1.0,
##           x_axis_visibility=True,
##           y_axis_visibility=True,
##           z_axis_visibility=True )


# ======================================================================= #
# ======================================================================= #
# ======================================================================= #

K = 101

# Level curves to draw horizontal lines on the xy-plane
lvlCurve_H = np.arange(0, K, 5)                     # Horizontal level curve for y=cte
lvlCurve_V = np.zeros_like(lvlCurve_H)              # Vertical level curve for x=cte
H, V = np.meshgrid(lvlCurve_H, lvlCurve_V)
H, V = H.flatten(), V.flatten()
lvlCurve_0 = np.zeros_like(H)                          # Force everything into the xy-plane (z=0)

for i in range (0, K, 5):
    mlab.plot3d( H, V+i, lvlCurve_0 )

# Level curves to draw vertical lines on the xy-plane
lvlCurve_V = np.arange(0, K, 5)
lvlCurve_H = np.zeros_like(lvlCurve_V)
H, V = np.meshgrid(lvlCurve_H, lvlCurve_V)
H, V = H.flatten(), V.flatten()
lvlCurve_0 = np.zeros_like(H)                          # Force everything into the xy-plane (z=0)

for i in range (0, K, 5):
    mlab.plot3d( H+i, V, lvlCurve_0 )

# Level curves to draw horizontal lines on the yz-plane
lvlCurve_H = np.arange(0, K, 5)                     # Horizontal level curve for y=cte
lvlCurve_V = np.zeros_like(lvlCurve_H)              # Vertical level curve for x=cte
H, V = np.meshgrid(lvlCurve_H, lvlCurve_V)
H, V = H.flatten(), V.flatten()
lvlCurve_0 = np.zeros_like(H)                          # Force everything into the xy-plane (z=0)

for i in range (0, K, 5):
    mlab.plot3d( lvlCurve_0, H, V+i )

# Level curves to draw vertical lines on the yz-plane
lvlCurve_V = np.arange(0, K, 5)
lvlCurve_H = np.zeros_like(lvlCurve_V)
H, V = np.meshgrid(lvlCurve_H, lvlCurve_V)
H, V = H.flatten(), V.flatten()
lvlCurve_0 = np.zeros_like(H)                          # Force everything into the xy-plane (z=0)

for i in range (0, K, 5):
    mlab.plot3d( lvlCurve_0, H+i, V )

# Level curves to draw horizontal lines on the xz-plane
lvlCurve_H = np.arange(0, K, 5)                     # Horizontal level curve for y=cte
lvlCurve_V = np.zeros_like(lvlCurve_H)              # Vertical level curve for x=cte
H, V = np.meshgrid(lvlCurve_H, lvlCurve_V)
H, V = H.flatten(), V.flatten()
lvlCurve_0 = np.zeros_like(H)                          # Force everything into the xy-plane (z=0)

for i in range (0, K, 5):
    mlab.plot3d( H, lvlCurve_0, V+i )

# Level curves to draw vertical lines on the xz-plane
lvlCurve_V = np.arange(0, K, 5)
lvlCurve_H = np.zeros_like(lvlCurve_V)
H, V = np.meshgrid(lvlCurve_H, lvlCurve_V)
H, V = H.flatten(), V.flatten()
##lvlCurve_0 = np.zeros(K*K)          # Force everything into the xy-plane (z=0)
lvlCurve_0 = np.zeros_like(H)                          # Force everything into the xy-plane (z=0)

for i in range (0, K, 5):
    mlab.plot3d( H+i, lvlCurve_0, V )

# Setup cartesian space
mlab.outline( extent=[0, K-1, 0, K-1, 0, K-1] )
mlab.axes( extent=[0, K-1, 0, K-1, 0, K-1],
           line_width = 1.0,
           x_axis_visibility=True,
           y_axis_visibility=True,
           z_axis_visibility=True )
  
##mlab.show()

# ======================================================================= #
# ======================================================================= #
# ======================================================================= #

# -------------------------------------------------------------------------

# ======================================================================= #
# ======================= ORBITING STUFF ANIMATION ====================== #
# ======================================================================= #
alpha = np.linspace(0, 2*math.pi, 100)  

xs = 10.*np.cos(alpha)+50
ys = 10.*np.sin(alpha)+50
zs = np.zeros_like(xs)+50
s  = 2+np.sin(alpha) 
mlab.points3d( 50, 50, 50, resolution=100, scale_factor=10.0 )
##mlab.outline(extent=[0, 10, 0, 10, 0, 10])
##mlab.axes( extent=[0, 10, 0, 10, 0, 10],
##           line_width = 1.0,
##           x_axis_visibility=True,
##           y_axis_visibility=True,
##           z_axis_visibility=True )

plt = mlab.points3d(xs[:1], ys[:1], zs[:1], resolution=100, scale_factor=10.0)

@mlab.animate(delay=25)
def anim():
    f = mlab.gcf()
    while True:
        for (x, y, z) in zip(xs, ys, zs):
            print('Updating scene...')
            plt.mlab_source.set(x=x, y=y, z=z)
            yield

anim()
mlab.show()
# ======================================================================= #
# ======================================================================= #
# ======================================================================= #
