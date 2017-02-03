from __future__ import unicode_literals
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from vlcsmart import smartVlc, smartPauseStopped
from threading import Thread
from BasicInfo import getName, getNamePath
from lyrics import getLyrics
import os, sys
from queue import Queue
from subtitle import Subtitle
from telegram import *
from time import sleep


class ImageButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(ImageButton, self).__init__(**kwargs)
        self.flag = 0
        self.source = 'data\off.png'
        self.allow_stretch = True

    def on_press(self):
        if self.flag == 0:
            #self.pos_hint={'x': .075, 'y': .7}
            self.source = 'data\on.png'
            self.flag=1

        else :
            #self.pos_hint={'x': .075, 'y': .7}
            self.source = 'data\off.png'
            self.flag = 0

class Search(FloatLayout):

    def __init__(self, **kwargs):
        super(Search, self).__init__(**kwargs)
        self.flag = 0

        # user_input = TextInput()
        self.user_input = TextInput(multiline=False, font_size=25)
        self.add_widget(self.user_input)
        self.user_input.size_hint = (0.5, 0.076)
        self.user_input.pos_hint = {'x':.37, 'y':.59}
        name = getName()
        print "Current ", name
        if name!='':
            name = name[:-4]
            self.user_input.text = name

    def update(self):
        name = getName()
        if name!='':
            name = name[:-4]
            self.user_input.text = name


# Declare both screens
class LandingScreen(Screen):

    def __init__(self, *args, **kwargs):
        super(LandingScreen, self).__init__(*args, **kwargs)
        self.smartPause = False
        self.curr_player = None
        self.sub = False
        self.subname = ''
        self.telegram = False

    def controlSmartPause(self, value, root):
        if value==0:                       # It is going to onpress of ImageButton class first
            self.smartPause = True
            print "Smart Pause on."
            self.player = smartVlc()
        else:
            stopthread = Thread(target=self.player.stop)
            stopthread.daemon = True
            stopthread.start()
            stopthread.join()
            root.vid.active = False
            root.wid.active = False
            self.smartPause = False
            print "Smart Pause is off."

    def telegramHelper(self, instance):
        try:
            self.tele.start()
        except VLCConnectionError:
            print "Telegram Unable to connect to VLC"
            sleep(0.01)
            instance.active = False
        except NetworkError:
            print "Telegram Unable to connect to Internet."
            sleep(0.01)
            instance.active = False
        except Exception as e:
            print "Telegram Error", str(e)
            instance.active = False

    def Switch_on_Telegram(self, instance, value):
        if value is True:
            print("Trying to switch on Telegram")
            try:
                self.tele = Telegram()
                self.telegram = True
                print "Switched on."
                telethread = Thread(target=self.telegramHelper, args = (instance,))
                telethread.daemon = True
                telethread.start()
            except VLCConnectionError:
                print "Unable to connect to VLC."
                print "Ensure it is running in telnet mode."
                instance.active = False

        else:
            if self.telegram:
                self.tele.stop()
            self.telegram = False
            print("Switch Off Telegram")


    def Switch_on_VLC(self, instance, value, instance2):
        if self.smartPause and value is True:
            print("Switch On VLC")
            self.curr_player = 'vlc'
            instance2.active = False
            sleep(0.01)
            val = self.player.connect('vlc')
            if not val:
                self.player.stop()
                instance.active = False
            else:
                vthread = Thread(target=self.player.start)
                vthread.daemon = True
                vthread.start()
        elif self.smartPause and value==False:
            print("Switch Off VLC")
            if self.curr_player == 'vlc':
                self.player.stop()
                self.curr_player = None
        elif self.smartPause == False:
            instance.active = False
            if self.curr_player == 'vlc':
                print "Switch off VLC."
                self.player.stop()
                self.curr_player = None

    def Switch_on_WMP(self, instance, value, instance2):
        if self.smartPause and value is True:
            print("Switch On WMP")
            self.curr_player = 'wmp'
            instance2.active = False
            sleep(0.01)
            self.player.connect('wmp')
            v2thread = Thread(target=self.player.start)
            v2thread.daemon = True
            v2thread.start()
        elif self.smartPause and value==False:
            print "Switch off WMP"
            if self.curr_player == 'wmp':
                self.player.stop()
                self.curr_player = None
        elif self.smartPause == False:
            instance.active = False
            if self.curr_player == 'wmp':
                print "Switch off WMP."
                self.player.stop()
                self.curr_player = None


    def downloadsubhelper(self, name, path):
        q4 = Queue()
        new = Subtitle(name, path, q4)
        subReturn = q4.get()
        if not subReturn[0]:
            # Unable to connect to internet
            return
        try:
            q2 = Queue()
            sthread = Thread(target = new.download, args=(q2,))
            sthread.daemon = True
            sthread.start()
            sthread.join(timeout = 30)
        except:
            print "Can't download Subtitle."
        result = None
        try:
            result = q2.get()
        except:
            pass
        if result:
            print "Subtitle Downloaded"
            self.sub = True
        else:
            print 'Subtitle not Downloaded.'
            self.sub = False


    def downloadsub(self):
        name, path = getNamePath()
        print name, path
        if name=='':
            return
        if name==self.subname and self.sub:
            print "Subtitle Already Downloaded."
            return
        if name!=self.subname:
            self.sub = False
        self.subname = name
        subthread = Thread(target = self.downloadsubhelper, args = (name, path))
        subthread.daemon = True
        try:
            subthread.start()
        except Exception as e:
            print str(e)

class LyricsScreen(Screen):

    def __init__(self, *args, **kwargs):
        super(LyricsScreen, self).__init__(*args, **kwargs)
        self.lyrics = ""
        self.song = ''

    def loadLyricshelper(self, song):
        q = Queue()
        getLyrics(song, q)
        self.lyrics = q.get()
        self.lyrics = self.lyrics.encode('utf-8')
        self.lyrics2.text = self.lyrics

    def loadLyrics(self, song):
        if self.song==song and self.lyrics!='Sorry, Lyrics not found.':
            return
        else:
            self.song = song
            self.lyrics2.text = "Loading Lyrics for " + song + " ..."
            print "Loading Lyrics for " + song + " ..."
            threadl = Thread(target = self.loadLyricshelper, args=(song,))
            threadl.daemon = True
            threadl.start()

class HelpScreen(Screen):
    def __init__(self, *args, **kwargs):
        super(HelpScreen, self).__init__(*args, **kwargs)
        self.help_text = '''Adroit makes your media player smart! :-)
Adroit helps you do things in a simple way with its neat UI.

Have you ever thought how nice it would be if your player can sense you looking at the screen and pause when you are looking away. Adroit lets you do that simply by enabling smart pause.
You can use the lyrics feature to instantly get the lyrics of whatever song you want saving you hassle of searching on the internet.
You can also download the subtitle of movie or TV series episode you are playing.  And as the subtitles are retrieved with the help of the hash you can rest asure about its syncing.
Not only this you can also turn on the Telegram feature of Adroit and use the telegram messenger in your mobile to control your media remotely by just chatting with Adroit.
Never thought it would be this simple, right?
The commands available with Adroit bot are- play,pause,next,prev,vup,vdown,fscreen,rfscreen only for vlc media player.
You just have to setup a bot following these steps https://core.telegram.org/bots#6-botfather and write the api token in api.txt.


"Adroit" - Let the revolution begin.
Version: 1.0
Developer:- Tushar Tripathi
Designer:-   Harshil Chaudhary
BITS Pilani'''

class AdroitApp(App):
    pass

if __name__ == '__main__':
    logfile = open('logger.dat', 'w')
    # sys.stdout = logfile
    AdroitApp().run()
    logfile.close()
