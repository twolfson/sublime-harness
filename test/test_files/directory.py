import os
import sublime

try :
    from hello import hello
except:
    from .hello import hello

def run():
    with open('%s', 'w') as f:
        f.write(hello)
