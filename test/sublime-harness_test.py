from unittest import TestCase
from sublime_harness import sublime_harness

# Outline tests
"""
sublime-harness
    can run arbitrary Python (write to disk)
    can manipulate Sublime Text (open a view, write content, get content, write fetched content to disk)
"""


class TestRunFunction(TestCase):
    def test_run_exists(self):
        self.assertTrue(bool(sublime_harness))
