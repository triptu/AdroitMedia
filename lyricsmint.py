import requests, os, subprocess
from bs4 import BeautifulSoup as bs

s=""
def fetch(raw):
    items=['<br/>', '<p>', '</p>', '<div id="lyric"><h2>', 'Lyrics</h2>',\
           '<i><b>', '</b></i>', '</div>']
    replacements=['\n', '\n', '\n', '', '\n', 'By-', '', '']
    for i, item in enumerate(items):
        try:
            raw=raw.replace(item, replacements[i])
        except Exception as e:
            print "Error- ", e
    return raw

def scrape(url):
    global s
    r=requests.get(url)
    soup=bs(r.text, "html.parser")

    s=soup.find('div', id="lyric")
    title = soup.find('h2').text.strip().replace('Lyrics','')
    lyrics = fetch(str(s))
    print "Lyrics fetched from Lyricsmint."
    print lyrics

    path= 'D:\\DC++Share\\Songs\\pyDirect\\Lyrics\\Hindi'
    os.chdir(path)

    name = title + '.txt'

    with open(name, 'w') as handle:
        handle.write(lyrics)

    p = subprocess.Popen(name, shell=True)
    #subprocess.Popen("TASKKILL /F /PID {pid}".format(pid=p.pid))
    return None


if __name__ == '__main__':
    url = raw_input("Enter the url of lyrics of song from Lyricsmint.>>> ")
    scrape(url)

