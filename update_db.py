from __future__ import unicode_literals
import os
import sys
import sqlite3
from time import time

start = time()

reload(sys)
sys.setdefaultencoding('utf8')
dbName = 'data\learn.db'

SUPPORTED = ['mp3', 'm4a', 'mp4', 'webm', '3gp', 'mkv', 'mpg', 'mpeg', 'flv', 'avi']
# format (hash, MF1, MF2, SS1, SS2, sentiment)


def updateNew(path):
    delete()
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS songs(keyword TEXT, spath TEXT, MF1 REAL, MF2 REAL, SS1 REAL, SS2 REAL)')
    count = 0
    for folderName, subfolders, filenames in os.walk(path):
        # print('The current folder is ' + folderName)
        for filename in filenames:
            extension = os.path.splitext(filename)[1][1:]
            if extension.lower() in SUPPORTED:
                temp = unicode(os.path.join(folderName, filename))
                # handle.write('\n')
                c.execute("INSERT INTO songs (keyword, spath, MF1, MF2, SS1, SS2) VALUES (?, ?, ?, ?, ?, ?)",
                          (unicode(hash(temp.strip())), temp, 10, 10, 10, 10))
                conn.commit()
                count += 1
    c.close()
    conn.close()
    print "Total Files", count
    print('')
    print "Time taken = ", time() - start


def delete():
    if os.path.exists(dbName):
        os.remove(dbName)


# updateNew('D:\DC++Share\Songs')
