import os
import sublime
import time

def run():
    with open('%s', 'w') as f:
        f.write(str(time.time()))

    if os.environ.get('SUBLIME_AUTO_KILL'):
        sublime.run_command('exit')
