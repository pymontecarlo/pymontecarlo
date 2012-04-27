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
from pymontecarlo.testcase import TestCase

from config import ConfigParser

# Globals and constants variables.

class TestConfigParser(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        lines = ['[section1]', 'option1=value1', 'option2=value2',
                 '[section2]', 'option3=value3', 'option4=value4']
        sobj = StringIO('\n'.join(lines))

        self.c = ConfigParser()
        self.c.read(sobj)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('value1', self.c.section1.option1)
        self.assertEqual('value2', self.c.section1.option2)
        self.assertEqual('value3', self.c.section2.option3)
        self.assertEqual('value4', self.c.section2.option4)

        self.assertRaises(AttributeError, getattr, self.c, 'section3')
        self.assertRaises(AttributeError, getattr, self.c.section1, 'option3')

    def testread(self):
        # Section with digit
        lines = ['[1section1]', 'option=value1', 'option2=value2',
                 '[section2]', 'option3=value3', 'option4=value4']
        sobj = StringIO('\n'.join(lines))
        c = ConfigParser()
        self.assertRaises(IOError, c.read, sobj, False)

        # Option with digit
        lines = ['[section1]', '1option=value1', 'option2=value2',
                 '[section2]', 'option3=value3', 'option4=value4']
        sobj = StringIO('\n'.join(lines))
        c = ConfigParser()
        self.assertRaises(IOError, c.read, sobj, False)

        # Skip
        lines = ['[1section1]', 'option=value1', 'option2=value2',
                 '[section2]', '1option3=value3', 'option4=value4']
        sobj = StringIO('\n'.join(lines))
        c = ConfigParser()
        c.read(sobj, ignore_errors=True)

        self.assertEqual(1, len(list(c)))
        self.assertTrue('section2' in c)
        self.assertTrue('option4' in c.section2)

    def test__contains__(self):
        self.assertTrue('section1' in self.c)
        self.assertTrue('section2' in self.c)
        self.assertFalse('section3' in self.c)

        self.assertTrue('option1' in self.c.section1)
        self.assertTrue('option2' in self.c.section1)
        self.assertFalse('option3' in self.c.section1)

    def testwrite(self):
        # Add non-string value
        self.c.section1.option3 = 1

        # Write
        output = StringIO()
        self.c.write(output)

        # Read and test
        input = StringIO(output.getvalue())
        parser = SafeConfigParser()
        parser.readfp(input)

        self.assertTrue(parser.has_section('section1'))
        self.assertTrue(parser.has_option('section1', 'option1'))
        self.assertTrue(parser.has_option('section1', 'option2'))
        self.assertTrue(parser.has_option('section1', 'option3'))
        self.assertEqual('value1', parser.get('section1', 'option1'))
        self.assertEqual('value2', parser.get('section1', 'option2'))
        self.assertEqual('1', parser.get('section1', 'option3'))

        self.assertTrue(parser.has_section('section2'))
        self.assertTrue(parser.has_option('section2', 'option3'))
        self.assertTrue(parser.has_option('section2', 'option4'))
        self.assertEqual('value3', parser.get('section2', 'option3'))
        self.assertEqual('value4', parser.get('section2', 'option4'))

    def test__setattr__(self):
        self.assertEqual('value1', self.c.section1.option1)
        self.c.section1.option1 = 'value99'
        self.assertEqual('value99', self.c.section1.option1)

    def testadd_section(self):
        self.c.add_section('section3')
        self.assertTrue('section3' in self.c)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
