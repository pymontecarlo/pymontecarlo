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
from pymontecarlo.testcase import TestCase

from pymontecarlo.util.manager import Manager

# Globals and constants variables.

class Mock1(object):
    pass

class Mock2(object):
    pass

class TestManager(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.manager = Manager()

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testregister_loader(self):
        self.manager.register_loader('tag1', Mock1)
        self.assertEqual(Mock1, self.manager.get_class('tag1'))
        self.assertRaises(ValueError, self.manager.get_class, 'tag2')

        self.assertRaises(ValueError, self.manager.register_loader, 'tag1', Mock2)

    def testregister_saver(self):
        self.manager.register_saver('tag1', Mock1)
        self.assertEqual('tag1', self.manager.get_tag(Mock1))
        self.assertRaises(ValueError, self.manager.get_tag, Mock2)

        self.assertRaises(ValueError, self.manager.register_saver, 'tag2', Mock1)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
