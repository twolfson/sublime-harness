# Load in core dependencies
import os
import shutil
import subprocess

# Load in 3rd party dependencies
import sublime_info

# Load local dependencies
from .logger import logger

# Set up constants
__dir__ = os.path.dirname(os.path.abspath(__file__))

# TODO: We are going to need a mechanism for utils
# (e.g. get temporary dir, copy dir, run script in file)

# TODO: We need to decide if callback is the best cleanup mechanism.
# Maybe something more like `open`, `close` is more Pythonic


class Base(object):
    plugin_dir = os.path.join(sublime_info.get_package_directory(), 'sublime-harness-tmp')

    @classmethod
    def ensure_plugin_dir(cls):
        # If the plugin test directory does not exist, create it
        if not os.path.exists(cls.plugin_dir):
            os.makedirs(cls.plugin_dir)

    @classmethod
    def install_command_launcher(cls):
        # Guarantee the plugin test dir exists
        cls.ensure_plugin_dir()

        # If command launcher doesn't exist, copy it
        # TODO: Verify this works in Windows
        orig_command_path = os.path.join(__dir__, '/launchers/command.py')
        dest_command_path = os.path.join(cls.plugin_dir, '/command_launcher.py')
        if not os.path.exists(dest_command_path):
            shutil.copyfile(orig_command_path, dest_command_path)
        else:
        # Otherwise...
            # If there are updates for command launcher
            expected_command = None
            with open(orig_command_path) as f:
                expected_command = f.read()
            actual_command = None
            with open(dest_command_path) as f:
                actual_command = f.read()
            if expected_command != actual_command:
                # Update the file
                shutil.copyfile(orig_command_path, dest_command_path)

                # and notify the user we must restart Sublime
                raise Exception('We had to update the sublime-harness plugin. You must close or restart Sublime to continue testing.')

    init_launcher_path = os.path.join(plugin_dir, 'init_launcher.py')

    @classmethod
    def install_init_launcher(cls):
        # Guarantee the plugin test dir exists
        cls.ensure_plugin_dir()

        # Clean up any past instances of init launcher
        cls.remove_init_launcher()

        # Install a new one
        # TODO: Verify this doesn't have any double invocation consequences
        orig_command_path = os.path.join(__dir__, '/launchers/init.py')
        shutil.copyfile(orig_command_path, cls.init_launcher_path)

    @classmethod
    def remove_init_launcher(cls):
        # If the init launcher exists, delete it
        if os.path.exists(cls.init_launcher_path):
            os.unlink(cls.init_launcher_path)

    @classmethod
    def run_plugin(cls, plugin_str):
        # Guarantee there is an output directory and launcher
        cls.ensure_plugin_dir()

        # Output test to directory
        f = open(os.path.join(cls.plugin_dir, '/plugin.py'), 'w')
        f.write(plugin_str)
        f.close()

        # TODO: These commands should go in a launching harness
        # If we are running Sublime Text 3 and it has not yet started, use `init`
        running_via_init = False
        if sublime_info.get_sublime_version >= 3000:
            # TODO: Use tasklist for Windows
            # Get process list
            child = subprocess.Popen(['ps', 'ax'], stdout=subprocess.PIPE)
            ps_list = str(child.stdout.read())

            # Kill the child
            child.kill()

            # Determine if Sublime Text is running
            # TODO: This could be subl, sublime_text, or other
            sublime_is_running = False
            for process in ps_list.split('\n'):
                if cls._sublime_command in process:
                    sublime_is_running = True
                    break

            # If sublime isn't running, use our init trigger
            logger.debug('Current process list: %s' % ps_list)
            if not sublime_is_running:
                # Install the init trigger
                cls.install_init_launcher()

                # and launch sublime_text
                logger.info('Launching %s via init' % cls._sublime_command)
                subprocess.call([cls._sublime_command])

                # Mark the init to prevent double launch
                running_via_init = True

        # By default, return a callback that does nothing
        callback = lambda: True

        # If we used the init command
        if running_via_init:
            # Return a callback to clean up init launcher
            callback = lambda: cls.remove_init_launcher()

        # Return the callback
        return callback
