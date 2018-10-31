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

### ========================================================================= #
#### raw data plot
### ========================================================================= #
##ax1 = plt.axes(projection='3d')
##
### Data for a three-dimensional line
###zline = np.linspace(0, 15, 1000)
###xline = np.sin(zline)
###yline = np.cos(zline)
###ax.plot3D(xline, yline, zline, 'gray')
##
##for i in range( 0, Npos ):
##
##    # magnet position
##    ax1.scatter3D(xm[pos[i][0]:pos[i][1]],
##                  ym[pos[i][0]:pos[i][1]],
##                  zm[pos[i][0]:pos[i][1]],
##                  c=zm[pos[i][0]:pos[i][1]],
##                  cmap='Greens')
##
##    # end-effector position
##    ax1.scatter3D(xe[pos[i][0]:pos[i][1]],
##                  ye[pos[i][0]:pos[i][1]],
##                  ze[pos[i][0]:pos[i][1]],
##                  c=ze[pos[i][0]:pos[i][1]],
##                  cmap='Reds')
##
##
###ax.legend()
##ax1.set_xlim(-150, 150)
##ax1.set_ylim(-150, 150)
##ax1.set_zlim(-250, 250)
##ax1.set_xlabel('X')
##ax1.set_ylabel('Y')
##ax1.set_zlabel('Z')
##plt.show()

### ========================================================================= #
#### stats
### ========================================================================= #
##ax2 = plt.axes(projection='3d')
##
### Data for a three-dimensional line
###zline = np.linspace(0, 15, 1000)
###xline = np.sin(zline)
###yline = np.cos(zline)
###ax.plot3D(xline, yline, zline, 'gray')
##
##for i in range( 0, Npos ):
##
##    # magnet position
##    ax2.scatter3D(xm_mean[i],
##                  ym_mean[i],
##                  zm_mean[i],
##                  color='Blue')
##    
##    # magnet position error bars
##    ax2.plot([xm_mean[i]+xm_se[i]*100, xm_mean[i]-xm_se[i]*100],
##             [ym_mean[i], ym_mean[i]],
##             [zm_mean[i], zm_mean[i]],
##             marker="_",
##             color='Black')
##    
##    ax2.plot([xm_mean[i], xm_mean[i]],
##             [ym_mean[i]+ym_se[i]*100, ym_mean[i]-ym_se[i]*100],
##             [zm_mean[i], zm_mean[i]],
##             marker="_",
##             color='Black')
##    
##    ax2.plot([xm_mean[i], xm_mean[i]],
##             [ym_mean[i], ym_mean[i]],
##             [zm_mean[i]+zm_se[i]*100, zm_mean[i]-zm_se[i]*100],
##             marker="_",
##             color='Black')
##
##    # end-effector position
##    ax2.scatter3D(xe_mean[i],
##                  ye_mean[i],
##                  ze_mean[i],
##                  color='Red')
##
##    # end-effector position error bars
##    ax2.plot([xe_mean[i]+xe_se[i]*100, xe_mean[i]-xe_se[i]*100],
##             [ye_mean[i], ye_mean[i]],
##             [ze_mean[i], ze_mean[i]],
##             marker="_",
##             color='Black')
##    
##    ax2.plot([xe_mean[i], xe_mean[i]],
##             [ye_mean[i]+ye_se[i]*100, ye_mean[i]-ye_se[i]*100],
##             [ze_mean[i], ze_mean[i]],
##             marker="_",
##             color='Black')
##    
##    ax2.plot([xe_mean[i], xe_mean[i]],
##             [ye_mean[i], ye_mean[i]],
##             [ze_mean[i]+ze_se[i]*100, ze_mean[i]-ze_se[i]*100],
##             marker="_",
##             color='Black')
##
##
###ax.legend()
##ax2.set_xlim(-150, 150)
##ax2.set_ylim(-150, 150)
##ax2.set_zlim(-250, 250)
##ax2.set_xlabel('X')
##ax2.set_ylabel('Y')
##ax2.set_zlabel('Z')
##plt.show()

# ========================================================================= #
## other
# ========================================================================= #
actual_pos = [(20.00, -85.00, -165.00),
              (26.00, 95.00, -212.80),
              (85.00, 37.00, -129.80),
              (55.75, 74.50, -231.80),
              (-37.50, -36.00, -199.80),
              (-86.00, -90.00, -231.80),
              (-126.50, -8.00, -231.80),
              (-82.50, 27.50, -212.80),
              (-79.00, 46.00, -212.80),
              (-66.50, 60.50, -212.80)]

ax1 = plt.axes(projection='3d')

# Data for a three-dimensional line
#zline = np.linspace(0, 15, 1000)
#xline = np.sin(zline)
#yline = np.cos(zline)
#ax.plot3D(xline, yline, zline, 'gray')

for i in range( 0, Npos ):

    # magnet position
    ax1.scatter3D(actual_pos[i][0],
                  actual_pos[i][1],
                  actual_pos[i][2],
                  color='Blue')

    # end-effector position
    ax1.scatter3D(xe[pos[i][0]:pos[i][1]],
                  ye[pos[i][0]:pos[i][1]],
                  ze[pos[i][0]:pos[i][1]],
                  color='Red')


#ax.legend()
ax1.set_xlim(-150, 150)
ax1.set_ylim(-150, 150)
ax1.set_zlim(-250, 250)
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Z')
plt.show()


# ========================================================================= #
## flat subplots
# ========================================================================= #
actual_pos = [(20.00, -85.00, -165.00),
              (26.00, 95.00, -212.80),
              (85.00, 37.00, -129.80),
              (55.75, 74.50, -231.80),
              (-37.50, -36.00, -199.80),
              (-86.00, -90.00, -231.80),
              (-126.50, -8.00, -231.80),
              (-82.50, 27.50, -212.80),
              (-79.00, 46.00, -212.80),
              (-66.50, 60.50, -212.80)]

for i in range( 0, Npos ):

    # magnet position
    magpos = plt.scatter(actual_pos[i][0],
                         actual_pos[i][1],
                         color='Blue')

    # end-effector position
    endeff = plt.scatter(xe[pos[i][0]:pos[i][1]],
                         ye[pos[i][0]:pos[i][1]],
                         color='Red')


# ref circle, magnet
rmcx = [100]
rmcy = [-100]
rm   = [800]
refmag = plt.scatter(rmcx, rmcy, s=rm, color='black', edgecolor='black')

# ref circle, end effector
recx = [100]
recy = [-100]
re   = [100]

refeff = plt.scatter(recx, recy, s=re, color='white', edgecolor='black')

#ax.legend()
##plt.set_xlim(-150, 150)
##a.set_ylim(-150, 150)
##ax1.set_zlim(-250, 250)
##ax1.set_xlabel('X')
##ax1.set_ylabel('Y')
##ax1.set_zlabel('Z')
ticks = np.linspace(-150, 150, num=int(300/25 + 1), endpoint=True)
plt.xticks(ticks, fontsize=9)
plt.yticks(ticks, fontsize=9)
plt.xlabel('X (mm)')
plt.ylabel('Y (mm)')
plt.legend((magpos, endeff, refmag, refeff),
           ("Magnet Position","End-Effector Position","Magnet Ref. Size","End Effector Ref. Size"),
           labelspacing=1.5,
           #ncol=4,
           fontsize=10,
           framealpha=1,
           shadow=True,
           borderpad=1,
           loc=1)
plt.grid()
plt.show()
