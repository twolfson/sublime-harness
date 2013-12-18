import os
try:
    from urllib.request import urlopen
    from urllib.error import URLError
except ImportError:
    from urllib2 import urlopen, URLError

# TODO: Consider using a proper logger
class IgnorantLogger(object):
    def _log(self, level, msg):
        pass

    def debug(self, msg):
        self._log('debug', msg)

    def info(self, msg):
        self._log('info', msg)

    def warn(self, msg):
        self._log('warn', msg)


# TODO: Robustify this with port and address
class HttpLogger(IgnorantLogger):
    def _log(self, level, msg):
        try:
            # TODO: This is horrible string interpolation
            req = urlopen('http://localhost:7070', data='level={}&msg={}'.format(level, msg))
            req.read() # DEV: Stop open pipes from occurring
        except URLError:
            pass


# TODO: This is really bad technique. We should be doing this based off of a factory.
# TODO: Then, inside of the place where we load the program we can use env var
logger = HttpLogger() if os.environ.get('HARNESS_LOGGER') else IgnorantLogger()
