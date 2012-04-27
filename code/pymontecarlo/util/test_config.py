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
from ConfigParser import SafeConfigParser

# Third party modules.

# Local modules.
from config import ConfigParser

# Globals and constants variables.

class TestConfigParser(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        lines = ['[section1]', 'option1=value1', 'option2=value2',
                 '[section2]', 'option3=value3', 'option4=value4']
        sobj = StringIO('\n'.join(lines))

        self.c = ConfigParser()
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

    def test__contains__(self):
        self.assertTrue('section1' in self.c)
        self.assertTrue('section2' in self.c)
        self.assertFalse('section3' in self.c)

        self.assertTrue('option1' in self.c.section1)
        self.assertTrue('option2' in self.c.section1)
        self.assertFalse('option3' in self.c.section1)

    def testwrite(self):
        output = StringIO()
        self.c.write(output)

        input = StringIO(output.getvalue())
        parser = SafeConfigParser()
        parser.readfp(input)

        self.assertTrue(parser.has_section('section1'))
        self.assertTrue(parser.has_option('section1', 'option1'))
        self.assertTrue(parser.has_option('section1', 'option2'))
        self.assertEqual('value1', parser.get('section1', 'option1'))
        self.assertEqual('value2', parser.get('section1', 'option2'))

        self.assertTrue(parser.has_section('section2'))
        self.assertTrue(parser.has_option('section2', 'option3'))
        self.assertTrue(parser.has_option('section2', 'option4'))
        self.assertEqual('value3', parser.get('section2', 'option3'))
        self.assertEqual('value4', parser.get('section2', 'option4'))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
