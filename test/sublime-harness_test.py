from unittest import TestCase
from sublime_harness import sublime_harness

# Outline tests
"""
sublime-harness
    running arbitrary Python (write to disk)
        executes the code
    running Sublime Text specific code (open a view, write content, get content, write fetched content to disk)
        executes within Sublime Text
        when Sublime Text is launched again
            does not execute the code twice
"""


class TestSublimeHarness(TestCase):
    def test_run_python(self):
        """sublime-harness can run arbitrary Python"""
        write_to_disk = """
        with open('/tmp/harness') as f:
            f.write('hello world')
        """
        with sublime_harness.Harness(write_to_disk):
            pass
