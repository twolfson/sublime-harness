import os
import sublime

def run():
    with open('%s', 'w') as f:
        f.write(sublime.packages_path())

    if os.env.get('SUBLIME_AUTO_KILL'):
        sublime.run_command('exit')
