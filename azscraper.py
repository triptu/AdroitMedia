from __future__ import unicode_literals
import requests, os, subprocess
from time import sleep
from bs4 import BeautifulSoup as bs

def scrape(url):
    author = url.split('/')[-2]

    # Faking user agent using headers as azlyrics blocks scraper scripts.
    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }
    r=requests.get(url, headers=headers)
    soup=bs(r.text, "html.parser")
    t = soup.find_all('div', {'class':'div-share'})[1].findChild()
    title = t.contents[0].strip('').replace('"','').replace('lyrics','')
    s = soup.find_all('div')
    lyrics = s[22].text
    print "Lyrics fetched from azscraper."
    print "\n\n\n%s\n" %(title)
    try:
        print lyrics
    except:
        pass

    path= 'D:\\DC++Share\\Songs\\pyDirect\\Lyrics'
    os.chdir(path)

    name = '%s - %s.txt' %(title, author)
    with open(name, 'w') as handle:
        handle.write(title.encode('utf8'))
        handle.write(lyrics.encode('utf8'))

    print "Opening File now... ta da"
    subprocess.Popen(name, shell=True)


if __name__ == '__main__':
    url = raw_input("Enter the url of lyrics of song from azlyrics.>>> ")
    scrape(url)

