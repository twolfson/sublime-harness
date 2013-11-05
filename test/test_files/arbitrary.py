import os
import sublime

def run():
    with open('%s', 'w') as f:
        f.write('hello world')

    if os.environ.get('SUBLIME_AUTO_KILL'):
        sublime.run_command('exit')
