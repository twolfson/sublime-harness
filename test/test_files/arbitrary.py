import os
import sublime

def run():
    f = open('%s', 'w')
    f.write('hello world')
    f.close()

    if os.environ.get('SUBLIME_AUTO_KILL'):
        sublime.run_command('exit')
