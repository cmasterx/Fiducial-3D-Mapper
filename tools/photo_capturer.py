import cv2
import os
import pickle
from ipcamera import IPCamera

file_dir = './images/'
filename = 'capture_{}.png'

def main():
    # check if directory exists
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)
    filepath = os.path.join(file_dir, filename)
    
    cam = IPCamera('http://192.168.1.160:8080/video')

    file_counter = 0
    while cam.isOpened():
        ret, frame = cam.read()

        cv2.imshow('Camera', frame)

        key_pressed = cv2.waitKey(1) & 0xFF
        if key_pressed == ord('q'):
            break

        if key_pressed == ord('c'):
            print('Capturing image')

            # iterates file_counter until it finds a file name that doesn't exist
            print(filepath.format(file_counter))
            while os.path.exists(filepath.format(file_counter)):
                file_counter += 1
                
            cv2.imwrite(filepath.format(file_counter), frame)
            file_counter += 1

if '__main__' in __name__:
    main()