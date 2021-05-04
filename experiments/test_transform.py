import cv2
import cv2.aruco as aruco
import pickle
import numpy as np
from ipcamera import IPCamera
import glm
import time

def main():
    cv2.setNumThreads(12)
    s_length = 31/32
    square = np.zeros((12, 2, 3))
    square[0,0,:] = [0 - 0.5,0-0.5,1]
    square[1,0,:] = [1 - 0.5,0-0.5,1]
    square[2,0,:] = [1 - 0.5,1-0.5,1]
    square[3,0,:] = [0 - 0.5,1-0.5,1]

    square[0,1,:] = [1-0.5,0-0.5,1]
    square[1,1,:] = [1-0.5,1-0.5,1]
    square[2,1,:] = [0-0.5,1-0.5,1]
    square[3,1,:] = [0-0.5,0-0.5,1]

    
    # check if directory exists
    cam = cv2.VideoCapture(0)
    # cam = IPCamera('http://192.168.1.160:8080/video')

    # load camera matrix
    with open('./calibration.pckl', 'rb') as file:
        (_, mtx, dist, _, _) = pickle.load(file)

    ARUCO_PARAMS = aruco.DetectorParameters_create()
    ARUCO_DICT = aruco.Dictionary_get(aruco.DICT_6X6_250)

    board = aruco.GridBoard_create(
        markersX=2,
        markersY=2,
        markerLength=0.09,
        markerSeparation=0.01,
        dictionary=ARUCO_DICT)

    square_orig = square.copy()
    while cam.isOpened():
        square = square_orig.copy()
        ret, frame = cam.read()

        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, ARUCO_DICT, parameters=ARUCO_PARAMS)
            corners, ids, rejectedImgPoints, recoveredIds = aruco.refineDetectedMarkers(
                image = gray,
                board = board,
                detectedCorners = corners,
                detectedIds = ids,
                rejectedCorners = rejectedImgPoints,
                cameraMatrix = mtx,
                distCoeffs = dist
            )
            
            if ids is not None:
                rvec, tvec, _objPoints = aruco.estimatePoseSingleMarkers(corners, 31/32, mtx, dist)                                           
            
                for i in range(len(rvec)):
                    frame = aruco.drawAxis(frame, mtx, dist, rvec[i, 0], tvec[i, 0], 5)
            
                ext_mtx = np.zeros((3, 4))
                rvec_mat, _ = cv2.Rodrigues(rvec[0,0])
                ext_mtx[:,0:3] = rvec_mat
                ext_mtx[:,3]  = tvec[0,0]
                # ext_mtx = np.column_stack(rvec_mat, tvec[0,0])


                points = [[-31/32 / 2, 31 / 32 / 2, 0], [-31/32 / 2, 31 / 32 / 2, 5]]
                for i in range(len(points)):
                    # print(mtx)
                    # print(ext_mtx)
                    # print(np.matmul(mtx, ext_mtx))
                    points[i] = np.matmul(np.matmul(mtx, ext_mtx), glm.vec4(points[i], 1))
                    # new_points = cv2.projectPoints([points], rvec[0,0], tvec[0,0], mtx, dist)
                    points[i] = (int(points[i][0] / points[i][2]), int(points[i][1] / points[i][2]))
                    # points[i] = np.array(glm.vec2(points[i]))
                    # points[i] = tuple(l for l in points[i])
                
                # transform points of square
                transfor_mtx =  np.matmul(mtx, ext_mtx)
                for l in range(square.shape[0]):
                    for p in range(square.shape[1]):
                        tmp_pt = np.matmul(transfor_mtx, glm.vec4(glm.vec3(square[l,p,:]), 1.0))
                        # print(square[l,p,:])
                        # print(tmp_pt / tmp_pt[2])
                        square[l,p,:] = tmp_pt / tmp_pt[2]
                

                for l in range(square.shape[0]):
                    p0 = (int(square[l,0,0]), int(square[l,0,1]))
                    p1 = (int(square[l,1,0]), int(square[l,1,1]))
                    cv2.line(frame, p0, p1, (255, 0, 255), 5)
                    # print(p0)
                    # print(p1)
                     
                # cv2.line(frame, points[0], points[1], (125, 125, 0), 9)
                
                
            cv2.imshow('Camera', frame)
            time.sleep(1/24)
            # exit(1)

        key_pressed = cv2.waitKey(1) & 0xFF
        if key_pressed == ord('q'):
            break

if '__main__' in __name__:
    main()
