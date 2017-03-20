from __future__ import unicode_literals
from vlcclient import VLCClient
from BasicInfo import getNamePath
import os
import datetime
import random
from time import sleep
from update_db import updateNew
import sqlite3

record = {}
dbName = 'data/learn.db'
day = datetime.datetime.today().weekday()
hour = datetime.datetime.today().hour
if hour < 17 and hour > 10:
    if day < 5:
        slot = 'MF1'
        pos = 1
    else:
        slot = 'SS1'
        pos = 3
else:
    if day < 5:
        slot = 'MF2'
        pos = 2
    else:
        slot = 'SS2'
        pos = 4


times = ['MF1', 'SS1', 'MF2', 'SS2']

songs = []
prob = []
tot = 0


def addNew(hash2, fullpath):
    temp = str(hash2)
    c.execute("INSERT INTO songs (keyword, spath, MF1, MF2, SS1, SS2) VALUES (?, ?, ?, ?, ?, ?)",
              (temp, fullpath, 10, 10, 10, 10))


def update(offset, full=None):
    if not full:
        full = getNamePath()
    song = os.path.join(full[1], full[0])
    full = song.replace('/', '\\')
    hash2 = str(hash(full))
    if hash2 not in record:
        addNew(hash2, full)
        record[hash2] = [hash2, 10, 10, 10, 10, full]
    c.execute('SELECT * FROM songs WHERE keyword = ?', (hash2,))
    data = c.fetchall()
    pars = []
    for beer in data:
        pars = list(beer)
    pars[pos] = str(float(pars[pos]) + offset)
    c.execute('UPDATE songs SET {} = ? WHERE keyword = ?'.format(times[pos - 1]), (pars[pos], hash2))


def makeFalse():
    global prediction
    prediction = False


def makeTrue():
    global prediction
    prediction = True


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
        while prediction:
            sleep(1)
            try:
                if vconnected is False:
                    vlc = VLCClient("::1")
                    vlc.connect()
                    vconnected = True
                if prevfullpath == '':
                    prevfullpath = getNamePath()
                    prev_song = vlc.get_title()
                curr_song = vlc.get_title()
                if curr_song == prev_song:
                    if not(updated):
                        try:
                            totlen = int(vlc.get_length())
                        except:    # No song queued
                            return False
                        elapsed = int(vlc.get_time())
                        if elapsed > 0.75 * totlen:
                            update(1)
                            print "Updating for", prev_song, "with offset", 1
                            updated = True
                else:
                    if updated is False:
                        if elapsed < 0.5 * totlen:
                            update(-0.5, prevfullpath)
                            print "Updating for", prev_song, "with offset", -0.5
                    prev_song = curr_song
                    prevfullpath = getNamePath()
                    updated = False
                if vlc.get_title() in vlc.playlist().split('\n')[-3]:
                    # It means this song is the last in playlist
                    totlen = int(vlc.get_length())
                    elapsed = int(vlc.get_time())
                    if elapsed > 1:
                        print "Going to add new song."
                        # numpy.random.choice(songs, probability=songs)
                        nextSong = random.choice(songs)
                        nextSong = nextSong[-1]
                        print "Next Song-", nextSong
                        if os.path.exists(nextSong):
                            vlc.enqueue(nextSong)
                        else:
                            while not(os.path.exists(nextSong)):
                                print "Oops! Some problem occured."
                                sleep(0.2)
                                nextSong = random.choice(songs)
                                nextSong = nextSong[-1]
                                print "New Next Song-", nextSong
                            vlc.enqueue(nextSong)

            except Exception as e:
                print str(e)
                break


class PlayPrediction():

    def main(self):
        global prediction, SONG_PATH, conn, c, record, songs, tot, vlc, vconnected
        vlc = VLCClient("::1")
        vconnected = False
        try:
            vlc.connect()
            vconnected = True
        except:
            print "VLC not connected. :-("
            return False
        prediction = True
        SONG_PATH = ''
        with open('data/songfolder.txt') as handle:
            for line in handle:
                SONG_PATH = line.strip()
                break
        if not os.path.exists(SONG_PATH):
            print "Song Folder path doesn't exist."
            return False
        SONG_PATH = unicode(SONG_PATH)
        print SONG_PATH
        updateNew(SONG_PATH)
        conn = sqlite3.connect(dbName)
        c = conn.cursor()
        c.execute('SELECT * FROM songs')
        data = c.fetchall()
        for row in data:
            pars = list(row)
            # print pars
            record[int(pars[0])] = pars[1:]
            if float(pars[pos]) > 8.5:
                songs.append((pars[pos], pars[0], pars[1]))
                tot += 1
        songs.sort()
        for song in songs:
            prob.append(float(song[0]) / tot)

        smartPlaylist()
        c.close()
        conn.close()

    def stop(self):
        global prediction
        print "Play Prediction Turned off."
        prediction = False
