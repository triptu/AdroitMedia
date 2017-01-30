from __future__ import unicode_literals
import requests, os, subprocess
from bs4 import BeautifulSoup as bs

def scrape(url):

    r=requests.get(url)
    soup=bs(r.text, "html.parser")

    s=soup.find('div', id="lyrics-body-text")
    title = soup.find('h1', style="font-size:2.3em;").text.strip().replace('Lyrics','')
    lyrics = s.text
    print "Lyrics fetched from metrolyrics."
    print "\n\n\n%s\n" %(title)
    print lyrics

    path= 'D:\\DC++Share\\Songs\\pyDirect\\Lyrics'
    os.chdir(path)

    name = title + '.txt'

    with open(name, 'w') as handle:
        handle.write(title.encode('utf8'))
        handle.write('\n\n')
        handle.write(lyrics.encode('utf8'))

    p = subprocess.Popen(name, shell=True)
    #subprocess.Popen("TASKKILL /F /PID {pid}".format(pid=p.pid))
    return None


if __name__ == '__main__':
    url = raw_input("Enter the url of lyrics of song from metrolyrics.>>> ")
    scrape(url)

