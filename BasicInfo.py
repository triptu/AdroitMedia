from vlcclient import VLCClient
import re
from threading import Thread

def getName():
    vlc = VLCClient("::1")
    try:
        vlc.connect()
    except:
        return ""
    info = vlc.status()
    fullPath = re.compile(r'.*file:///(?P<Path>.*?) \).\n\( audio')
    vlc.disconnect()
    if fullPath.match(info):
        Path = fullPath.match(info).group('Path')
        return Path.split('/')[-1]
    else:
        return ""


def getNamePath():
    vlc = VLCClient("::1")
    try:
        vlc.connect()
    except:
        return '', ''
    info = vlc.status()
    fullPath = re.compile(r'.*file:///(?P<Path>.*?) \).\n\( audio')
    vlc.disconnect()
    if fullPath.match(info):
        Path = fullPath.match(info).group('Path')
        path = re.match(r'.*/', Path)
        name = Path.split('/')[-1]
        return name.strip(), path.group(0)
    else:
        return '', ''


def runChecker(vlc):
    try:
        vlc.connect()
    except:
        return False


def getStatus():
    vlc = VLCClient("::1")
    sThread = Thread(target=runChecker, args=(vlc,))
    sThread.daemon = True
    sThread.start()
    sThread.join(0.25)
    if sThread.isAlive:
        return False
    try:
        vlc.connect()
    except:
        return False
    temp = vlc.status().split()[-2]
    if str(temp).lower() == 'playing':
        return True
    else:
        return False
