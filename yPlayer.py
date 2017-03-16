import requests


class ytubePlayer():

    def play(self):
        print "Youtube Play"
        requests.get('http://127.0.0.1:5000/setplay')

    def pause(self):
        print "Youtube pause"
        requests.get('http://127.0.0.1:5000/setpause')

    def status(status):
        return True

    def disconnect(self):
        return True
