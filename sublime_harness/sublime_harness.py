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


class Harness(object):
    sublime_path = sublime_info.get_sublime_path()
    sublime_command = os.path.basename(sublime_path)

    def ensure_directory(self):
        # If the harness directory does not exist, create it
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def install_init_launcher(self):
        # Clean up any past instances of init launcher
        self.remove_init_launcher()

        # Install a new one
        orig_command_path = os.path.join(__dir__, 'launchers/init.py')
        shutil.copyfile(orig_command_path, self.init_launcher_path)

    def remove_init_launcher(self):
        # If the init launcher exists, delete it
        if os.path.exists(self.init_launcher_path):
            os.unlink(self.init_launcher_path)

        # Disarm the init launcher
        self.disarm_init_launcher()

    def arm_init_launcher(self):
        # Touch the run placeholder
        os.utime(self.run_placeholder_path)

    def disarm_init_launcher(self):
        # Remove the run placeholder
        if os.path.exists(self.run_placeholder_path):
            os.unlink(self.run_placeholder_path)

    def __init__(self):
        # TODO: Require namespace for harness directory
        # Guarantee the harness directory exists
        self.directory = os.path.join(sublime_info.get_package_directory(), 'sublime-harness-tmp')
        self.ensure_directory()

        self.init_launcher_path = os.path.join(self.directory, 'init_launcher.py')
        self.run_placeholder_path = os.path.join(self.directory, '.init_launcher_can_run')

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

        # TODO: These commands should go in a launching command
        # TODO: Use tasklist for Windows
        # Get process list
        child = subprocess.Popen(['ps', 'ax'], stdout=subprocess.PIPE)
        ps_list = str(child.stdout.read())

        # Kill the child
        child.kill()

        # Determine if Sublime Text is running
        sublime_is_running = False
        for process in ps_list.split('\n'):
            if self.sublime_command in process:
                sublime_is_running = True
                break
        logger.debug('Current process list: %s' % ps_list)

        # Mark close as not called
        self.close_called = False

        # Disarm the init launcher before installing a new launcher
        self.disarm_init_launcher()

        # Install the init trigger and make it ready to run
        self.install_init_launcher()
        self.arm_init_launcher()

        # If Sublime wasn't running, start it
        if not sublime_is_running:
            logger.info('Launching %s' % self.sublime_path)
            subprocess.call([self.sublime_path])

    def close(self):
        # TODO: When we get to generic directories, clean them up
        # Clean up our launcher
        self.remove_init_launcher()

        # Mark close as called
        self.close_called = True
