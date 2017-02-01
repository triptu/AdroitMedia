from vlcclient import VLCClient
import re

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
        return ""
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

