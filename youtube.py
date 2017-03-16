import socket
import logging
from time import sleep

LOG_FILENAME = 'logger.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
# define socket address
TCP_IP = '127.0.0.1'  # consider all possible incoming IPs
TCP_PORT = 5000  # port used for communicating with the client
BUFFER_SIZE = 4096  # buffer size used when receiving data


class ytubePlayer():

    def __init__(self):
        self.running = True
        self.song = ''
        self.status = 'random'
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((TCP_IP, TCP_PORT))
            logging.debug("Socket server created. Waiting for connection.")
        except:
            logging.critical("Failed to create socket. Maybe firewall problem. Please Give permissions.")

    def start(self):
        self.running = True
        self.server.listen(5)
        while self.running:
            try:
                conn, addr = self.server.accept()
                msg = conn.recv(BUFFER_SIZE)
            except:
                break
            if not msg:
                break
            msg = msg.strip().split('\n')[0]
            msg = msg.strip().rstrip('HTTP/1.1 ')
            if 'favicon' in msg:
                conn.close()
                continue
            server_message = 'HTTP/1.1 200 OK\n\n%s' % 'True'
            if 'getstatus' in msg:
                server_message = 'HTTP/1.1 200 OK\n\n%s' % self.status
            elif 'song=' in msg:
                msg = msg.strip(' /').split('=')[1]
                msg = msg.replace('%20', ' ')
                msg = msg.replace('%22', '"')
                self.song = msg.strip()
            elif 'getSong' in msg:
                server_message = 'HTTP/1.1 200 OK\n\n%s' % self.get_current()
            elif 'setplay' in msg:
                self.play()
            elif 'setpause' in msg:
                self.pause()
            # print msg
            # send message to client
            conn.send(server_message)
            conn.close()

    def play(self):
        logging.debug("Youtube Play")
        self.status = 'play'

    def pause(self):
        logging.debug("Youtube pause")
        self.status = 'pause'

    def get_current(self):
        logging.debug('Get current song on youtube')
        return self.song

    def stop(self):
        self.running = 'False'
        self.status = 'False'
        self.server.close()
        sleep(0.1)


if __name__ == '__main__':
    ytube = ytubePlayer()
    ytube.start()
    ytube.stop()
