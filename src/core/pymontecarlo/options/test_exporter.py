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
import tempfile
import shutil
import os

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.options.exporter import XMLExporter
from pymontecarlo.options.options import Options

# Globals and constants variables.

class TestXMLExporter(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.tmpdir = tempfile.mkdtemp()

        self.ops = Options("test1")

        self.e = XMLExporter()

    def tearDown(self):
        TestCase.tearDown(self)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testexport(self):
        filepath = self.e.export(self.ops, self.tmpdir)

        self.assertTrue(os.path.exists(filepath))
        self.assertIn(os.path.basename(filepath), os.listdir(self.tmpdir))

    def testexport_multivalue_options(self):
        self.ops.beam.energy_eV = [1e3, 2e3]
        self.assertRaises(ValueError, self.e.export, self.ops, self.tmpdir)

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
