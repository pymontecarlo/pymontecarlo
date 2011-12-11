#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
from StringIO import StringIO

# Third party modules.

# Local modules.
from config import ConfigReader

# Globals and constants variables.

class TestConfigReader(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        lines = ['[section1]', 'option1=value1', 'option2=value2',
                 '[section2]', 'option3=value3', 'option4=value4']
        sobj = StringIO('\n'.join(lines))

        self.c = ConfigReader()
        self.c.read(sobj)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('value1', self.c.section1.option1)
        self.assertEqual('value2', self.c.section1.option2)
        self.assertEqual('value3', self.c.section2.option3)
        self.assertEqual('value4', self.c.section2.option4)

        self.assertRaises(AttributeError, self.c.__getattr__, 'section3')
        self.assertRaises(AttributeError, self.c.section1.__getattr__, 'option3')

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
