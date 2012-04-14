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
import tempfile
import os
import shutil

# Third party modules.

# Local modules.
from pymontecarlo.input.material import pure
import pymontecarlo.program.penelope.lib.material as material

# Globals and constants variables.

class TestMaterial(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

        shutil.rmtree(self.tempdir, ignore_errors=True)

    def testskeleton(self):
        self.assertTrue(True)

    def testcreate(self):
        filepath = os.path.join(self.tempdir, 'cu.mat')
        material.create(pure(29), filepath)

        with open(filepath, 'r') as fp:
            lines = fp.readlines()
            self.assertTrue(lines[0].startswith(' PENELOPE'))
            self.assertTrue(lines[-1].startswith(' PENELOPE'))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
