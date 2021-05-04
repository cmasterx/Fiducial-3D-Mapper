import cv2
import sys

def main(argv):
    if len(argv) < 3:
        print('Usage: python3 ./{} <camera ID> <video filename>'.format(argv[0]))
        print('\tex: python3 ./{} 0 myvideo.avi'.format(argv[0]))
        return 1
    
    try:
        # camera ID
        camID = int(argv[1])
    except ValueError:
        print('The cameraID should be an number. "{}" is not valid'.format(argv[1]))
        return(1)

    # output filename
    filename = argv[2]
    # camera insetance
    cam = cv2.VideoCapture(camID)
    cam_dimensions = (int(cam.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    cam_fps = cam.get(cv2.CAP_PROP_FRAME_COUNT)

    # video writer
    print(cam_dimensions)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_writer = cv2.VideoWriter(filename, fourcc, 30, cam_dimensions)
    
    while cam.isOpened():
        ret, frame = cam.read()

        video_writer.write(frame)
        
        cv2.imshow('Recording', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    video_writer.release()
    cv2.destroyAllWindows()
    
    return 0

if '__main__' in __name__:
    ret = main(sys.argv)
    exit(ret)