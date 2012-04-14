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
import shutil

# Third party modules.

# Local modules.
from pymontecarlo.input.geometry import Substrate
from pymontecarlo.input.material import pure

import pymontecarlo.program.penelope.lib.geometry as pengeometry
from pymontecarlo.program.penelope.io.exporter import Exporter

# Globals and constants variables.

class TestGeometry(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testskeleton(self):
        self.assertTrue(True)

    def testinit(self):
        geometry = Substrate(pure(29))
        geoinfo, _matinfos = Exporter().export_geometry(geometry, self.tmpdir)

        geofilepath = geoinfo[1]
        nmat, nbody = pengeometry.init(geofilepath)

        self.assertEqual(1, nmat)
        self.assertEqual(2, nbody)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
