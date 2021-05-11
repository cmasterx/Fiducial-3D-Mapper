import cv2
import cv2.aruco as aruco
import time
import os
from ipcamera import IPCamera

OUT_DIR = './video'
# CAMERA_SOURCE = 1
# CAMERA_SOURCE = 'http://192.168.4.24:8080/video'
CAMERA_SOURCE = 0

if '__main__' in __name__:
    # camera = cv2.VideoCapture('http://192.168.4.24:8080/video')
    
    # check if video source is a camera, file, or ipcamera
    if isinstance(CAMERA_SOURCE, int):
        # video source is a camera
        camera = cv2.VideoCapture(CAMERA_SOURCE)
    elif isinstance(CAMERA_SOURCE, str):
        # video source is a file or ip camera
        if CAMERA_SOURCE.startswith('http'):
            # camera is an ipcamera
            camera = IPCamera(CAMERA_SOURCE)
        else:
            camera = cv2.VideoCapture(CAMERA_SOURCE)
    
    # camera properties
    font = cv2.FONT_HERSHEY_COMPLEX
    org = (50, 50)
    fontScale = 1
    color = (255, 0, 0)
    thickness = 2

    checker_pattern = (6, 9)
    
    capture_time = 10            # number of seconds before a capture
    current_time = time.time()  # current time
    capture_counter = 1         # counter for camera
    capture_limit = 15          # maximum number of images
    
    # create video result directory if not found
    if not os.path.exists(OUT_DIR):
        print('Cannot find {}, creating directory.'.format(OUT_DIR))
        os.makedirs(OUT_DIR)
    else:
        print('Directory \'{}\' found.'.format(OUT_DIR))
    
    while True:
        camera.grab()
        ret, frame = camera.read()
        time_at_frame = time.time()
        
        # img = cv2.putText(frame, 'Test', org, font, fontScale, color, thickness, cv2.LINE_AA)
        img = frame
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        retval, corners = cv2.findChessboardCorners(img_gray, checker_pattern, None)
        
        if (time.time() - current_time > capture_time):
            filepath = os.path.join(OUT_DIR, 'frame_{}.png'.format(capture_counter))
            cv2.imwrite(filepath, img_gray)
            current_time = time_at_frame
            capture_counter += 1

        if capture_counter <= capture_limit:
            img = cv2.drawChessboardCorners(img, checker_pattern, corners, retval)
            cv2.putText(img, 'Images Left: {:3} - Capturing in {:.1f}'.format(capture_limit - capture_counter + 1,capture_time - (time_at_frame - current_time)), org, font, fontScale, color, thickness, cv2.LINE_AA)
        else:
            cv2.putText(img, 'Done', org, font, fontScale, color, thickness, cv2.LINE_AA)

        # put circles in corners
        if ret == True:
            pass
            # print('Returned true - corners: ', img)
        
        # flip = cv2.flip(img, 1)
        
        cv2.imshow('camera', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(1/48)
    
    camera.release()
    cv2.destroyAllWindows()
    # cv.aruco.Dic
    
    pass