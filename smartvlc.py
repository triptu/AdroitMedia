'''Steps:-
1. Open vlc using "vlc --extraintf telnet --telnet-password admin" at cmd.
                        OR
2. Follow these steps for permanent configuration of vlc:-
    a) Goto Tools>Preferences after opening vlc.
    b) In lower left corner click on all below show settings.
    c) Goto Interface>Main interfaces and check mark telnet.
    d) Goto Interface>Main interfaces>Lua and set password="admin".
        Also verify host=localhost and Port=4212. Don't mess up with anything else.
3. Run Program
4. Enjoy...!
'''

import numpy as np
import os, cv2, threading, sys, datetime
from time import sleep
from vlcclient import VLCClient
from pyautogui import confirm

# print "\nCreator: Tushar Tripathi"
# print "Email:  tushutripathi@gmail.com\n"

hour = int(str(datetime.datetime.now().time())[:2])
accuracy = 2 if (hour>17 or hour<8) else 5

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# face_cascade2 = cv2.CascadeClassifier('haarcascade_frontalface_alt2.xml')
eye_cascade3 = cv2.CascadeClassifier('haarcascade_lefteye_2splits.xml')
# eye_cascade2 = cv2.CascadeClassifier('eyes.xml')
eye_cascade2 = cv2.CascadeClassifier('eyeglasses.xml')

vlc = VLCClient("::1")
connected = False

try:
    vlc.connect()
    connected = True
    print "Connected to VLC. \n"
except Exception as e:
    print "VLC is not running in Telnet Mode."
    print "Run VLC in Telnet mode and try again."
    sleep(3)
    sys.exit(0)


# vlc.add("D:\DC++Share\Songs\Video\pyDirect\OneRepublic - Counting Stars-hT_nvWreIhg.mp4")

cap = None                                 # Object for video capture
try:
    cap = cv2.VideoCapture(0)
except:
    print "Problem with camera."
    sys.exit(0)
times, times2= 0, 0                 # times- number of prev frames with no eyes. times2- with eye(s)
state = vlc.status().split()[-2]
curr = 1 if str(state).lower()=='playing' else 0

def check(val):
    global times, times2, curr, connected
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
        if curr:
            try:
                vlc.pause()
            except:
                connected = False
            print "Pause"
            curr = 0
    if times2>=thresh:
        times = 0
        if not curr:
            try:
                vlc.play()
            except:
                connected = False
            print "Play"
            curr = 1

while True:
    # Capturing Frame
    ret, img = cap.read()
    # It takes some time for camera to function
    # if ret==False:
    #     continue

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


    faces = face_cascade.detectMultiScale(gray, 1.1, 3, minSize=(100,100))
    if len(faces)==0:
        thread = threading.Thread(target=check, args=(0,))
        thread.daemon = True
        thread.start()
    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0), accuracy)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        eyes = eye_cascade3.detectMultiScale(roi_gray, 1.05, minSize=(20,20))
        eyes2 = eye_cascade2.detectMultiScale(roi_gray, 1.05, minSize=(30,30))

        thread = threading.Thread(target=check, args=(len(eyes)+len(eyes2),))
        thread.daemon = True
        thread.start()

        # print len(eyes)+len(eyes2), times, times2
        for (ex,ey,ew,eh) in eyes:
            cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
        for (ex,ey,ew,eh) in eyes2:
            cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,0,255),2)

    if connected == False:
        print "Unable to connect to VLC."
        print "Please check that VLC is running in telnet mode and try again."
        sleep(3)
        cv2.destroyAllWindows()
        sys.exit(0)

    cv2.imshow('img',img)

    if cv2.waitKey(1) & 0xFF == ord('q'): # Press q to exit.
        break


cv2.destroyAllWindows()
