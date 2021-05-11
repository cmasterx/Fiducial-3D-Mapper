import os
import pickle
import cv2
from numpy.lib.type_check import _real_dispatcher
from trimesh.visual import color
import cv2.aruco as aruco
import glm
import numpy as np
import matplotlib.pyplot as plt
import trimesh
import pyrender
import json
import sys
import argparse
from ipcamera import IPCamera

# import cv2.aruco as aruco

def mat4topy4(mat:glm.mat4) -> np.array:
    n = np.eye(4)

    for r in range(4):
        for c in range(4):
            n[r,c] = mat[c,r]
    return n
    
def py4tomat4(mat:np.array) -> glm.mat4:
    n = glm.mat4()

    for r in range(4):
        for c in range(4):
            n[c,r] = mat[r,c]
    return n

def draw_cube_img(img, marker_length, int_mtx, ext_mtx):
    half_length = marker_length / 2
    cam_mtx = np.matmul(int_mtx, ext_mtx)

    lines_3D = []
    colors = []
    thicknesses = []

    # vertical lines
    lines_3D.append([(-half_length,  half_length, 0), (-half_length,  half_length, marker_length)])
    lines_3D.append([( half_length,  half_length, 0), ( half_length,  half_length, marker_length)])
    lines_3D.append([( half_length, -half_length, 0), ( half_length, -half_length, marker_length)])
    lines_3D.append([(-half_length, -half_length, 0), (-half_length, -half_length, marker_length)])

    # blue lines with thickness of 3
    for i in range(4):
        colors.append((255,0,0))
        thicknesses.append(3)

    # horizontal lines
    lines_3D.append([(-half_length,  half_length, marker_length), ( half_length,  half_length, marker_length)])
    lines_3D.append([( half_length,  half_length, marker_length), ( half_length, -half_length, marker_length)])
    lines_3D.append([( half_length, -half_length, marker_length), (-half_length, -half_length, marker_length)])
    lines_3D.append([(-half_length, -half_length, marker_length), (-half_length,  half_length, marker_length)])

    # green lines with thickness of 3
    for i in range(4):
        colors.append((0,255,0))
        thicknesses.append(3)


    lines_2D = []
    for line in lines_3D:

        single_line_2D = []
        for point in line:
            point = np.matmul(cam_mtx, np.append(point, [1]))
            single_line_2D.append((int(point[0] / point[2]), int(point[1] / point[2])))
        
        lines_2D.append(single_line_2D)
    
    for i, line in enumerate(lines_2D):
        cv2.line(img, line[0], line[1], colors[i], thicknesses[i])
    
def main(cap, cameraMatrix, distCoeffs, fps, marker_size, marker_units, flipFeed=False):

    # default parameters of AruCo
    ARUCO_PARAMS = aruco.DetectorParameters_create()
    ARUCO_DICT = aruco.Dictionary_get(aruco.DICT_6X6_250)

    # initialization
    last_text = ""

    # MODEL_MTX = np.array(glm.rotate(glm.mat4(), glm.radians(90), (1, 0, 0)))

    # FLAGS
    draw_axis = False
    draw_bunny = True
    draw_lines = False
    draw_cube = False
    record = False
    was_recording = False
    
    # 3D renderer
    ## scene
    scene = pyrender.Scene(bg_color=(0,0,0,0))

    ### OTHER
    camera_pose = glm.mat4()
    camera_pose = glm.translate(camera_pose, glm.vec3(0.0, 0.0, 0))
    camera_pose = np.array(camera_pose)

    # lighting
    light_pose = glm.translate(camera_pose, glm.vec3(0.0, 3.0, 3.0))
    light_pose = np.array(light_pose)

    ## pyrender camera
    pyrender_cam = pyrender.IntrinsicsCamera(cameraMatrix[0,0], cameraMatrix[1,1], cameraMatrix[0,2], cameraMatrix[1,2])
    camera_mat = np.eye(4) # 4x4 identity matrix
    camera_mat[2,3] = 0
    pyrender_camera_node = pyrender.Node(camera=pyrender_cam, matrix=np.eye(4))
    scene.add_node(pyrender_camera_node)
    scene.set_pose(pyrender_camera_node, camera_pose)
    
    ## mesh
    # trimesh_bunny = trimesh.load('./models/bunny.obj')
    # bunny_mesh = pyrender.Mesh.from_trimesh(trimesh_bunny)
    # bunny_mat = np.matmul(MODEL_MTX, glm.scale(glm.mat4(), glm.vec3(1 / max(bunny_mesh.extents))))  # scale bunny to max dimension 1.0 and rotate on x axis

    # bunny_pose = glm.mat4()
    # bunny_pose = glm.scale(bunny_pose, glm.vec3(1.0 / max(bunny_mesh.extents) / 10000))
    # print(max(bunny_mesh.extents))
    # bunny_pose = glm.translate(bunny_pose, glm.vec3(0,0, -100))
    # bunny_pose = np.array(bunny_pose)
    
    # bunny_node = pyrender.Node(mesh=bunny_mesh, matrix=bunny_pose)
    # scene.add_node(bunny_node)

    # ## lighting
    # light_cam = pyrender.PointLight((255, 245, 182), intensity=30000.0)
    # light_mtx = light_mtx = glm.translate(glm.mat4(py4tomat4(camera_mat)), glm.vec3(0.0, 3.0, 3.0))
    # light_mtx = np.array(light_mtx)
    # light_cam_node = pyrender.Node(light=light_cam, matrix=light_pose)
    # scene.add_node(light_cam_node)

    ## mesh
    ### bunny
    bunny_trimesh = trimesh.load('./models/bunny.obj')
    bunny_mesh = pyrender.Mesh.from_trimesh(bunny_trimesh)
    bunny_node = pyrender.Node(mesh=bunny_mesh, matrix=np.eye(4))
    scene.add_node(bunny_node)
    bunny_mtx = glm.mat4()
    bunny_mtx = glm.scale(bunny_mtx, glm.vec3(2.0 / np.max(bunny_mesh.extents)))
    bunny_mtx = glm.rotate(bunny_mtx, glm.radians(90), glm.vec3(1,0,0))
    bunny_mtx = glm.rotate(bunny_mtx, glm.radians(180), glm.vec3(0,0,1))
    bunny_mtx = glm.rotate(bunny_mtx, glm.radians(180), glm.vec3(0,1,0))
    # translate bunny above the surface
    # _yfactor = 2 * bunny_mesh.extents[1] / np.max(bunny_mesh.extents) / 2
    _yfactor = 300
    bunny_mtx = glm.translate(bunny_mtx, glm.vec3(0, _yfactor, -10.0))
    bunny_mtx = np.array(bunny_mtx)
    # bunny_node.scale *= 0.01
    scene.set_pose(bunny_node, pose=bunny_mtx)

    ### ground
    # pyrender.Mesh.from_points()

    ## lighting
    light = pyrender.PointLight((255, 245, 182), intensity=500)
    light_mtx = glm.translate(camera_pose, glm.vec3(0.0, 3.0, 3.0))
    light_mtx = np.array(light_mtx)
    scene.add(light, pose=light_mtx)

    ## get off-screen renderer
    _ret, _tmp_img = cap.read()
    w, h = _tmp_img.shape[1], _tmp_img.shape[0]
    renderer = pyrender.OffscreenRenderer(w,h)
    # viewer = pyrender.Viewer(scene)       # 3D viewer of scene

    # Video Writer
    video_writer = None
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    cam_dimensions = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    cam_fps = cap.get(cv2.CAP_PROP_FRAME_COUNT) if fps is None else fps
    if cam_fps < 0:
        # cannot obtain camera fps, so default to 30 fps
        cam_fps = 30

    while cap.isOpened():
        # while video feed is available
        
        # get frame from video feed
        ret, frame = cap.read()
        
        if ret:
            img_draw = frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # marker detection
            corners, ids, rejectedPoints = aruco.detectMarkers(gray, ARUCO_DICT, parameters=ARUCO_PARAMS)

            if ids is not None:
                # marker is detected


                img_draw = aruco.drawDetectedMarkers(img_draw, corners, borderColor=(0, 0, 255))
                rvec, tvec, _objPoints = aruco.estimatePoseSingleMarkers(corners, marker_size, cameraMatrix, distCoeffs)
                rvec_corrected = np.copy(rvec[0,0])
                rvec_corrected[1] *= -1
                rvec_corrected[2] *= -1
                
                # create extrinsic matrix
                rvec_mat, _ = cv2.Rodrigues(rvec_corrected)

                # print(rvec_mat)
                ext_mtx = np.zeros((3,4))
                ext_mtx[0:3,0:3] = rvec_mat
                ext_mtx[0:3,3] = tvec[0,0]
                # ext_mtx[0:3, 0:4] = np.column_stack((rvec_mat, np.array(tvec[0,0])))
                
                # relative matrix
                rel_mtx = np.zeros((3,4))
                _rel_mat, _ = cv2.Rodrigues(rvec[0,0])
                rel_mtx[0:3,0:3] = _rel_mat
                rel_mtx[0:3,3] = tvec[0,0]
                # ext_mtx[0:3, 0:4] = np.colu
                
                # new_bunny_mtx = np.matmul(ext_mtx, np.eye(4))
                # scene.set_pose(bunny_node, new_bunny_mtx)
                # scene.set_pose(bunny_node, np.array(glm.translate(glm.mat4(), glm.vec3(0.0, 0.0, 1))))
                
                if draw_bunny:
                    # draws bunny

                    # generate translation and rotation matrices from rvecs and tvecs
                    translate_factor = glm.translate(glm.mat4(), glm.vec3(tvec[0,0][0], -tvec[0,0][1], -tvec[0,0][2]))
                    rotate_factor = np.eye(4)
                    rotate_factor[0:3,0:3] = rvec_mat
                    
                    # generate final transformation matrix and applying pose to bunny
                    ext_mtx_4 = np.eye(4)
                    ext_mtx_4[0:3,:] = ext_mtx
                    ext_mtx_4 = np.matmul(ext_mtx_4, bunny_mtx)
                    ext_mtx_4 = np.matmul(rotate_factor, bunny_mtx)
                    ext_mtx_4 = np.matmul(translate_factor, ext_mtx_4)
                    scene.set_pose(bunny_node, pose=ext_mtx_4)
                    
                    # render bunny with alpha channel
                    color_render, depth_render = renderer.render(scene, flags=pyrender.RenderFlags.RGBA)

                    # masks of 3d render
                    _, color_render_mask = cv2.threshold(color_render[:,:,3], 10, 255, cv2.THRESH_BINARY)
                    color_render_mask_inv = cv2.bitwise_not(color_render_mask)

                    # obtain the sections from each image
                    draw_img_bg = cv2.bitwise_and(img_draw, img_draw, mask = color_render_mask_inv)
                    color_render_fg = cv2.bitwise_and(color_render, color_render, mask=color_render_mask)

                    # combine the image with the 3D render
                    img_draw = cv2.add(draw_img_bg, color_render_fg[:,:,0:3])
                    
                if draw_cube:
                    # draws a cube
                    draw_cube_img(img_draw, marker_size, cameraMatrix, rel_mtx)
                
                if draw_axis:
                    img_draw = aruco.drawAxis(img_draw, cameraMatrix, distCoeffs, rvec[0,0], tvec[0,0], 1)

                # prints distance and enabled features
                point = np.matmul(rel_mtx, np.array([0,0,0,1]))
                real_distance = glm.distance(glm.vec3(point), glm.vec3(0,0,0))
                new_string = 'Draw Bunny ("b"): [{}] - Draw Cube ("c"): [{}] - Draw Axis ("a"): [{}] - Distance to marker: {:.3f} {}\r'.format(draw_bunny, draw_cube, draw_axis, real_distance, marker_units)
                sys.stdout.write('{}\r'.format(' ' * len(last_text)))
                sys.stdout.write(new_string)
                last_text = new_string

            # draw image
            cv2.imshow('Feed', img_draw)

            # key listeners
            key_press = cv2.waitKey(1) & 0xFF
            if key_press == ord('q'):
                print('Quitting...')
                cap.release()
                cv2.destroyAllWindows()
                return 0
            elif key_press == ord('a'):
                draw_axis = not draw_axis
            elif key_press == ord('b'):
                draw_bunny = not draw_bunny
            elif key_press == ord('c'):
                draw_cube = not draw_cube
            elif key_press == ord('r'):
                record = not record

            # record option
            if record:
                if not was_recording:
                    # if video was not recording before, create video writer
                    video_writer = cv2.VideoWriter('recording.avi', fourcc, cam_fps, cam_dimensions)
                    was_recording = True
                
                # record video
                video_writer.write(img_draw)
                
            else:
                if was_recording:
                    if video_writer is not None:
                        # video writer exists. Release video writer and delete
                        video_writer.release()
                        video_writer = None

                    was_recording = False


if '__main__' in __name__:

    # Setup
    ## script path
    prog_path = os.path.dirname(os.path.abspath(__file__))
    
    ## defaults
    default_calibration_filename = 'calibration.pckl'
    default_settings_filename = 'settings.json'
    settings_filepath = os.path.join(prog_path, default_settings_filename)

    DEFAULT_CONFIG = {
                'version': 1.4,
                'calibration': default_calibration_filename,
                'video_source': 0,
                'recording_fps': None,
                'marker_size': 1.5,
                'marker_units': 'in'
    }
    
    usage = '$ python3 {} [-cl calibration_file_path.pckl ] [-ls settings_file.json ]'
    description = """Tracks a Fiducial marker and calculates relative distance from camera and displays 3D objects.
    Tested on Ubuntu 20.04 on Python3.8.
    """
    
    parser = argparse.ArgumentParser(prog='Fiducial AR Tracker', usage=usage, description=description)
    parser.add_argument('-ls', '--load-settings', required=False, default=settings_filepath, help='Preloaded settings information for the program to run. This file includes camera source and objects. If none provided, default is ./{}, which will be generated if it does not exist'.format(default_settings_filename))
    parser.add_argument('-cl', '--calibration', required=False, default=None, help='This overrides the calibration filepath from the settings'.format(default_calibration_filename))
    parser.add_argument('-gs', '--generate-settings', required=False, default=None, help='Generate a settings.json file with the name provided.')
    args = parser.parse_args(sys.argv[1:])

    if args.generate_settings is not None:
        with open(args.generate_settings, 'w+') as file:
            json.dump(DEFAULT_CONFIG, file, indent=4)
            exit(0)
    
    ## if no settings file is found, create one
    if not os.path.exists(settings_filepath):
        with open(settings_filepath, 'w+') as file:
            json.dump(DEFAULT_CONFIG, file, indent=4)

            
    # load settings file
    try:
        with open(args.load_settings, 'r') as f:
            configs = json.load(f)

        if configs['version'] < DEFAULT_CONFIG['version']:
            # if config version of file less than current version, update what's missing

            for key in DEFAULT_CONFIG:
                # iterate through all keys in default config
                
                if key not in configs:
                    # put key where it does not exist
                    configs[key] = DEFAULT_CONFIG[key]

            # write config file
            with open(args.load_settings, 'w+') as f:
                json.dump(configs, f, indent=4)
            
    except FileNotFoundError:
        print('Invalid settings file: {} - cannot be found'.format(args.load_settings))
        exit(1)
    
    if args.calibration is not None:
        configs['calibration'] = args.calibration
    
    # get callibration items
    with open(configs['calibration'], 'rb') as f:
        (_, cameraMatrix, distCoeffs, _, _) = pickle.load(f)
    
    # generate camera source
    try:
        int(configs['video_source'])
        # if there is no exception, then a device camera is requested
        cam = cv2.VideoCapture(configs['video_source'])
        cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
    except ValueError:
        # if raised, then video source is a string
        video_source = configs['video_source']

        if video_source.startswith('http'):
            # this is an ip camera, use ipcamera class
            cam = IPCamera(video_source)
        else:
            # this is a file
            cam = cv2.VideoCapture(video_source)

    # send to main function
    main(cam, cameraMatrix, distCoeffs, configs['recording_fps'], configs['marker_size'], configs['marker_units'])
    