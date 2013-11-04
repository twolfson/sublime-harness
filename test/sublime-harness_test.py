import os
import tempfile
import time
from unittest import TestCase
from sublime_harness import sublime_harness

# Outline tests
"""
sublime-harness
    running arbitrary Python  # write to disk
        executes the code
    running Sublime Text specific code  # open a view, write content, get content, write fetched content to disk
        executes within Sublime Text
        when Sublime Text is launched again
            does not execute the code twice
"""


class TestSublimeHarness(TestCase):
    def test_running_arbitrary_python(self):
        # Generate and run our temporary task
        output_file = tempfile.mkstemp()[1]
        write_to_disk = """
with open(%s, 'w') as f:
    f.write('hello world')""" % output_file
        harness = sublime_harness.Harness(write_to_disk)
        harness.run()

        # Wait for the file to exist
        while True:
            if os.path.exists(output_file):
                break
            time.sleep(0.1)

        # Remove the plugin
        harness.close()
