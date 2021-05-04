# %% imports
import numpy as np
import glm

# %% helper functions
def normalize(arr, vtype):
    return np.array((glm.normalize(vtype(arr))))

# %% camera and reference to points
points = np.zeros((2,2))
points[0,:] = [0, 2]
points[1,:] = [1, 2]

# cameras
camera_pos = np.zeros((2,2))
camera_pos[0,:] = [0,0]
camera_pos[1,:] = [1,0]

camera_vecs = np.zeros((2, 2, 2))

for c in range(len(cameras_vecs)):
    for p in range(len(points)):
        camera_vecs[c,p,:] = normalize((points[p,:] - camera_pos[c,:]), glm.vec2)


# %% build A matrix
mtx = np.zeros((4,4))
mtx[0,0] = mtx[1,2] = camera_vecs[0, 0, 0]
mtx[0,1] = mtx[1,3] = camera_vecs[0, 0, 1]
mtx[2,0] = mtx[3,2] = camera_vecs[0, 1, 0]
mtx[2,1] = mtx[3,3] = camera_vecs[0, 1, 1]

# %% build b matrix
b = np.append(camera_vecs[1,0,:], camera_vecs[1,1,:])

# %% find the transformation matrix
res = np.linalg.lstsq(mtx, b)

# %% build x matrix
x = np.zeros((2,2))
x[0,:] = res[3][0:2]
x[1,:] = res[3][2:]

# %%
