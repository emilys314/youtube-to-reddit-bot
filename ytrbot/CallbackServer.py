from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import re
from multiprocessing import Process, Queue

# Subclass HTTPServer with some additional callbacks
class CallbackHTTPServer(HTTPServer):

    def server_activate(self):
        self.RequestHandlerClass.pre_start()
        HTTPServer.server_activate(self)
        self.RequestHandlerClass.post_start()

    def server_close(self):
        self.RequestHandlerClass.pre_stop()
        HTTPServer.server_close(self)
        self.RequestHandlerClass.post_stop()


# HTTP request handler
class HttpHandler(BaseHTTPRequestHandler):

    @classmethod
    def pre_start(cls):
        print('## Before calling socket.listen() ##')

    @classmethod
    def post_start(cls):
        print('## After calling socket.listen() ##')

    @classmethod
    def pre_stop(cls):
        print('## Before calling socket.close() ##')

    @classmethod
    def post_stop(cls):
        print('## After calling socket.close() ##')

    def do_GET(self):
        print("## I have just recieved a GET request ##")
        path = str(self.path)
        channel = path[path.find("channel_id%3D")+len("channel_id%3D"):path.rfind("&hub.challenge")]
        print("From channel: ", channel)
        #print(path)
        #print(self.headers)

        start = "hub.challenge="
        end = "&hub.mode"
        #print("header.find:",header.find('hub.challenge='),"  header.rfind:",header.rfind('&hub.mode'))
        challengeString = path[path.find(start)+len(start):path.rfind(end)]
        #print(challengeString)

#        print(self.rfile.read())
        self.send_response(200)
        self.end_headers()
        self.wfile.write(challengeString.encode("utf8"))

    def do_POST(self):
        print("## I have just received an HTTP POST request ##")
        print("For channel: ", self.headers.get("Link"))
        print(self.path)
        print(self.headers)
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        print(post_body)
#        print(self.rfile.read())
        self.send_response(200)


class Upload():
    def __init__(self, message):
        message = message[message.find("<yt:channelId>"):]
        self.channel_id = message[message.find("<yt:channelId>")+len("<yt:channelId>"):message.rfind("</yt:channelId>")]
        self.title = message[message.find("<title>")+len("<title>"):message.rfind("</title>")]
        self.author = message[message.find("<name>")+len("<name>"):message.rfind("</name>")]
        self.url = message[message.find("href=\"")+len("href=\""):message.rfind("\"/>")]
        #print("Title",self.title,"Author",self.author,"channel",self.channel_id,"Url",self.url)

    def __str__(self):
        return ("("+self.channel_id+" "+self.title+" "+self.author+" "+self.url+")")


def start(queue):
    # Create server
    try:
        print ("## Creating server ##")
        server = CallbackHTTPServer(('10.0.0.150', 8000), HttpHandler)
    except KeyboardInterrupt:
        print ("## Server creation aborted ##")
        return

    # Start serving
    try:
        print ("## Calling serve_forever() ##")
        server.serve_forever()
    except KeyboardInterrupt:
        print ("## Calling server.server_close() ##")
        server.server_close()


def main():
    queue = Queue()
    start(queue)

if __name__ == '__main__':
    main()
