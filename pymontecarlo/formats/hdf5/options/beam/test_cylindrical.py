#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.hdf5.options.beam.cylindrical import \
    CylindricalBeamHDF5Handler
from pymontecarlo.options.beam.cylindrical import CylindricalBeam
from pymontecarlo.options.particle import Particle

# Globals and constants variables.

class TestCylindricalBeamDF5Handler(TestCase):

    def testconvert_parse(self):
        handler = CylindricalBeamHDF5Handler()
        beam = CylindricalBeam(15e3, 123.456, Particle.POSITRON, 1.0, 2.0)
        beam2 = self.convert_parse_hdf5handler(handler, beam)
        self.assertEqual(beam2, beam)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
