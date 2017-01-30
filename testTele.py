from telegram import *
from threading import Thread
from pyautogui import confirm
# from time import sleep

tele = Telegram()
thread = Thread(target=tele.start)
try:
    thread.start()
except NetworkError:
    print "Network Error."
except VLCConnectionError:
    print "Can't connect to vlc."
except:
    print "Error"
# If switch is turned off do this
switch = confirm(text = 'Stop Telegram', title = 'Control', buttons = ['OK'])
tele.stop()
