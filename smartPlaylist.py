from vlcclient import VLCClient
from BasicInfo import getNamePath
import os
import datetime
import random
from time import sleep
record = {}
day = datetime.datetime.today().weekday()
hour = datetime.datetime.today().hour
if hour<17 and hour>10:
    if day<5:
        slot = 'MF1'
        pos = 1
    else:
        slot = 'SS1'
        pos = 3
else:
    if day<5:
        slot = 'MF2'
        pos = 2
    else:
        slot = 'SS2'
        pos = 4


songs = []
prob = []
tot = 0
with open('record.csv') as handle:
    for line in handle:
        line = line.strip()
        pars = line.split(',')
        record[int(pars[0])] = pars[1:]
        if float(pars[pos])>8.5:
            songs.append((pars[pos], pars[0], pars[-1]))
            tot+=1

songs.sort()
for song in songs:
    prob.append(float(song[0])/tot)


def addNew(hash2, fullpath, sentiment=0.5):
    with open('record.csv', 'a') as handle:
        handle.write(str(hash2)+',10,10,10,10,0.5,'+fullpath+'\n')

def update(offset, full =None):
    if not full:
        full = getNamePath()
    song = os.path.join(full[1], full[0])
    full = song.replace('/','\\')
    hash2 = str(hash(full))
    if hash2 not in record:
        addNew(hash2, full)
        record[hash2] = [hash2,10,10,10,10,0.5, full]
    handle2 = open('record2.csv', 'w')
    with open('record.csv', 'a+') as handle:
        for line in handle:
            line = line.strip()
            pars = line.split(',')
            if hash2 == pars[0]:
                pars[pos] = str(float(pars[pos]) + offset)
                record[hash2][pos-1] = str(float(pars[pos]) + offset)
                line = ",".join(pars)
            handle2.write(line+'\n')
    handle2.close()
    os.remove('record.csv')
    os.rename('record2.csv', 'record.csv')


prediction = True

def makeFalse():
    global prediction
    prediction = False

def makeTrue():
    global prediction
    prediction = True

vlc = VLCClient("::1")
vconnected = False
try:
    vlc.connect()
    vconnected = True
except:
    pass
def smartPlaylist():
    print 'Started'
    global vconnected
    prev_song = ''
    updated = False
    prevfullpath = ''
    try:
        vlc = VLCClient("::1")
        vlc.connect()
        vconnected = True
    except:
        vconnected = False
    if True:
        while True:
            sleep(1)
            try:
                if vconnected == False:
                    vlc = VLCClient("::1")
                    vlc.connect()
                    vconnected = True
                if prevfullpath == '':
                    prevfullpath = getNamePath()
                    prev_song = vlc.get_title()
                curr_song = vlc.get_title()
                if curr_song==prev_song:
                    if not(updated):
                        totlen = int(vlc.get_length())
                        elapsed = int(vlc.get_time())
                        if elapsed>0.75*totlen:
                            update(1)
                            print "Updating for", prev_song, "with offset", 1
                            updated = True
                else:
                    prev_song = curr_song
                    if updated == False:
                        if elapsed<0.5*totlen:
                            update(-0.5, prevfullpath)
                            print "Updating for", prev_song, "with offset", -0.5
                    prevfullpath = getNamePath()
                    updated = False
                if vlc.get_title() in vlc.playlist().split('\n')[-3]:
                    # It means this song is the last in playlist
                    totlen = int(vlc.get_length())
                    elapsed = int(vlc.get_time())
                    if elapsed>1:
                        print "Going to add new song."
                        # numpy.random.choice(songs, probability=songs)
                        nextSong = random.choice(songs)
                        print nextSong
                        nextSong = nextSong[-1]
                        print nextSong
                        if os.path.exists(nextSong):
                            vlc.enqueue(nextSong)
                        else:
                            while not(os.path.exists(nextSong)):
                                nextSong = random.choice(songs)
                                print nextSong
                                nextSong = nextSong[-1]
                            vlc.enqueue(nextSong)

            except Exception as e:
                print str(e)
                break

if __name__ == '__main__':
    smartPlaylist()


