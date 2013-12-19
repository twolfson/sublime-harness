# Load in core dependencies
import code
import os
import sublime
import sublime_plugin

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

urlopen('http://localhost:7070', data=b'init is running')


# Set up constants
__dir__ = os.path.dirname(os.path.abspath(__file__))
run_placeholder_path = os.path.join(__dir__, '.init_launcher_can_run')


# Set up hook for set timeout loop
plugin_host_loaded = False


class SublimeHarnessInitLauncherNamespaceCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        # Mark the plugin host as loaded to stop future timeouts
        global plugin_host_loaded
        plugin_host_loaded = True

        urlopen('http://localhost:7070', data=b'executing code')
        urlopen('http://localhost:7070', data=b'file exists ' + str(os.path.exists(run_placeholder_path)).encode('utf8'))

        # If the harness has not been run yet, remove the lock so no others can run
        if os.path.exists(run_placeholder_path):
            os.unlink(run_placeholder_path)
        # Otherwise, don't run
        else:
            return

        # On every run, re-import the test class
        # DEV: Sublime Text does not recognize changes to command.py.
        # DEV: Once it is loaded and run once via CLI, it is locked in memory until Sublime Text is restarted
        filepath = __dir__ + '/plugin.py'
        namespace = 'sublime-harness-tmp'
        is_sublime_2k = sublime.version() < '3000'
        plugin_dict = {
            '__dir__': __dir__,
            '__file__': filepath,
            '__name__': 'plugin' if is_sublime_2k else '%s.plugin' % namespace,
            '__package__': None if is_sublime_2k else namespace,
            '__builtins__': __builtins__,
        }

        # DEV: In Python 2.x, use execfile. In 3.x, use compile + exec.
        # if getattr(__builtins__, 'execfile', None):
        if is_sublime_2k:
            execfile(filepath, plugin_dict, plugin_dict)
        else:
            f = open(filepath)
            script = f.read()
            interpretter = code.InteractiveInterpreter(plugin_dict)
            interpretter.runcode(compile(script, filepath, 'exec'))
        urlopen('http://localhost:7070', data=b'running plugin')
        # TODO: There is a definitely pickup lag when iterating on launchers
        import json
        urlopen('http://localhost:7070', data=json.dumps(
             dict((key, os.environ.get(key)) for (key, value) in  ['TRAVIS', 'VAGRANT', 'SUBLIME_AUTO_KILL']), indent=4).encode('utf8'))
        plugin_dict['run']()


def run():
    # Attempt to run our plugin
    # TODO: Use real namespace
    sublime.run_command('sublime_harness_init_launcher_namespace')

    # If it did not run (plugin_host has not loaded), then try again in 100ms
    global plugin_host_loaded
    if not plugin_host_loaded:
        sublime.set_timeout(run, 100)
run()
