from __future__ import unicode_literals
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from vlcsmart import smartVlc, smartPauseStopped
from kivy.core.window import Window
from threading import Thread
from BasicInfo import getName, getNamePath
from lyrics import getLyrics
import os
import sys
from queue import Queue
from subtitle import Subtitle
from telegram import *
from time import sleep
from kivy.properties import *
from kivymd.theming import ThemeManager
from kivymd import snackbar as Snackbar
from kivy.factory import Factory
import requests
from kivymd.toolbar import Toolbar
from kivymd.selectioncontrols import MDSwitch
from kivymd.navigationdrawer import NavigationDrawer
from kivymd.textfields import MDTextField
from youtube import ytubePlayer
import logging


class HoverBehavior(object):
    """Hover behavior.
    :Events:
        `on_enter`
            Fired when mouse enter the bbox of the widget.
        `on_leave`
            Fired when the mouse exit the widget
    """

    hovered = BooleanProperty(False)
    border_point = ObjectProperty(None)
    '''Contains the last relevant point received by the Hoverable. This can
    be used in `on_enter` or `on_leave` in order to know where was dispatched the event.
    '''

    def __init__(self, **kwargs):
        self.register_event_type('on_enter')
        self.register_event_type('on_leave')
        Window.bind(mouse_pos=self.on_mouse_pos)
        super(HoverBehavior, self).__init__(**kwargs)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return                      # do proceed if I'm not displayed <=> If have no parent
        pos = args[1]
        # Next line to_widget allow to compensate for relative layout
        inside = self.collide_point(*self.to_widget(*pos))
        if self.hovered == inside:
            # We have already done what was needed
            return
        self.border_point = pos
        self.hovered = inside
        if inside:
            self.dispatch('on_enter')
        else:
            self.dispatch('on_leave')

    def on_enter(self):
        pass

    def on_leave(self):
        pass


Factory.register('HoverBehavior', HoverBehavior)


class ImageButton(ButtonBehavior, Image, HoverBehavior):
    def __init__(self, **kwargs):
        super(ImageButton, self).__init__(**kwargs)
        self.flag = 0
        self.source = 'atlas://data/smartPauseRed/off'
        # self.source = 'data/mid.jpg'
        self.allow_stretch = True

    def on_press(self):
        if self.flag == 0:
            # self.pos_hint={'x': .075, 'y': .7}
            self.source = 'atlas://data/smartPauseRed/on'
            # self.source = 'data/on.png'
            self.flag = 1

        else:
            # self.pos_hint={'x': .075, 'y': .7}
            self.source = 'atlas://data/smartPauseRed/off'
            # self.source = 'data/off.png'
            self.flag = 0

    def on_enter(self, *args):
        if self.flag == 0:
            self.source = 'atlas://data/smartPauseRed/offhover'
            # self.source = 'data/mid.jpg'
        else:
            self.source = 'atlas://data/smartPauseRed/onhover'
            # self.source = 'data/mid.jpg'

    def on_leave(self, *args):
        if self.flag == 0:
            self.source = 'atlas://data/smartPauseRed/off'
            # self.source = 'data/off.png'
        else:
            self.source = 'atlas://data/smartPauseRed/on'
            # self.source = 'data/on.png'


class FlatTextInput2(TextInput):

    def __init__(self, **kargs):
        if 'background_color' not in kargs.keys():
            kargs['background_color'] = [0, 0, 0, 0]
        super(FlatTextInput2, self).__init__(**kargs)


class Search(FloatLayout):

    def __init__(self, **kwargs):
        super(Search, self).__init__(**kwargs)
        self.flag = 0

        # user_input = TextInput()
        self.user_input = MDTextField(multiline=False, font_size=23)
        self.user_input.hint_text = 'Song Name'
        self.add_widget(self.user_input)
        self.user_input.size_hint = (0.55, 0.115)
        self.user_input.pos_hint = {'x': .07, 'y': .47}
        name = getName()
        print "Current ", name
        if name != '':
            name = name.strip()
            if name[-4:] == 'webm':
                name = name[:-1]
            name = name[:-4]
            self.user_input.text = name
            sleep(0.01)                 # To make the next line always work.
            self.user_input.cursor = (0, 0)

    def update(self):
        status = getStatus()
        if status:
            name = getName()
            name = name.strip()
            if name[-4:] == 'webm':
                name = name[:-1]
            name = name[:-4]
            self.user_input.text = name
            sleep(0.01)                 # To make the next line always work.
            self.user_input.cursor = (0, 0)
        else:
            try:
                name = requests.get('http://127.0.0.1:5000/getSong').text
                name = name.strip("'b")
                self.user_input.text = name
            except:
                pass


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
        if value == 0:                       # It is going to onpress of ImageButton class first
            self.smartPause = True
            print "Smart Pause on."
            root.wmplabelid.color = (0, 0, 0, 1)
            root.vlclabelid.color = (0, 0, 0, 1)
            root.ytlabel.color = (0, 0, 0, 1)
            self.player = smartVlc()
        else:
            stopthread = Thread(target=self.player.stop)
            stopthread.daemon = True
            stopthread.start()
            stopthread.join()
            root.vid.active = False
            root.wid.active = False
            root.wmplabelid.color = (0, 0, 0, 0.6)
            root.vlclabelid.color = (0, 0, 0, 0.6)
            root.ytlabel.color = (0, 0, 0, 0.6)
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
                telethread = Thread(target=self.telegramHelper, args=(instance,))
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

    def Switch_on_VLC(self, instance, value, instance2, instance3):
        print "VLC switched."
        sleep(0.01)
        if self.smartPause and value is True:
            print("Switch On VLC")
            self.curr_player = 'vlc'
            instance2.active = False
            sleep(0.01)
            self.player = smartVlc()
            val = self.player.connect('vlc')
            if not val:
                self.player.stop()
                instance.active = False
            else:
                vthread = Thread(target=self.player.start)
                vthread.daemon = True
                vthread.start()
        elif self.smartPause and value is False:
            print("Switch Off VLC")
            if self.curr_player == 'vlc':
                try:
                    self.player.stop()
                except:
                    pass
                self.curr_player = None
        elif self.smartPause is False:
            instance.active = False
            if self.curr_player == 'vlc':
                print "Switch off VLC."
                try:
                    self.player.stop()
                except:
                    pass
                self.curr_player = None

    def Switch_on_YouTube(self, instance, value, instance2, instance3):
        if self.smartPause and value is True:
            print "Switch on youtube"
            self.curr_player = 'ytube'
            instance2.active = False
            instance3.active = False
            sleep(0.01)
            self.player.connect('ytube')
            y2thread = Thread(target=self.player.start)
            y2thread.daemon = True
            y2thread.start()
        elif self.smartPause and value is True:
            print "Switch off youtube"
            if self.curr_player == 'ytube':
                self.player.stop()
                self.curr_player = None
        elif self.smartPause is False:
            instance.active = False
            if self.curr_player == 'ytube':
                print "Switch off youtube."
                self.player.stop()
                self.curr_player = None
        elif value is False:
            if self.curr_player == 'ytube':
                print "Switch off YouTube."
                self.player.stop()
                self.curr_player = None

    def Switch_on_WMP(self, instance, value, instance2, instance3):
        if self.smartPause and value is True:
            print("Switch On WMP")
            self.curr_player = 'wmp'
            instance2.active = False
            sleep(0.01)
            self.player = smartVlc()
            self.player.connect('wmp')
            v2thread = Thread(target=self.player.start)
            v2thread.daemon = True
            v2thread.start()
        elif self.smartPause and value is False:
            print "Switch off WMP"
            if self.curr_player == 'wmp':
                try:
                    self.player.stop()
                except:
                    pass
                self.curr_player = None
        elif self.smartPause is False:
            instance.active = False
            if self.curr_player == 'wmp':
                print "Switch off WMP."
                try:
                    self.player.stop()
                except:
                    pass
                self.curr_player = None

    def Switch_on_Prediction(self, instance, value):
        print value

    def downloadsubhelper(self, name, path):
        q4 = Queue()
        new = Subtitle(name, path, q4)
        subReturn = q4.get()
        if not subReturn[0]:
            Snackbar.make("Unable to connect to Internet.")
            return
        try:
            q2 = Queue()
            sthread = Thread(target=new.download, args=(q2,))
            sthread.daemon = True
            sthread.start()
            sthread.join(timeout=60)
        except:
            print "Can't download Subtitle."
            Snackbar.make("Subtitle not Downloaded.")
            return
        result = None
        try:
            result = q2.get()
        except:
            pass
        if result:
            print "Subtitle Downloaded"
            self.sub = True
            Snackbar.make("Subtitle Downloaded Successfully :-)")
        else:
            print 'Subtitle not Downloaded.'
            Snackbar.make("Subtitle not found, Sorry!")
            self.sub = False

    def downloadsub(self):
        name, path = getNamePath()
        print name, path
        if name == '':
            return
        if name == self.subname and self.sub:
            print "Subtitle Already Downloaded."
            Snackbar.make("Subtitle Already Downloaded")
            return
        if name != self.subname:
            self.sub = False
        Snackbar.make("Searching for Subtitle")
        self.subname = name
        subthread = Thread(target=self.downloadsubhelper, args=(name, path))
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
        self.lyrics2.cursor = (0, 0)

    def loadLyrics(self, song):
        if self.song == song and self.lyrics != 'Sorry, Lyrics not found.':
            return
        else:
            self.song = song
            self.lyrics2.text = "Loading Lyrics for " + song + " ..."
            print "Loading Lyrics for " + song + " ..."
            threadl = Thread(target=self.loadLyricshelper, args=(song,))
            threadl.daemon = True
            threadl.start()


class HelpScreen(Screen):

    def __init__(self, *args, **kwargs):
        super(HelpScreen, self).__init__(*args, **kwargs)
        self.help_text = '''\nAdroit enhances your media viewing experience with its awesome UI and loads of features. :-)
Have you ever thought how nice it would be if your player can sense you looking at the screen and pause when you are looking away. Adroit lets you do that simply by enabling smart pause.\
 You can use the smart pause for VLC, WMP as well as whille watching videos on youtube.
Doesn't it becomes a nuisance when you are doing something important and the playlist stops? Not anymore. Adroit takes over your playlist and never let the music stop. If the current playing song\
 is last in the playlist it adds a new song based on your past behaviour. Adroit becomes intellligent with time as it understands you better. Based on what kind of songs you listen based on day and time of\
 day it automatically tunes it recommendations. Don't like the song? Just skip it and Adroit will know.
You can use the lyrics feature to instantly get the lyrics of whatever song you want saving you hassle of searching on the internet.
You can also download the subtitle of movie or TV series episode you are playing.  And as the subtitles are retrieved with the help of the hash you can rest asure about its syncing.
Not only this you can also turn on the Telegram feature of Adroit and use the telegram messenger in your mobile to control your media remotely by just chatting with Adroit.\
 You can also send lyrics to the bot to get the lyrics of whatever song is being played locally or on youtube.
Never thought it would be this simple, right?
Developer:- Tushar Tripathi
Designer:- Harshil Chaudhary
BITS Pilani'''


class Adroit2App(App):
    theme_cls = ThemeManager()
    theme_cls.primary_palette = 'Red'
    # def build(self):
    #     Window.borderless = True


if __name__ == '__main__':
    logfile = open('logger.log', 'w')
    logfile.close()
    logging.basicConfig(filename='logger.log', level=logging.DEBUG)
    ytube = ytubePlayer()
    ythread = Thread(target=ytube.start)
    ythread.daemon = True
    ythread.start()
    # sys.stdout = logfile
    Adroit2App().run()
    ytube.stop()
