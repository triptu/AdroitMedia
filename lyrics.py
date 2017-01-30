from __future__ import unicode_literals
import requests
from bs4 import BeautifulSoup as bs


supported = ['azlyrics',
             'metrolyrics',
             'lyricsmint',
             'glamsham',
             'allthelyrics']

def getLyrics(query):
    query += " lyrics"
    base  =  "https://www.google.co.in/search"
    r     =  requests.get(base, params={'q':query})
    soup  =  bs(r.text, "html.parser")
    tags  =  soup.find_all('h3')
    url   =  ''

    for i in range(5):
        url= "https://www.google.co.in/" + tags[0].contents[0]['href']
        for site in supported:
            if site in url:
                break
        else:
            url = ''
            continue
        break

    if url == '':         # No supported site
        return False

    if 'azlyrics' in url:
        return azScrape(url)

    elif 'metrolyrics' in url:
        return metroScrape(url)

    elif 'lyricsmint' in url:
        return lyricsmintScrape(url)

    elif 'allthelyrics' in url:
        return allthelyricsScrape(url)

    elif 'glamsham Lyrics' in url:
        return glamshamScrape(url)

    else:
        return False


def azScrape(url):
    # Faking user agent using headers as azlyrics blocks scraper scripts.
    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }
    r=requests.get(url, headers=headers)
    soup=bs(r.text, "html.parser")
    t = soup.find_all('div', {'class':'div-share'})[1].findChild()
    title = t.contents[0].strip('').replace('"','').replace('lyrics','')
    s = soup.find_all('div')
    lyrics = s[22].text.strip()
    s = "\n%s\n\n" %(title)
    s += lyrics
    return s


def metroScrape(url):
    r=requests.get(url)
    soup=bs(r.text, "html.parser")
    s=soup.find('div', id="lyrics-body-text")
    title = soup.find('h1', style="font-size:2.3em;").text.strip().replace('Lyrics','')
    lyrics = s.text
    # print "Lyrics fetched from metrolyrics."
    s = "\n%s\n\n" %(title)
    s += lyrics
    return s


def lyricsmintScrape(url):
    r=requests.get(url)
    soup=bs(r.text, "html.parser")
    s=soup.find('div', id="lyric")
    s = unicode(s)
    # print type(s)
    items=['<br/>', '<p>', '</p>', '<div id="lyric"><h2>', 'Lyrics</h2>',\
           '<i><b>', '</b></i>', '</div>']
    replacements=['\n', '\n', '\n', '', '\n', 'By-', '', '']
    for i, item in enumerate(items):
        try:
            s=s.replace(item, replacements[i])
        except Exception as e:
            print "Error- ", e
    title = soup.find('h2').text.strip().replace('Lyrics','')
    return s


def allthelyricsScrape(url):
    r=requests.get(url)
    soup=bs(r.text, "html.parser")
    s=soup.find('div', class_ = "content-text-inner")
    title = soup.find('h1', class_ = "page-title").text
    lyrics = s.text.strip()
    return title + '\n' + lyrics

def glamshamScrape(url):

    r=requests.get(url)
    soup=bs(r.text, "html.parser")

    s=soup.find('div', class_ = "col-sm-6")
    s = unicode(s)
    title = soup.find('font', class_ = "general").text
    title = title[7:]
    items=['<br>', '<div class="col-sm-6">', '<font class="general">', '</br>', '/div', '/font', '<>']
    replacements=['\n', '', '', '', '', '', '']
    for i, item in enumerate(items):
        try:
            s = s.replace(item, replacements[i])
        except Exception as e:
            print "Error- ", e
    lyrics = s.strip()
    return title + '\n' + lyrics

print getLyrics("Thinking out loud")
