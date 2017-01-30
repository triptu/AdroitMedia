from vlcclient import VLCClient as vc



vlc = vc("::1")
vlc.connect()

# def getName(info):



# def getPath(info):


print vlc.info()
# print getName(vlc.info())
# print getPath(vlc.info())
