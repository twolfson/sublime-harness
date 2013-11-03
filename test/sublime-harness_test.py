from unittest import TestCase
from sublime_harness import sublime_harness

# Outline tests
"""
sublime-harness
    can run arbitrary Python (write to disk)
    can manipulate Sublime Text (open a view, write content, get content, write fetched content to disk)
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
