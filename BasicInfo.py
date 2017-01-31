from vlcclient import VLCClient
import re

def getName(info):
    fullPath = re.compile(r'.*file:///(?P<Path>.*?)\)')
    if fullPath.match(info):
        Path = fullPath.match(info).group('Path')
        return Path.split('/')[-1]
    else:
        return False


def getPath(info):
    fullPath = re.compile(r'.*file:///(?P<Path>.*?)\.')
    if fullPath.match(info):
        Path = fullPath.match(info).group('Path')
        path = re.match(r'.*/', Path)
        return path.group(0)
    else:
        return False



if __name__ == '__main__':
    vlc = VLCClient("::1")
    vlc.connect()
    print "Playing - ", getName(vlc.status())
    print "Path - ", getPath(vlc.status())
    vlc.disconnect()
