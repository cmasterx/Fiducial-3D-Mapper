# does not work

import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
import glm

def apply_matrix(lines, idx, matrix):
    """
    Apply matrix transformation to a line at point idx
    """
    copy = lines
    for i, line in enumerate(lines):
        copy[i, idx, :] = np.array(matrix * glm.vec4(np.append(line[idx, :], 1.0)))[0:3]
    
    return copy
    
def main():
    X = np.random.rand(100, 3)*10
    Y = np.random.rand(100, 3)*5

    plt.ion()

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # sc = ax.scatter(X[:, 0], X[:, 1], X[:, 2])

    MV = glm.identity(glm.mat4)
    MV = glm.translate(MV, (0,0,2))

    lines = np.zeros(shape=(4, 2, 3))
    lines[:, 0, :] = 0  # set origin of points to 0
    lines[0, 1, :] = [-1,  1, 0]
    lines[1, 1, :] = [ 1,  1, 0]
    lines[2, 1, :] = [ 1, -1, 0]
    lines[3, 1, :] = [-1, -1, 0]

    lines = apply_matrix(lines, 1, MV)
    
    sc = [ ax.plot(line[:,0], line[:,1], line[:,2]) for line in lines]
    fig.canvas.draw()
    # plt.show()
    alpha = 0.5

    fig.canvas.draw_idle()
    # time.sleep(20)
    for phase in np.linspace(0, 10*np.pi, 500):
        # plt.pause(1) 
        
        translation = glm.translate(glm.mat4(), (alpha * np.cos(phase), alpha * np.sin(phase), 0.0))
        to_show = apply_matrix(lines, 1, translation)
        
        for i, s in enumerate(sc):
            print(s)
            # time.sleep(1)
            # s[0].set_data(lines[i, :, 0], lines[i, :, 1])
            # s._offsets3d=(lines[i, :, 0], lines[i, :, 1], lines[i, :, 2])

        # s._offsets3d = (lines)
        # fig.canvas.draw()
        # fig.canvas.flush_events()
        # plt.draw()
        # time.sleep(0.01)

if '__main__' in __name__:
    main()