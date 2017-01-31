from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton


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
        self.user_input.size_hint = (0.5, 0.09)
        self.user_input.pos_hint = {'x':.4, 'y':.68}

        def on_enter(instance):
            print instance.text


        self.user_input.bind(on_text_validate=on_enter)


# Declare both screens
class LandingScreen(Screen):

    def __init__(self, *args, **kwargs):
        super(LandingScreen, self).__init__(*args, **kwargs)
        self.smartPause = False

    def controlSmartPause(self, value, root):
        if value==0:                       # It is going to onpress of ImageButton class first
            self.smartPause = True
            print "Smart Pause on."
        else:
            root.vid.active = False
            root.wid.active = False
            self.smartPause = False
            print "Smart Pause off."

    def Switch_on_Telegram(self, instance, value):
        if value is True:
            print("Switch On Telegram")
        else:
            print("Switch Off Telegram")

    def Switch_on_VLC(self, instance, value, instance2):
        if self.smartPause and value is True:
            print("Switch On VLC")
            instance2.active = False
        else:
            instance.active = False
            if self.smartPause:
                print("Switch Off VLC")

    def Switch_on_WMP(self, instance, value, instance2):
        if self.smartPause and value is True:
            print("Switch On WMP")
            instance2.active = False
        else:
            instance.active = False
            if self.smartPause:
                print("Switch Off WMP")

    def downloadsub(self):
        print "Downloading Subtitle"

class LyricsScreen(Screen):

    def loadLyrics(self, song):
        print "Searching lyrics of ", song
        self.lyrics2.text = "Loading Lyrics for " + song + " ..."
        #lyrics = getLyrics(song)
        #Change text to lyrics.

class HelpScreen(Screen):
    def __init__(self, *args, **kwargs):
        super(HelpScreen, self).__init__(*args, **kwargs)
        self.help_text = '''Adroit makes your media player smart! :-)
Adroit helps you do things in a simple way with its neat UI.

Have you ever thought how nice it would be if your player can sense you looking at the screen and pause when you are looking away. Adroit lets you do that simply by enabling smart pause.
You can use the lyrics feature to instantly get the lyrics of whatever song you want saving you hassle of searching on the internet.
You can also download the subtitle of movie or TV series episode you are playing.  And as the subtitles are retrieved with the help of the hash you can be suure about its syncing.
Not only this you can also turn on the Telegram feature of Adroit and use the telegram messenger in your mobile to control your media remotely by just chatting with Adroit.
Never thought it would be this simple, right?
The commands available with Adroit bot are- play,pause,next,prev,vup,vdown,fscreen,rfscreen.
You just have to setup a bot following these steps https://core.telegram.org/bots#6-botfather and write the api token in api.txt.


"Adroit" - Let the revolution begin.
Version 1.0
Creators - Tushar Tripathi, Harshil Chaudhary'''

class AdroitApp(App):
    pass

if __name__ == '__main__':
    AdroitApp().run()
