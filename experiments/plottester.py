# %% imports
import glm
import numpy as np
import plotupdater3d as pl3d

# %% create variables
mx = glm.translate(glm.mat4(), (0,0,100))
lines = np.random.rand(4, 2, 3) * 10

# %% generate copy matrix
copy = pl3d.apply_matrix(lines, 1, mx)

# %% print original lines
print(lines)

# %% print copy matrix
print(copy)
