# Load in core dependencies
import code
import os
import sublime
import sublime_plugin

# Set up constants
__dir__ = os.path.dirname(os.path.abspath(__file__))


class SublimeHarnessCommandLauncherNamespaceCommand(sublime_plugin.ApplicationCommand):
    def run(self):
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
        plugin_dict['run']()
