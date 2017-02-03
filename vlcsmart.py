import numpy as np
import cv2, threading, datetime, re
from time import sleep
from vlcclient import VLCClient
from winplayer import MediaPlayer
from threading import Thread

class smartPauseStopped(Exception):
    pass

class smartVlc():

    def __init__(self):
        hour = int(str(datetime.datetime.now().time())[:2])
        self.accuracy = 2 if (hour>17 or hour<8) else 7

        self.face_cascade = cv2.CascadeClassifier('data\\haarcascade_frontalface_default.xml')
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

        thresh = 10
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
        if self.cap is None:
            print "Can't Connect with Camera."
        while self.running:
            # Capturing Frame
            if self.cap:
                ret, img = self.cap.read()
            else:
                break
            # It may take some time for camera to function
            if ret==False:
                continue
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            faces = self.face_cascade.detectMultiScale(gray, 1.1, self.accuracy, minSize=(100,100))
            checkVal = 0
            for (x,y,w,h) in faces:
                cv2.rectangle(img,(x,y), (x+w,y+h), (255,0,0))
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = img[y:y+h, x:x+w]
                eyes = self.eye_cascade3.detectMultiScale(roi_gray, 1.1, minSize=(20,20))
                # eyes2 = self.eye_cascade2.detectMultiScale(roi_gray, 1.1, minSize=(30,30))
                for (ex,ey,ew,eh) in eyes:
                    cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
                # for (ex,ey,ew,eh) in eyes2:
                    # cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,0,255),2)
                # checkVal += len(eyes)+len(eyes2)
                checkVal += len(eyes)

            thread = threading.Thread(target=self.check, args=(checkVal,))
            thread.daemon = True
            thread.start()

            if self.choice == "vlc" and self.vconnected == False and self.running == True:
                print "Unable to connect to VLC."
                print "Please check that VLC is running in telnet mode."
                self.stop()
                self.gotError = True
            # cv2.imshow('img',img)

            # if cv2.waitKey(1) & 0xFF == ord('q'): # Press q to exit.
            #     self.stop()
            #     break

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
        if self.choice and self.choice.lower() == 'vlc' and self.vconnected:
            self.player.disconnect()
            print "VLC disconnected."
            self.vconnected = False
        else:
            print "Media Player disconnected."
            self.player = None
        if self.cap:
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
    sleep(5)
    vlc.stop()
    vlc.connect('wmp')
    th2 = Thread(target = vlc.start)
    th2.daemon = True
    th2.start()
    sleep(5)
    vlc.stop()
