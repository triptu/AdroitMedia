import numpy as np
import cv2, threading, datetime, re
from time import sleep, time
from vlcclient import VLCClient
from winplayer import MediaPlayer
from threading import Thread
from yPlayer import ytubePlayer


''' There are things which may not make sense. They are done either for optimization in terms of efficiency, time and processing or
because they fixed something and their removal might break something.'''
'''Observations:-
1. Time is not really a problem. The bottleneck I found was reading image from camera feed which takes about 33 ms and obviously nothing can be done about it.
2. But cpu usage is. I have cut down cpu usage from more than 50-60% to under 20%. But still there can be further progress. My stupidity and steps taken:-
   a) Using two eyes har cascades for accuracy. Its of no need. Uses unnecessary cpu. Chose the best of them.
   b) I am now using lbpcascade instead of haar cascade as it showed better cpu usage. Haar involves lots of floating data.
   c) Checking only for alternative frames.
   d) Checking for eyes only in the upper half of face. Very effective and works unless you are some kind of eye monster.
   e) Experimented with cropping frame. False negatives. A small boundary can be cropped though.
'''


class smartPauseStopped(Exception):
    pass

class smartVlc():

    def __init__(self):
        hour = int(str(datetime.datetime.now().time())[:2])
        self.accuracy = 2 if (hour>17 or hour<8) else 7

        # self.face_cascade = cv2.CascadeClassifier('data\\haarcascade_frontalface_default.xml')
        self.face_cascade = cv2.CascadeClassifier('data\\lbpcascade_frontalface.xml')
        self.eye_cascade3 = cv2.CascadeClassifier('data\\haarcascade_lefteye_2splits.xml')
        # self.eye_cascade2 = cv2.CascadeClassifier('data\\eyeglasses.xml')

        self.cap = None
        self.choice, self.player = None, None
        self.running = True
        self.vconnected = False
        self.state = 1                           # 0 means paused. 1 means playing.
        self.times, self.times2= 0, 0                 # times- number of prev frames with no eyes. times2- with eye(s)
        self.gotError = False

    def connect(self, choice):
        self.choice = choice
        if self.choice.lower() =="wmp":
            if self.vconnected:
                self.player.disconnect()
            self.player = MediaPlayer()
            self.running = True
            print "Connected to Windows Media Player. Start media."
            sleep(0.5)
            return True
        elif self.choice.lower() == "vlc":
            if self.vconnected:
                return True
            self.player = VLCClient("::1")
            try:
                self.player.connect()
                self.running = True
                self.vconnected = True
                print "Connected to VLC. \n"
                temp = self.player.status().split()[-2]
                self.state = 1 if str(temp).lower()=='playing' else 0
                return True
            except Exception as e:
                self.vconnected = False
                self.running = False
                print "VLC is not running in Telnet Mode."
                print "Run VLC in Telnet mode and try again."
                print "Error in connecting to vlc. ", str(e)
                self.player.disconnect()
                return False
        elif self.choice.lower() == 'ytube':
            if self.vconnected:
                self.player.disconnect()
            self.player = ytubePlayer()
            self.running = True
            print "Connected to youtube"
            sleep(0.5)
            return True

    def check(self, val):                               # val = eyes detected
        if self.choice == 'vlc':
            try:
                temp = self.player.status().split()[-2]
                self.state = 1 if str(temp).lower()=='playing' else 0
            except:
                self.vconnected = False
                self.running = False
                print "Connection to VLC broken."
                return False

        thresh = 5
        if val==0 and self.times<thresh:
            self.times+=1
            if self.times2>0:
                self.times2-=1
        if val>=1 and self.times2<thresh:
            self.times2+=1
            if self.times>0:
                self.times-=1
        if self.times>=thresh:
            self.times2 = 0
            if self.state:
                try:
                    self.player.pause()
                    print "Pause"
                    self.state = 0
                except:
                    self.vconnected = False
                    self.running = False
        if self.times2>=thresh:
            self.times = 0
            if not self.state:
                try:
                    self.player.play()
                    print "Play"
                    self.state = 1
                except:
                    self.vconnected = False
                    self.running = False

    def start(self):
        self.cap = None                                 # Object for video capture
        try:
            self.cap = cv2.VideoCapture(0)
        except:
            print "Problem with camera."
            return False
        if self.cap is None or not(self.cap.isOpened()):
            print "Can't Connect with Camera."
        flag = 0
        # t1, t2, t3, t4, count = 0,0,0,0, 0
        while self.running:
            # Capturing Frame
            # time1 = time()
            if self.cap and self.cap.isOpened():
                ret, img = self.cap.read()
                # t4+= (time()-time1)
            else:
                print "Unable to read from the camera feed."
                break
            # It may take some time for camera to function
            if ret==False:
                print "Return value for camera feed is false. Nothing read."
                continue
            # Dealing with only alternate frames for improved efficiency.
            if flag==0:
                flag = 1
                continue
            else:
                flag = 0
            # count+=1
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # time2 = time(); t1+=(time2-time1)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, self.accuracy, minSize=(100,100))
            # time3 = time(); t2+=(time3-time2)
            checkVal = 0
            for (x,y,w,h) in faces:
                # cv2.rectangle(img,(x,y), (x+w,y+h), (255,0,0))                                    # Uncoment for displaying frames
                roi_gray = gray[y:y+h/2, x:x+w]                                                     # h/2 because eyes are generally in uffer half of face/
                                                                                                    # change to h if you are some kind of monster
                # roi_color = img[y:y+h, x:x+w]
                eyes = self.eye_cascade3.detectMultiScale(roi_gray, 1.1, minSize=(20,20))
                # for (ex,ey,ew,eh) in eyes:                                                        # Uncomment for showing
                    # cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
                checkVal += len(eyes)
            # time4 = time(); t3+=(time4-time3)
            thread = threading.Thread(target=self.check, args=(checkVal,))
            thread.daemon = True
            thread.start()
            # cv2.imshow('img',img)


            if self.choice == "vlc" and self.vconnected == False and self.running == True:
                print "Unable to connect to VLC."
                print "Please check that VLC is running in telnet mode."
                self.stop()
                self.gotError = True


            if cv2.waitKey(1) & 0xFF == ord('q'): # Press q to exit.
                self.stop()
                break
        # print "Time taken for capturing and converting to grayscale per frame:", t1/(count*1.0)
        # print "Time taken for detetcting face per frame:", t2/(count*1.0)
        # print "Time taken for detetcting eyes per frame:", t3/(count*1.0)
        # print "Time taken for capturing:", t4/(count*2.0)

    def setChoice(self, choice):
        if choice==self.choice:
            pass
        else:
            self.choice = choice
            if choice == 'wmp':
                self.player.disconnect()
            self.connect()

    def stop(self):
        self.running = False
        if self.choice:
            if self.choice.lower() == 'vlc' and self.vconnected:
                self.player.disconnect()
                print "VLC disconnected."
                self.vconnected = False
            elif self.choice.lower() == 'wmp':
                print "Media Player disconnected."
            elif self.choice.lower() == 'wmp':
                print "YouTube disconnected."
                self.player = None
        if self.cap and self.cap.isOpened():
            print "camera off"
            self.cap.release()
            cv2.destroyAllWindows()
        # if self.gotError:
        #     raise smartPauseStopped
        return True

if __name__ == '__main__':
    vlc = smartVlc()
    vlc.connect('vlc')
    th = Thread(target = vlc.start)
    th.daemon = True
    th.start()
    sleep(15)
    print "Stopping now."
    vlc.running = False
    sleep(2)
    vlc.stop()
    vlc = smartVlc()
    vlc.connect('vlc')
    th = Thread(target = vlc.start)
    th.daemon = True
    th.start()
    sleep(15)
    print "Stopping now."
    vlc.running = False
    sleep(2)
    vlc.stop()

