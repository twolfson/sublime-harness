from unittest import TestCase
from sublime_harness import sublime_harness


class TestRunFunction(TestCase):
    def test_run_exists(self):
        self.assertTrue(bool(sublime_harness))
