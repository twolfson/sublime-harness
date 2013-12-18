import os
from urllib import urlencode
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
            req = urlopen('http://localhost:7070', data=urlencode({
                'level': level,
                'msg': msg
            }))
            req.read() # DEV: Stop open pipes from occurring
        except URLError:
            pass


logger = HttpLogger() if os.environ.get('HARNESS_LOGGER') else IgnorantLogger()
