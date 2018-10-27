import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as axes3d

fig = plt.figure(dpi=100)
ax = fig.add_subplot(111, projection='3d')



#data
fx = [0.673574075,0.727952994,0.6746285]
fy = [0.331657721,0.447817839,0.37733386]
fz = [18.13629648,8.620699842,9.807536512]

#error data
xerror = [0.041504064,0.02402152,0.059383144]
yerror = [0.015649804,0.12643117,0.068676131]
zerror = [3.677693713,1.345712547,0.724095592]

#plot points
ax.plot(fx, fy, fz, linestyle="None", marker="o")

#plot errorbars
for i in np.arange(0, len(fx)):
    ax.plot([fx[i]+xerror[i], fx[i]-xerror[i]], [fy[i], fy[i]], [fz[i], fz[i]], marker="_")
    ax.plot([fx[i], fx[i]], [fy[i]+yerror[i], fy[i]-yerror[i]], [fz[i], fz[i]], marker="_")
    ax.plot([fx[i], fx[i]], [fy[i], fy[i]], [fz[i]+zerror[i], fz[i]-zerror[i]], marker="_")

#configure axes
ax.set_xlim3d(0.55, 0.8)
ax.set_ylim3d(0.2, 0.5)
ax.set_zlim3d(8, 19)

plt.show()
