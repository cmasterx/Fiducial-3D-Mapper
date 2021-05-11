To run:
 $ python3 main.py

callibration might be required for specific camera.

When running, press the following key characters for:
    q: quit
    a: toggle draw axis
    b: toggle draw box
    b: toggle draw bunny

In the terminal, the distance from the camera to the marker will be displayed. For the
appropriate distance to work, changing "marker_size" in settings.json to the correct marker_size
of the marker.

Python libraries required:
opencv2
opencv-contrib-python
glm
numpy
trimesh
json
argparse
pyrender

If running on MacOS - pyrender must be installed manually:

    For MacOS:
    git clone https://github.com/mmatl/pyglet.git
    cd pyglet
    pip install .