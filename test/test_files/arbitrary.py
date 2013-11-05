import os
import time
import sublime

def run():
    time.sleep(1)
    f = open('%s', 'w')
    f.write('hello world')
    f.close()

    # if os.environ.get('SUBLIME_AUTO_KILL'):
    #     sublime.run_command('exit')
