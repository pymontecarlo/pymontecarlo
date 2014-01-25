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
from pymontecarlo.options.options import Options
from pymontecarlo.options.material import Material
from pymontecarlo.options.limit import ShowersLimit

from pymontecarlo.program.monaco.exporter import Exporter

# Globals and constants variables.
from pymontecarlo.options.particle import ELECTRON

class TestExporter(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.tmpdir = tempfile.mkdtemp()

        self.e = Exporter()

        self.ops = Options('aatest')
        self.ops.beam.energy_eV = 4e3
        self.ops.geometry.material = \
            Material({6: 0.4, 13: 0.6}, absorption_energy_eV={ELECTRON: 234.0})
        self.ops.limits.add(ShowersLimit(1234))

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testexport(self):
        self.e.export(self.ops, self.tmpdir)

        filenames = os.listdir(self.tmpdir)
        self.assertEqual(2, len(filenames))
        self.assertIn('aatest.MAT', filenames)
        self.assertIn('aatest.SIM', filenames)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
