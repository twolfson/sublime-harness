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
        # Edge case
        when Sublime Text is launched again
            does not execute the code twice

# Intermediate test
sublime-harness
    runs in the `directory`  # write files to `directory`, assert they can be loaded from

# Edge case
sublime-harness
    will throw if code does not contain a `run` method
"""


class TestSublimeHarness(unittest.TestCase):
    def test_running_arbitrary_python(self):
        # Generate and run our temporary task
        output_file = tempfile.mkstemp()[1]
        harness = sublime_harness.Harness()
        plugin_str = open(__dir__ + '/test_files/arbitrary.py').read() % output_file
        harness.run(plugin_str)

        # Wait for the output file to exist
        while (not os.path.exists(output_file) or os.stat(output_file).st_size == 0):
            time.sleep(0.1)

        # Grab the file output
        with open(output_file) as f:
            self.assertIn('hello world', f.read())

        # Remove the plugin
        harness.close()

    def test_running_st_python(self):
        # Generate and run our temporary task
        output_file = tempfile.mkstemp()[1]
        harness = sublime_harness.Harness()
        plugin_str = open(__dir__ + '/test_files/st_python.py').read() % output_file
        harness.run(plugin_str)

        # Wait for the output file to exist
        while (not os.path.exists(output_file) or os.stat(output_file).st_size == 0):
            time.sleep(0.1)

        # Grab the file output
        with open(output_file) as f:
            self.assertIn('Packages', f.read())

        # Remove the plugin
        harness.close()
