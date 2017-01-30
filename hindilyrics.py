import requests, os, subprocess
from bs4 import BeautifulSoup as bs

def scrape(url):

    r=requests.get(url)
    soup=bs(r.text, "html.parser")

    s=soup.find('font', face='verdana')
    title = soup.find('h5').text
    lyrics = s.text.replace('\r ', '\n').strip()
    print "Lyrics fetched from 'hindilyrics.net'.\n\n"
    print title, '\n'
    print lyrics

    path= 'D:\\DC++Share\\Songs\\pyDirect\\Lyrics\\Hindi'
    os.chdir(path)

    name = title + '.txt'

    with open(name, 'w') as handle:
        handle.write(title+'\n\n')
        handle.write(lyrics)

    p = subprocess.Popen(name, shell=True)
    #subprocess.Popen("TASKKILL /F /PID {pid}".format(pid=p.pid))
    return None


if __name__ == '__main__':
    url = raw_input("Enter the url of lyrics of song from hindilyrics.>>> ")
    scrape(url)

