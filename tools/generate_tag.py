import cv2 as cv
import cv2.aruco as aruco
import sys

default_args = {
    'size': 1,
    'id':    100,
    'filename': 'marker.jpg'
}

if '__main__' in __name__:
    print (sys.argv)

    if len(sys.argv) == 1:
        args = default_args
    elif len(sys.argv) == 4:
        args = {
            'size': int(sys.argv[2]),
            'id': int(sys.argv[1]),
            'filename' : sys.argv[3],
        }
    else:
        print('Usage: python3 ./{} <id of tag> <size of tag> <filename>'.format(sys.argv[0]))
        exit(1)

    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    img = aruco.drawMarker(aruco_dict, args['id'], args['size'])
    cv.imwrite(args['filename'], img)

    # cv.imshow('frame', img)
    # cv.waitKey(0)
    # cv.destroyAllWindows()