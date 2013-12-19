# TODO: Consider using https://pypi.python.org/pypi/wsgilog/0.3
import BaseHTTPServer


# Create a server which logs POST body to stdout
class LogServer(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_POST(self):
        len = int(self.headers.getheader('content-length'))
        print self.rfile.read(len)
        self.send_response(200, 'Logged to stdout')


# Create our server
app = BaseHTTPServer.HTTPServer(('', 7070), LogServer)
app.serve_forever()
