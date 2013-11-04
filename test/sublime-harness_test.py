import os
import tempfile
import time
import unittest

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
    runs in the `directory`  # write files to `directory`, assert they can be loaded from
"""

# Decision: Code up v1 as plugin-level only
# and a property that lists out directory
# Namespaced directory will be created on init
# DEV: If someone wants low-level access, they have the directory to write to ;)


class TestSublimeHarness(unittest.TestCase):
    def test_running_arbitrary_python(self):
        # Generate and run our temporary task
        output_file = tempfile.mkstemp()[1]
        harness = sublime_harness.Harness()
        plugin_str = """
with open('%s', 'w') as f:
    f.write('hello world')""" % output_file
        harness.run(plugin_str)

        # Wait for the output file to exist
        while (not os.path.exists(output_file) or os.stat(output_file).st_size == 0):
            time.sleep(0.1)

        # Grab the file output
        with open(output_file) as f:
            self.assertEqual('hello world', f.read())

        # Remove the plugin
        # TODO: plugin_runner isn't making much sense right now...
        harness.close()

    @unittest.skip('hai')
    def test_running_st_python(self):
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

