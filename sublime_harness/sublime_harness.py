# Load in core dependencies
import ast
import os
import shutil
import subprocess

# Load in 3rd party dependencies
import sublime_info

# Load local dependencies
from .logger import logger

# Set up constants
__dir__ = os.path.dirname(os.path.abspath(__file__))

# TODO: init launcher needs that file safeguard to deal with people who don't clean up
# When init plugin is loading, check for `.abc`.
# If it exists, continue executing. Once launched, remove it.
# During the timeout check, keep on verifying it exists (we don't want double load race conditions)
# Otherwise, do nothing.



class Harness(object):
    sublime_path = sublime_info.get_sublime_path()
    sublime_command = os.path.basename(sublime_path)

    def ensure_directory(self):
        # If the harness directory does not exist, create it
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def install_command_launcher(self):
        # If command launcher doesn't exist, copy it
        # TODO: Verify this works in Windows
        orig_command_path = os.path.join(__dir__, 'launchers/command.py')
        dest_command_path = os.path.join(self.directory, 'command_launcher.py')
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


    def install_init_launcher(self):
        # Clean up any past instances of init launcher
        self.remove_init_launcher()

        # Install a new one
        # TODO: Verify this doesn't have any double invocation consequences
        orig_command_path = os.path.join(__dir__, 'launchers/init.py')
        shutil.copyfile(orig_command_path, self.init_launcher_path)

    def remove_init_launcher(self):
        # If the init launcher exists, delete it
        if os.path.exists(self.init_launcher_path):
            os.unlink(self.init_launcher_path)

    def __init__(self):
        # TODO: Require namespace for harness directory
        # Guarantee the harness directory exists
        self.directory = os.path.join(sublime_info.get_package_directory(), 'sublime-harness-tmp')
        self.ensure_directory()

        self.init_launcher_path = os.path.join(self.directory, 'init_launcher.py')

        # Save defaults
        self.close_called = True

    def run(self, script):
        # TODO: Add safeguard for only running once at a time

        # Assert we are provided a run function
        has_run_fn = False
        for node in ast.iter_child_nodes(ast.parse(script)):
            try:
                if (node.__class__.__name__ == 'FunctionDef' and node.name == 'run'):
                    has_run_fn = True
                    break
            except:
                pass

        # If there was no run function, complain and leave
        if not has_run_fn:
            raise Exception('"run" function was not found in "script": %s' % script)

        # Output test to directory
        f = open(os.path.join(self.directory, 'plugin.py'), 'w')
        f.write(script)
        f.close()

        # TODO: These commands should go in a launching harness
        # If we are running Sublime Text 3 and it has not yet started, use `init`
        running_via_init = False
        if sublime_info.get_sublime_version() >= 3000:
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
                if self.sublime_command in process:
                    sublime_is_running = True
                    break

            # If sublime isn't running, use our init trigger
            logger.debug('Current process list: %s' % ps_list)
            if not sublime_is_running:
                # Install the init trigger
                self.install_init_launcher()

                # and launch sublime_text
                logger.info('Launching %s via init' % self.sublime_path)
                subprocess.call([self.sublime_path])

                # Mark the init to prevent double launch
                running_via_init = True

        # Save running_via_init info
        self.running_via_init = running_via_init

        # If we are not running via init
        if not running_via_init:
            # Guarantee the command launcher exists
            self.install_command_launcher()

            # Invoke the launcher command
            # TODO: Use real namespace
            logger.info('Launching %s via --command' % self.sublime_path)
            subprocess.call([self.sublime_path, '--command', 'sublime_harness_command_launcher_namespace'])

        # Mark close as not called
        self.close_called = False

    def close(self):
        # TODO: When we get to generic directories, clean them up
        # If we were running via init, clean it up
        if self.running_via_init:
            self.remove_init_launcher()
