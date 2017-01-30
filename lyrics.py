''''Open the webpage with lyrics of a song.
Usage - 3 ways to use :-
1. Run the program- enter the song name when asked.
2. Run the program from command line and give the argument then
   with space. eg. lyrics thinking out loud
3. Copy the song run the program from cmd or run and
   suffix it with '/'. eg "lyrics /" (without quotes)
'''


import requests, sys, webbrowser, pyperclip, subprocess
from bs4 import BeautifulSoup as bs
import azscraper, metroscraper, lyricsmint, hindilyrics
from subprocess import check_output
from time import sleep

def get_pid():
    ''' Logic:- tasklist gives the tasks in order they are opened. Running the program
    will open a cmd prompt. Now if we immediately just after running the script check
    the processes then the last cmd.exe will be what is opened by this program.
    So we will get the pid which we will close at last.'''
    a = check_output(["tasklist"])
    p = a.replace('\r', '').split('\n')[3:-2]
    for i in range(-1, -len(p), -1):
        if "cmd.exe" in p[i]:
            return int(p[i].split()[1])


supported = ['azlyrics',
             'metrolyrics',
             'lyricsmint',
             'hindilyrics']

def openUrl(query):
    query+=" lyrics"
    base="https://www.google.co.in/search"
    r=requests.get(base, params={'q':query})
    soup=bs(r.text, "html.parser")
    tags=soup.find_all('h3')
    url= "https://www.google.co.in/" + tags[0].contents[0]['href']

    for site in supported:
        if site in url:
            break
    else:
        url= "https://www.google.co.in/" + tags[1].contents[0]['href']

    if 'azlyrics' in url:
        azscraper.scrape(url)

    elif 'metrolyrics' in url:
        metroscraper.scrape(url)

    elif 'lyricsmint' in url:
        lyricsmint.scrape(url)

    elif 'hindilyrics.net' in url:
        hindilyrics.scrape(url)

    else:
        webbrowser.open(url)



if __name__=="__main__":
    try:
        sys.argv[1]         # Checks if cmd line argument is given
        query= " ".join(sys.argv[1:])
    except:
        if "idlelib" in sys.modules:
            query = raw_input("Enter the song's name. - ")
        else:
            query=pyperclip.paste()
    print query
    openUrl(query)
    pid = get_pid()
    subprocess.Popen("TASKKILL /F /PID {pid}".format(pid=pid))
