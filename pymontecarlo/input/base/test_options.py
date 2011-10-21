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

# Third party modules.

# Local modules.
from pymontecarlo.input.base.options import Options
from pymontecarlo.input.base.detector import BackscatteredElectronEnergyDetector
from pymontecarlo.input.base.limit import ShowersLimit

# Globals and constants variables.

class TestOptions(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.ops = Options(name="Test")
        self.ops.beam.energy = 1234

        self.ops.detectors['bse'] = BackscatteredElectronEnergyDetector((0, 1234), 1000)
        self.ops.limits.add(ShowersLimit(5678))

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(1234, self.ops.beam.energy, 4)

        self.assertEqual(1, len(self.ops.detectors))
        det = self.ops.detectors['bse']
        self.assertAlmostEqual(0, det.limits[0], 4)
        self.assertAlmostEqual(1234, det.limits[1], 4)
        self.assertEqual(1000, det.channels)

        self.assertEqual(1, len(self.ops.limits))
        limit = self.ops.limits.match(ShowersLimit)
        self.assertEqual(5678, limit.showers)

    def testfrom_xml(self):
        element = self.ops.to_xml()
        ops = Options.from_xml(element)

        self.assertAlmostEqual(1234, ops.beam.energy, 4)

        self.assertEqual(1, len(ops.detectors))
        det = ops.detectors['bse']
        self.assertAlmostEqual(0, det.limits[0], 4)
        self.assertAlmostEqual(1234, det.limits[1], 4)
        self.assertEqual(1000, det.channels)

        self.assertEqual(1, len(ops.limits))
        limit = ops.limits.match(ShowersLimit)
        self.assertEqual(5678, limit.showers)

    def testdetectors(self):
        self.assertRaises(ValueError, self.ops.detectors.__setitem__, 'te', None)
        self.assertRaises(ValueError, self.ops.detectors.update, {'te': None})

        dets = self.ops.detectors.matches(BackscatteredElectronEnergyDetector)
        self.assertEqual(1, len(dets))

        dets = self.ops.detectors.matches(ShowersLimit)
        self.assertEqual(0, len(dets))

    def testlimits(self):
        self.assertRaises(ValueError, self.ops.limits.add, None)

        self.ops.limits.add(ShowersLimit(1234))
        self.assertEqual(1, len(self.ops.limits))
        limit = self.ops.limits.match(ShowersLimit)
        self.assertEqual(1234, limit.showers)

    def testto_xml(self):
        element = self.ops.to_xml()

        self.assertEqual('Options', element.tag)

        self.assertEqual('Test', element.get('name'))

        children = list(element.find('beam'))
        self.assertEqual(1, len(children))

        children = list(element.find('geometry'))
        self.assertEqual(1, len(children))

        children = list(element.find('detectors'))
        self.assertEqual(1, len(children))
        self.assertEqual('bse', children[0].get('_key'))

        children = list(element.find('limits'))
        self.assertEqual(1, len(children))


if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
