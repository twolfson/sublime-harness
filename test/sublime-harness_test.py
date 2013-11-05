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
"""


class TestSublimeHarness(unittest.TestCase):
    def setUp(self):
        self.output_file = tempfile.mkstemp()[1]
        self.harness = sublime_harness.Harness()

    def tearDown(self):
        os.unlink(self.output_file)

    def _wait_for_output_file(self):
        output_file = self.output_file
        while (not os.path.exists(output_file) or os.stat(output_file).st_size == 0):
            time.sleep(0.1)

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
        print 'output'
        plugin_str = open(__dir__ + '/test_files/directory.py').read() % self.output_file
        self.harness.run(plugin_str)
        print 'waiting'
        self._wait_for_output_file()

        # Grab the file output
        print 'assertion'
        with open(self.output_file) as f:
            self.assertEqual('world', f.read())

        # Remove the plugin and our file
        print 'cleanup'
        self.harness.close()
        os.unlink(dest_hello_path)

    def test_assert_run(self):
        assert_run_plugin = open(__dir__ + '/test_files/missing_run.py').read()
        self.assertRaises(Exception, self.harness.run, assert_run_plugin)

    def test_prevent_multiple_runs(self):
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
        # TODO: This won't run with Travis since it is launching synchronously =/
        # TODO: We should be able to reproduce this one within Vagrant
        print 'launching subl'
        child = subprocess.Popen([sublime_info.get_sublime_path()])
        print 'after launch'

        # Wait for a bit
        print 'sleeping'
        time.sleep(1)

        # Kill Sublime
        print 'killing'
        child.kill()
        time.sleep(0.2)

        # Assert file has not changed
        print 'asserting'
        f = open(self.output_file)
        new_timestamp = f.read()
        f.close()
        self.assertEqual(orignal_timestamp, new_timestamp)
