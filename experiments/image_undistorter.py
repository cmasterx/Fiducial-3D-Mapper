# %% imports
import cv2
import pickle
import numpy as np
import glm

# %% load camera matrix
with open('../calibration.pckl', 'rb') as file:
    (_ret, mtx, dist, rvec, tvec) = pickle.load(file)

# %% new camera matrix
h, w = cv2.imread('../video/frame_10.png').shape[:2]
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))


# %% test values
points = np.zeros((20,1,2)) + w

# %% get points
new_points = cv2.undistortPoints(points, mtx, dist)
# %%
