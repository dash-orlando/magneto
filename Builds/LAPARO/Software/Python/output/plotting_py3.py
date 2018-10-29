"""
plotting

Script developed to plot text data obtained from the LAPARO trainer

--Python 3 support

"""

# ============== #
# Import Modules
# ============== #
from    mpl_toolkits.mplot3d    import Axes3D
import  matplotlib.pyplot       as plt
import  numpy                   as np



# variables
filename = "10-26-18_15-1-49.txt"

# ========================================================================= #
# import data from text file
# ========================================================================= #
xm          = []
ym          = []
zm          = []
xe          = []
ye          = []
ze          = []
length      = []
sol_time    = []
#prog_time   = []

with open( filename, 'r' ) as file:
    for line in file:
        line = line.strip( '\n' ).split(',')
        xm.append(          float( line[0] ) )
        ym.append(          float( line[1] ) )
        zm.append(          float( line[2] ) )
        xe.append(          float( line[3] ) )
        ye.append(          float( line[4] ) )
        ze.append(          float( line[5] ) )
        length.append(      float( line[6] ) )
        sol_time.append(    float( line[7] ) )
        #prog_time.append(   line[8] )



# ========================================================================= #
# Data processing, statistics
# ========================================================================= #
# Data for three-dimensional scattered points
## position limits
pos   = [(160,     263),
         (276,     387),
         (407,     515),
         (532,     643),
         (662,     769),
         (784,     897),
         (908,     1026),
         (1041,    1153),
         (1160,    1280),
         (1291,    1415)]

Npos = len(pos)

# statistics
xm_mean = []
ym_mean = []
zm_mean = []
xe_mean = []
ye_mean = []
ze_mean = []
xm_std  = []
ym_std  = []
zm_std  = []
xe_std  = []
ye_std  = []
ze_std  = []
xm_se   = []
ym_se   = []
zm_se   = []
xe_se   = []
ye_se   = []
ze_se   = []


for i in range( 0, Npos ):
    data_len = pos[i][1]-pos[i][0]                                          # number of data points (n)

    # means
    ## magnet
    xm_mean.append( np.mean( xm[pos[i][0]:pos[i][1]] )  )
    ym_mean.append( np.mean( ym[pos[i][0]:pos[i][1]] )  )
    zm_mean.append( np.mean( zm[pos[i][0]:pos[i][1]] )  )
    ## end effector
    xe_mean.append( np.mean( xe[pos[i][0]:pos[i][1]] )  )
    ye_mean.append( np.mean( ye[pos[i][0]:pos[i][1]] )  )
    ze_mean.append( np.mean( ze[pos[i][0]:pos[i][1]] )  )

    # std
    ## magnet
    xm_std.append(  np.std( xm[pos[i][0]:pos[i][1]] )   )
    ym_std.append(  np.std( ym[pos[i][0]:pos[i][1]] )   )
    zm_std.append(  np.std( zm[pos[i][0]:pos[i][1]] )   )
    ## end effector
    xe_std.append(  np.std( xe[pos[i][0]:pos[i][1]] )   )
    ye_std.append(  np.std( ye[pos[i][0]:pos[i][1]] )   )
    ze_std.append(  np.std( ze[pos[i][0]:pos[i][1]] )   )

    # se
    ## magnet
    xm_se.append(   xm_std[i] / np.sqrt( data_len )     )
    ym_se.append(   ym_std[i] / np.sqrt( data_len )     )
    zm_se.append(   zm_std[i] / np.sqrt( data_len )     )
    ## end effector
    xe_se.append(   xe_std[i] / np.sqrt( data_len )     )
    ye_se.append(   ye_std[i] / np.sqrt( data_len )     )
    ze_se.append(   ze_std[i] / np.sqrt( data_len )     )

# ========================================================================= #
# plotting
# ========================================================================= #

## raw data plot
ax1 = plt.axes(projection='3d')

# Data for a three-dimensional line
#zline = np.linspace(0, 15, 1000)
#xline = np.sin(zline)
#yline = np.cos(zline)
#ax.plot3D(xline, yline, zline, 'gray')

for i in range( 0, Npos ):

    # magnet position
    ax1.scatter3D(xm[pos[i][0]:pos[i][1]],
                  ym[pos[i][0]:pos[i][1]],
                  zm[pos[i][0]:pos[i][1]],
                  c=zm[pos[i][0]:pos[i][1]],
                  cmap='Greens')

    # end-effector position
    ax1.scatter3D(xe[pos[i][0]:pos[i][1]],
                  ye[pos[i][0]:pos[i][1]],
                  ze[pos[i][0]:pos[i][1]],
                  c=ze[pos[i][0]:pos[i][1]],
                  cmap='Reds')


#ax.legend()
ax1.set_xlim(-150, 150)
ax1.set_ylim(-150, 150)
ax1.set_zlim(-250, 250)
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Z')
plt.show()

## stats
ax2 = plt.axes(projection='3d')

# Data for a three-dimensional line
#zline = np.linspace(0, 15, 1000)
#xline = np.sin(zline)
#yline = np.cos(zline)
#ax.plot3D(xline, yline, zline, 'gray')

for i in range( 0, Npos ):

    # magnet position
    ax2.scatter3D(xm_mean[i],
                  ym_mean[i],
                  zm_mean[i],
                  color='Blue')

    # end-effector position
    ax2.scatter3D(xe_mean[i],
                  ye_mean[i],
                  ze_mean[i],
                  color='Red')


#ax.legend()
ax2.set_xlim(-150, 150)
ax2.set_ylim(-150, 150)
ax2.set_zlim(-250, 250)
ax2.set_xlabel('X')
ax2.set_ylabel('Y')
ax2.set_zlabel('Z')
plt.show()
