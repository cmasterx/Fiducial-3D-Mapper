import numpy as np
import matplotlib.pyplot as plt
import time

# set matplotlib as 3d projections
plt.ion()
fig =  plt.figure()
ax = plt.axes(projection='3d')

zline = np.linspace(0, 15, 1000)
xline = np.sin(zline)
yline = np.cos(zline)

ax.plot3D(xline, yline, zline, 'gray')
ax.plot3D([0, 1], [0,1], [0,1], 'green')

ax.scatter3D(xline, yline, zline)

time.sleep(3)
# plt.show()
