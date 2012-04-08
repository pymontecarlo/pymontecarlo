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

# Third party modules.
from lxml.etree import tostring

# Local modules.
from pymontecarlo.util.xmlutil import create_global_schema, resolve_schema_location

import DrixUtilities.Files as Files

# Globals and constants variables.

class TestModule(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        relativePath = os.path.join('..', 'testdata', 'util', 'xmlutil')
        testdata = Files.getCurrentModulePath(__file__, relativePath)

        self.infos = [('bar1', 'http://foo.org/bar1', os.path.join(testdata, 'bar1.xsd')),
                      ('bar2', 'http://foo.org/bar2', os.path.join(testdata, 'bar2.xsd'))]

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testcreate_global_schema(self):
        root = create_global_schema(self.infos)

    def testresolve_schema_location(self):
        root = create_global_schema(self.infos)

        resolve_schema_location(root)

        print tostring(root, pretty_print=True)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
