import requests, json
from vlcclient import VLCClient
from lyrics import getLyrics
from threading import Thread
from BasicInfo import getName
from queue import Queue

class NetworkError(Exception):
    pass

class VLCConnectionError(Exception):
    pass

# token = 'bot238441806:AAHC5l1Bm3kvR38Ap-WsPYBmq0i7EaMXvHA'
token = ''
with open('data/token.txt') as f:
    for line in f:
        token = line
        break

class Telegram():

    def __init__(self):
        self.running = True
        self.vlc = VLCClient("::1")
        self.base = "https://api.telegram.org/bot%s/" %token
        try:
            self.vlc.connect()
        except:
            raise VLCConnectionError

    def get(self, command, payload=None):
        try:
            r=requests.get(self.base+command, params=payload)
        except:
            raise NetworkError
        return json.loads(r.text)

    def start(self):
        updates = self.get('getupdates')
        while self.running:
            try:
                self.vlc.status()
            except:
                raise VLCConnectionError
            if updates['result']!=[]:
                offset = updates['result'][-1]['update_id']
                payload = {"offset" : offset+1}
            else:
                payload = None
            updates = self.get('getupdates', payload)
            if updates['result']!=[]:
                for result in updates['result']:
                    message = result['message']['text']
                    user_id = result['message']['from']['id']

                    # Replying
                    reply = self.action(message)
                    if reply:
                        payload = {'text':reply, 'chat_id':str(user_id)}
                        send_msg = self.get('sendmessage', payload)
                        if reply == send_msg['result']['text']:
                            pass    # Success

    def action(self, msg):
        msg = msg.lower().strip()
        try:
            if msg == 'play':
                self.vlc.play()
            elif msg == 'pause':
                self.vlc.pause()
            elif msg == 'stop':
                self.vlc.stop()
            elif msg == 'next':
                self.vlc.next()
            elif msg == 'prev':
                self.vlc.prev()
            elif msg == 'fscreen':
                self.vlc.set_fullscreen(True)
            elif msg == 'rfscreen':
                self.vlc.set_fullscreen(False)
            elif msg == 'rewind':
                self.vlc.rewind()
            elif msg == 'volume':
                return "Current volume is", self.vlc.volume()
            elif msg == 'vup' or msg == 'volup':
                return "Current volume is", self.vlc.volup(2)
            elif msg == 'vdown' or msg == 'voldown':
                return "Current volume is", self.vlc.voldown(2)
            elif msg == 'help':
                 s = ''' Commands:-
Pause, play, stop, next, prev
vup- for volume Up
vdown - for volume down
fscreen - to set full screen
rfscreen - for reverse.
                 '''
                 return s
            elif msg == 'lyrics':
                q = Queue()
                song = getName()
                threadl = Thread(target = getLyrics, args=(song,q))
                threadl.daemon = True
                threadl.start()
                threadl.join()
                self.lyrics = q.get()
                return self.lyrics
            else:
                return "Invalid Command."
            return "Command executed successfully."
        except Exception as e:
            print "Error", str(e)
            raise VLCConnectionError

    def stop(self):
        try:
            self.vlc.disconnect()
        except:
            pass
        self.running = False
