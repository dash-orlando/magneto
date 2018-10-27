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


# import data from text file
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


# plotting

ax = plt.axes(projection='3d')

# Data for a three-dimensional line
#zline = np.linspace(0, 15, 1000)
#xline = np.sin(zline)
#yline = np.cos(zline)
#ax.plot3D(xline, yline, zline, 'gray')

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
for i in range( 0, Npos ):

    # magnet position
    ax.scatter3D(xm[pos[i][0]:pos[i][1]],
                 ym[pos[i][0]:pos[i][1]],
                 zm[pos[i][0]:pos[i][1]],
                 c=zm[pos[i][0]:pos[i][1]],
                 cmap='Greens')

    # end-effector position
    ax.scatter3D(xe[pos[i][0]:pos[i][1]],
                 ye[pos[i][0]:pos[i][1]],
                 ze[pos[i][0]:pos[i][1]],
                 c=ze[pos[i][0]:pos[i][1]],
                 cmap='Reds')

#ax.legend()
ax.set_xlim(-150, 150)
ax.set_ylim(-150, 150)
ax.set_zlim(-250, 250)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.show()

