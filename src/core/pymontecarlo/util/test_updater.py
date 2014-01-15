#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
import os
import tempfile
import shutil

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.util.updater import _Updater

# Globals and constants variables.

class MockUpdater(_Updater):
    """
    Mock updater that updates any text file so that the first line is ``Hello``.
    """

    def __init__(self):
        _Updater.__init__(self)

        self._updaters[0] = self._update_noversion
        self._updaters[1] = self._update_version1

    def _get_version(self, filepath):
        with open(filepath, 'r') as fp:
            text = fp.read().strip()
        return 1 if text == 'Hello' else 0

    def _validate(self, filepath):
        with open(filepath, 'r') as fp:
            text = fp.read().strip()
        if text != 'Hello':
            raise AssertionError('Text not "Hello"')

    def _update_noversion(self, filepath):
        with open(filepath, 'w') as fp:
            fp.write('Hello')
        return filepath

    def _update_version1(self, filepath):
        return filepath

class Test_Updater(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        # Create test files
        self.tmpdir = tempfile.mkdtemp()

        self.invalid_filepath = os.path.join(self.tmpdir, 'test1.txt')
        with open(self.invalid_filepath, 'w') as fp:
            fp.write('Version 0 file, invalid')

        self.valid_filepath = os.path.join(self.tmpdir, 'test2.txt')
        with open(self.valid_filepath, 'w') as fp:
            fp.write('Hello')

        # Updater
        self.updater = MockUpdater()

    def tearDown(self):
        TestCase.tearDown(self)

        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testskeleton(self):
        self.assertTrue(True)

    def testupdate_invalid(self):
        self.updater.update(self.invalid_filepath)

        backup_filepath = os.path.join(self.tmpdir, 'test1.txt.bak')
        self.assertTrue(os.path.exists(backup_filepath))

        with open(self.invalid_filepath, 'r') as fp:
            text = fp.read().strip()
        self.assertEqual('Hello', text)

    def testupdate_valid(self):
        self.updater.update(self.valid_filepath)

        backup_filepath = os.path.join(self.tmpdir, 'test2.txt.bak')
        self.assertTrue(os.path.exists(backup_filepath))

        with open(self.valid_filepath, 'r') as fp:
            text = fp.read().strip()
        self.assertEqual('Hello', text)

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
