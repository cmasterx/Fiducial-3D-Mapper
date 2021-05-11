# Fiducial 3D Mapper
This software extracts translation and rotation transformations from ArUco markers to render 3D objects on top of a video source and determine distance betwen the center of the camera and the center of the marker.

Augmented Reality - extracting 
![bunny-demo](bunny.gif)
![cube-demo](cube.gif)

## Installation
### MacOS
```zsh
$ git clone https://github.com/mmatl/pyglet.git
$ cd pyglet
$ pip install .
```

### Other Platforms
```bash
$ pip install pyrender
```
## Calibration
- Camera callibration is required 
- Callibration file must be a pickled tuple (with the pickle library) with contents (_ret, intrinsic_camera_matrix, distortion_coefficients, _translation_vectors, _rotational_vectors).
    - The contents of the tuple must be in this order
    - Variables with underscore prefix will not be used by the program

## To run
`$ python3 main.py`

### Keyboard Inputs at Render Window
    q: quit
    a: toggle draw axis
    b: toggle draw box
    b: toggle draw bunny

## Sources
- Bunny OBJ: http://www.kunzhou.net/tex-models.htm
