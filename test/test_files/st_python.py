import sublime

def run():
    with open('%s', 'w') as f:
        f.write(sublime.packages_path())
