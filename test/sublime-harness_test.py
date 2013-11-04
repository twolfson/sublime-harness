import os
import tempfile
import time
import unittest

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
    will throw if code does not contain a `run` method
Sublime Text
    running after running a sublime-harness
        does not re-execute harness code
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
