import os
import shutil
import tempfile
import time
import unittest
import subprocess

import sublime_info

from sublime_harness import sublime_harness

# Set up constants
__dir__ = os.path.dirname(os.path.abspath(__file__))

# Outline tests
"""
sublime-harness
    running arbitrary Python  # write to disk
        executes the code
    running Sublime Text specific code  # open a view, write content, get content, write fetched content to disk
        executes within Sublime Text

# Intermediate test
sublime-harness
    runs in the `directory`  # write files to `directory`, assert they can be loaded from

# Edge case
sublime-harness
    will raise if code does not contain a `run` method
Sublime Text
    running after running a sublime-harness
        does not re-execute harness code

# TODO: If there is an error launching Sublime Text, proliferate it
# Just not stderr (fucking headless + xvfb)
# which means status code
"""


class TestSublimeHarness(unittest.TestCase):
    def setUp(self):
        self.output_file = tempfile.mkstemp()[1]
        self.harness = sublime_harness.Harness()

    def tearDown(self):
        os.unlink(self.output_file)

        # If we are autokilling, wait for all Sublime's to close
        if os.environ.get('SUBLIME_AUTO_KILL'):
            while self._sublime_is_running():
                time.sleep(0.1)

    def _wait_for_output_file(self):
        output_file = self.output_file
        while (not os.path.exists(output_file) or
               os.stat(output_file).st_size == 0):
            time.sleep(0.1)

    def _sublime_is_running(self):
        child = subprocess.Popen(['ps', 'ax'], stdout=subprocess.PIPE)
        ps_list = str(child.stdout.read())
        child.kill()
        sublime_is_running = False
        sublime_path = sublime_info.get_sublime_path()
        sublime_command = os.path.basename(sublime_path)
        for process in ps_list.split('\n'):
            if sublime_command in process:
                sublime_is_running = True
                break
        return sublime_is_running

    def test_running_arbitrary_python(self):
        # TODO: This test is useless due to sublime self-kill
        # Generate and run our temporary task
        plugin_str = open(__dir__ + '/test_files/arbitrary.py').read() % self.output_file
        self.harness.run(plugin_str)
        self._wait_for_output_file()

        # Grab the file output
        with open(self.output_file) as f:
            self.assertIn('hello world', f.read())

        # Remove the plugin
        self.harness.close()

    def test_running_st_python(self):
        # Generate and run our temporary task
        plugin_str = open(__dir__ + '/test_files/st_python.py').read() % self.output_file
        self.harness.run(plugin_str)
        self._wait_for_output_file()

        # Grab the file output
        with open(self.output_file) as f:
            self.assertIn('Packages', f.read())

        # Remove the plugin
        self.harness.close()

    def test_run_in_directory(self):
        # Copy over a local file to the directory
        dest_hello_path = self.harness.directory + '/hello.py'
        shutil.copy(__dir__ + '/test_files/hello.py', dest_hello_path)

        # Generate and run our temporary task
        plugin_str = open(__dir__ + '/test_files/directory.py').read() % self.output_file
        self.harness.run(plugin_str)
        self._wait_for_output_file()

        # Grab the file output
        with open(self.output_file) as f:
            self.assertEqual('world', f.read())

        # Remove the plugin and our file
        self.harness.close()
        os.unlink(dest_hello_path)

    def test_assert_run(self):
        assert_run_plugin = open(__dir__ + '/test_files/missing_run.py').read()
        self.assertRaises(Exception, self.harness.run, assert_run_plugin)

    # DEV: Namez with zz to always run last (to see if lower level issues or this test are the problem)
    def test_zz_prevent_multiple_runs(self):
        # DEV: In Vagrant + ST3, this takes 15 seconds to run
        # Generate and run our temporary task
        plugin_str = open(__dir__ + '/test_files/timestamp.py').read() % self.output_file
        self.harness.run(plugin_str)
        self._wait_for_output_file()

        # Grab the file output
        f = open(self.output_file)
        orignal_timestamp = f.read()
        f.close()
        self.assertNotEqual(orignal_timestamp, '')

        # Remove the plugin
        self.harness.close()

        # Launch sublime again
        if os.environ.get('TRAVIS'):
            # DEV: Currently `subl` in Travis launches a fork from a bash shell meaning it uses a different PID which is destroyed.
            # TODO: We should add `/opt/sublime_text_2/sublime_text` as a primary check point for subl
            if sublime_info.get_sublime_version() < 3000:
                child = subprocess.Popen(['/opt/sublime_text_2/sublime_text', '--class=sublime-text-2'], stderr=subprocess.PIPE)
            else:
                child = subprocess.Popen(['/opt/sublime_text/sublime_text', '--wait'])
        else:
            child = subprocess.Popen([sublime_info.get_sublime_path()], stderr=subprocess.PIPE)

        # Wait for a bit
        time.sleep(1)

        # Kill Sublime
        child.kill()

        # Assert file has not changed
        f = open(self.output_file)
        new_timestamp = f.read()
        f.close()
        self.assertEqual(orignal_timestamp, new_timestamp)
