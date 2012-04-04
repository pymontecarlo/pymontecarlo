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

# Third party modules.

# Local modules.
import pymontecarlo.util.imp as imp

# Globals and constants variables.

class TestImp(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def test_match(self):
        includes = ['abc*', 'def*']
        excludes = ['abcdef']

        self.assertTrue(imp._match('abc', includes, excludes))
        self.assertFalse(imp._match('abcdef', includes, excludes))
        self.assertFalse(imp._match('ghi', includes, excludes))
        self.assertTrue(imp._match('abcdefghi', includes, excludes))

        includes = ['*']
        excludes = ['abc*', 'def*']

        self.assertFalse(imp._match('abc', includes, excludes))
        self.assertFalse(imp._match('abcdef', includes, excludes))
        self.assertTrue(imp._match('ghi', includes, excludes))
        self.assertFalse(imp._match('abcdefghi', includes, excludes))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
