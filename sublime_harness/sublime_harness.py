# Load in core dependencies
import os
import shutil
import subprocess
import time
import tempfile

# Load in 3rd party dependencies
import sublime_info
from jinja2 import Template

# Set up constants
__dir__ = os.path.dirname(os.path.abspath(__file__))

# TODO: Consider using a proper logger
class Logger(object):
    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warn(self, msg):
        pass
logger = Logger()


class Base(object):
    plugin_test_dir = os.path.join(sublime_info.get_package_directory(), 'sublime-plugin-tests-tmp')

    @classmethod
    def ensure_plugin_test_dir(cls):
        # If the plugin test directory does not exist, create it
        if not os.path.exists(cls.plugin_test_dir):
            os.makedirs(cls.plugin_test_dir)

    @classmethod
    def _ensure_utils(cls):
        # Ensure the plugin test directory exists
        cls.ensure_plugin_test_dir()

        # TODO: Use similar copy model minus the exception
        # TODO: If we overwrite utils, be sure to wait so that changes for import get picked up
        if not os.path.exists(cls.plugin_test_dir + '/utils'):
            shutil.copytree(__dir__ + '/utils', cls.plugin_test_dir + '/utils')

    @classmethod
    def install_command_launcher(cls):
        # Guarantee the plugin test dir exists
        cls.ensure_plugin_test_dir()

        # If command launcher doesn't exist, copy it
        orig_command_path = __dir__ + '/launchers/command.py'
        dest_command_path = cls.plugin_test_dir + '/command_launcher.py'
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
                raise Exception('We had to update the test launcher plugin. You must close or restart Sublime to continue testing.')

    _init_launcher_path = plugin_test_dir + '/init_launcher.py'

    @classmethod
    def remove_init_launcher(cls):
        # If the init launcher exists, delete it
        if os.path.exists(cls._init_launcher_path):
            os.unlink(cls._init_launcher_path)

    @classmethod
    def install_init_launcher(cls):
        # Guarantee the plugin test dir exists
        cls.ensure_plugin_test_dir()

        # Clean up any past instances of init launcher
        cls.remove_init_launcher()

        # Install a new one
        # TODO: Verify this doesn't have any double invocation consequences
        orig_command_path = __dir__ + '/launchers/init.py'
        shutil.copyfile(orig_command_path, cls._init_launcher_path)

    @classmethod
    def _run_test(cls, test_str, auto_kill_sublime=False):
        # Guarantee there is an output directory and launcher
        cls._ensure_utils()

        # Reserve an output file
        output_file = tempfile.mkstemp()[1]

        # Template plugin
        plugin_runner = None
        f = open(__dir__ + '/templates/plugin_runner.py')
        runner_template = Template(f.read())
        plugin_runner = runner_template.render(output_file=output_file,
                                               auto_kill_sublime=auto_kill_sublime)
        f.close()

        # Output plugin_runner to directory
        f = open(cls.plugin_test_dir + '/plugin_runner.py', 'w')
        f.write(plugin_runner)
        f.close()

        # Output test to directory
        f = open(cls.plugin_test_dir + '/plugin.py', 'w')
        f.write(test_str)
        f.close()

        # TODO: These commands should go in a launching harness
        # If we are running Sublime Text 3 and it has not yet started, use `init`
        running_via_init = False
        if SUBLIME_TEXT_VERSION == '3.0':
            # TODO: Use tasklist for Windows
            # Get process list
            child = subprocess.Popen(["ps", "ax"], stdout=subprocess.PIPE)
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

            # TODO: Use this logic for when another request to run is up
            # # and if Sublime was not running, wait for it to terminate
            # if not sublime_is_running:
            #     while True:
            #         sublime_is_still_running = False
            #         # TODO: Modularize this
            #         child = subprocess.Popen(["ps", "ax"], stdout=subprocess.PIPE)
            #         ps_list = str(child.stdout.read())

            #         # Kill the child
            #         child.kill()

            #         # TODO: Output ps_list to a debug file
            #         logger.debug('Current process list: %s' % ps_list)

            #         for process in ps_list.split('\n'):
            #             if cls._sublime_command in process:
            #                 sublime_is_still_running = True

            #         if not sublime_is_still_running:
            #             break
            #         else:
            #             logger.debug('Waiting for %s to terminate' % cls._sublime_command)
            #             time.sleep(0.1)
