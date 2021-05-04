import cv2
import time
import multiprocessing as mp

class IPCamera:

    def __init__(self,url):        
        # create pipe
        self.parent_pipe, child_pipe = mp.Pipe()

        # multiprocess
        self.p = mp.Process(target=self.update, args=(child_pipe,url))        
        self.p.daemon = True
        self.p.start()

    def release(self):
        self.parent_pipe.send('quit')

    def update(self, pipe, url):
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)   
        running = True

        while running:

            # grab all frames
            cap.grab()

            rec_dat = pipe.recv()       # from pipe

            # from arguments
            if rec_dat == 'read':
                dat = cap.read()
                pipe.send(dat)
            elif rec_dat == 'quit' :
                cap.release()
                running = False
            elif rec_dat == 'isOpen':
                pipe.send(cap.isOpened())

            time.sleep(0.001)

        pipe.close()

    def isOpened(self):
        self.parent_pipe.send('isOpen') # sends is open command
        res = self.parent_pipe.recv()
        self.parent_pipe.send(0)    # resets pipe
        return res

    def read(self):

        self.parent_pipe.send('read')
        dat = self.parent_pipe.recv()
        self.parent_pipe.send(0)

        return dat