import numpy as np
import cv2, threading, sys, datetime
from time import sleep
from vlcclient import VLCClient
from winplayer import MediaPlayer
from pyautogui import confirm

# For good detection in night time
hour = int(str(datetime.datetime.now().time())[:2])
accuracy = 2 if (hour>17 or hour<8) else 7

face_cascade = cv2.CascadeClassifier('data\\haarcascade_frontalface_default.xml')
# face_cascade2 = cv2.CascadeClassifier('data\\haarcascade_frontalface_alt2.xml')
eye_cascade3 = cv2.CascadeClassifier('data\\haarcascade_lefteye_2splits.xml')
# eye_cascade2 = cv2.CascadeClassifier('data\\eyes.xml')
eye_cascade2 = cv2.CascadeClassifier('data\\eyeglasses.xml')

choice, player = None, None
vconnected = False
state = 1                           # 0 means paused. 1 means playing.
times, times2= 0, 0                 # times- number of prev frames with no eyes. times2- with eye(s)

def getChoice(s='', Choice=''):                # FINAL check choice as input
    global player, vconnected, state, choice
    choice = confirm(text=s+'What do you want to use?', title='VLC or WMP?', buttons=['VLC', 'WMP', 'Exit'])
    if choice=="WMP":
        player = MediaPlayer()
        print "Connected to Windows Media Player. Start media."
        sleep(1)
        return True
    elif choice == "VLC":
        player = VLCClient("::1")
        try:
            player.connect()
            vconnected = True
            print "Connected to VLC. \n"
            temp = player.status().split()[-2]
            state = 1 if str(temp).lower()=='playing' else 0
            return True
        except Exception as e:
            vconnected = False
            print "VLC is not running in Telnet Mode."
            print "Run VLC in Telnet mode and try again."
            getChoice("VLC not found. ")
            return False
    else:
        sys.exit(0)


def check(val):                               # val = eyes detected
    global times, times2, state, vconnected
    if choice == 'VLC':
        try:
            temp = player.status().split()[-2]
            state = 1 if str(temp).lower()=='playing' else 0
        except:
            vconnected = False
            return

    thresh = 10
    if val==0 and times<thresh:
        times+=1
        if times2>0:
            times2-=1
    if val>=1 and times2<thresh:
        times2+=1
        if times>0:
            times-=1
    if times>=thresh:
        times2 = 0
        if state:
            try:
                player.pause()
                print "Pause"
                state = 0
            except:
                vconnected = False
    if times2>=thresh:
        times = 0
        if not state:
            try:
                player.play()
                print "Play"
                state = 1
            except:
                vconnected = False


def start(Choice=''):
    getChoice(Choice)
    cap = None                                 # Object for video capture
    try:
        cap = cv2.VideoCapture(0)
    except:
        print "Problem with camera."
        sys.exit(0)
    while True:
        # Capturing Frame
        ret, img = cap.read()
        # It may take some time for camera to function
        if ret==False:
            continue
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.1, accuracy, minSize=(100,100))
        checkVal = 0
        for (x,y,w,h) in faces:
            cv2.rectangle(img,(x,y), (x+w,y+h), (255,0,0), accuracy)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
            eyes = eye_cascade3.detectMultiScale(roi_gray, 1.05, minSize=(20,20))
            eyes2 = eye_cascade2.detectMultiScale(roi_gray, 1.05, minSize=(30,30))
            for (ex,ey,ew,eh) in eyes:
                cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
            for (ex,ey,ew,eh) in eyes2:
                cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,0,255),2)
            checkVal += len(eyes)+len(eyes2)

        thread = threading.Thread(target=check, args=(checkVal,))
        thread.daemon = True
        thread.start()

        if choice == "VLC" and vconnected == False:
            print "Unable to connect to VLC."
            print "Please check that VLC is running in telnet mode and try again."
            cv2.destroyAllWindows()
            getChoice("VLC not found. ")

        cv2.imshow('img',img)

        if cv2.waitKey(1) & 0xFF == ord('q'): # Press q to exit.
            break


if __name__ == "__main__":
    start()
    cv2.destroyAllWindows()
