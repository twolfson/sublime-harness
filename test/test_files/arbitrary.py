import os
import sublime

def run():
    with open('%s', 'w') as f:
        f.write('hello world')
