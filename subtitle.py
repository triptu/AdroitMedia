from xmlrpclib import ServerProxy
import base64, zlib, struct
import os


class Settings(object):
    OPENSUBTITLES_SERVER = 'http://api.opensubtitles.org/xml-rpc'
    USER_AGENT = 'OSTestUserAgentTemp'
    LANGUAGE = 'en'


class File(object):
    def __init__(self, path):
        self.path = path
        self.size = str(os.path.getsize(path))

    def get_hash(self):
        '''Original from: http://goo.gl/qqfM0
        '''
        longlongformat = 'q'  # long long
        bytesize = struct.calcsize(longlongformat)

        try:
            f = open(self.path, "rb")
        except(IOError):
            return "IOError"

        hash = int(self.size)

        if int(self.size) < 65536 * 2:
            return "SizeError"

        for x in range(65536 // bytesize):
            buffer = f.read(bytesize)
            (l_value, ) = struct.unpack(longlongformat, buffer)
            hash += l_value
            hash = hash & 0xFFFFFFFFFFFFFFFF  # to remain as 64bit number

        f.seek(max(0, int(self.size) - 65536), 0)
        for x in range(65536 // bytesize):
            buffer = f.read(bytesize)
            (l_value, ) = struct.unpack(longlongformat, buffer)
            hash += l_value
            hash = hash & 0xFFFFFFFFFFFFFFFF

        f.close()
        returnedhash = "%016x" % hash
        return str(returnedhash)


class OpenSubtitles(object):
    '''OpenSubtitles API wrapper.

    Please check the official API documentation at:
    http://trac.opensubtitles.org/projects/opensubtitles/wiki/XMLRPC
    '''

    def __init__(self, language=None):
        self.xmlrpc = ServerProxy(Settings.OPENSUBTITLES_SERVER,
                                  allow_none=True)
        self.language = language or Settings.LANGUAGE
        self.token = None

    def _get_from_data_or_none(self, key):
        '''Return the key getted from data if the status is 200,
        otherwise return None.
        '''
        status = self.data.get('status').split()[0]
        return self.data.get(key) if '200' == status else None

    def login(self, username='', password=''):
        '''Returns token is login is ok, otherwise None.
        '''
        self.data = self.xmlrpc.LogIn(username, password,
                                 self.language, Settings.USER_AGENT)
        token = self._get_from_data_or_none('token')
        if token:
            self.token = token
        return token

    def logout(self):
        '''Returns True is logout is ok, otherwise None.
        '''
        data = self.xmlrpc.LogOut(self.token)
        return '200' in data.get('status')

    def search_subtitles(self, params, pathfile):
        '''Returns a list with the subtitles info.
        '''
        self.data = self.xmlrpc.SearchSubtitles(self.token, params)
        resp = self._get_from_data_or_none('data')
        if resp == None:
            return False
        subtitles = []
        for result in resp:
            if int(result['SubBad']) != 1:
                subtitles.append({'subid': result['IDSubtitleFile'],
                                  'hash': result['MovieHash']})
        if len(subtitles)==0:
            return False
        sub = self.download_subtitles(subtitles[0])
        if not sub:
            return False
        filename = pathfile + ".srt"
        file = open(filename, "wb")
        file.write(sub)
        file.close()
        return True

    def download_subtitles(self, subtitle):
        resp = self.xmlrpc.DownloadSubtitles(self.token, [subtitle['subid']])
        if resp['status'].upper() != '200 OK':
            return False
        decoded = base64.standard_b64decode(resp['data'][0]['data'].encode('ascii'))
        decompressed = zlib.decompress(decoded, 15 + 32)
        return decompressed

    def download_subtitle(self, name, path):
        try:
            fullpath = os.path.join(path, name)
            f = File(fullpath)
            hash = f.get_hash()
            size = f.size
            out = self.search_subtitles([{'sublanguageid': 'eng', 'moviehash': hash, 'moviebytesize': size}],\
                                         os.path.splitext(fullpath)[0])
            return out
        except Exception as e:
            print str(e)
            return False

class Subtitle:

    def __init__(self, name, path):
        self.path = path
        self.name = name
        self.opsub = OpenSubtitles()
        self.opsub.login()

    def download(self):
        val =  self.opsub.download_subtitle(self.name, self.path)
        self.opsub.logout()
        return val


if __name__ == '__main__':
    path = "C:\Users\Tushar\Downloads\python-opensubtitles-master\python-opensubtitles-master\pythonopensubtitles"
    name = "Deadpool.2016.720p.BluRay.x264.YIFY[God.Of.Atheists].mp4"
    sub = Subtitle(name, path)
    print "Downloading Subtitle", sub.download()

