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
from pymontecarlo.input.base.model import ELASTIC_CROSS_SECTION, ELASTIC_CROSS_SECTION_TYPE

# Globals and constants variables.

class TestOptions(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.ops = Options(name="Test")
        self.ops.beam.energy_eV = 1234

        self.ops.detectors['bse'] = BackscatteredElectronEnergyDetector((0, 1234), 1000)
        self.ops.limits.add(ShowersLimit(5678))
        self.ops.models.add(ELASTIC_CROSS_SECTION.rutherford)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(1234, self.ops.beam.energy_eV, 4)

        self.assertEqual(1, len(self.ops.detectors))
        det = self.ops.detectors['bse']
        self.assertAlmostEqual(0, det.limits_eV[0], 4)
        self.assertAlmostEqual(1234, det.limits_eV[1], 4)
        self.assertEqual(1000, det.channels)

        self.assertEqual(1, len(self.ops.limits))
        limit = self.ops.limits.find(ShowersLimit)
        self.assertEqual(5678, limit.showers)

        self.assertEqual(1, len(self.ops.models))
        model = self.ops.models.find(ELASTIC_CROSS_SECTION_TYPE)
        self.assertEqual(ELASTIC_CROSS_SECTION.rutherford, model)

    def testfrom_xml(self):
        element = self.ops.to_xml()
        ops = Options.from_xml(element)

        self.assertAlmostEqual(1234, ops.beam.energy_eV, 4)

        self.assertEqual(1, len(ops.detectors))
        det = ops.detectors['bse']
        self.assertAlmostEqual(0, det.limits_eV[0], 4)
        self.assertAlmostEqual(1234, det.limits_eV[1], 4)
        self.assertEqual(1000, det.channels)

        self.assertEqual(1, len(ops.limits))
        limit = ops.limits.find(ShowersLimit)
        self.assertEqual(5678, limit.showers)

        self.assertEqual(1, len(ops.models))
        model = ops.models.find(ELASTIC_CROSS_SECTION_TYPE)
        self.assertEqual(ELASTIC_CROSS_SECTION.rutherford, model)

    def testdetectors(self):
        dets = self.ops.detectors.findall(BackscatteredElectronEnergyDetector)
        self.assertEqual(1, len(dets))

        dets = self.ops.detectors.findall(ShowersLimit)
        self.assertEqual(0, len(dets))

    def testlimits(self):
        self.ops.limits.add(ShowersLimit(1234))
        self.assertEqual(1, len(self.ops.limits))
        limit = self.ops.limits.find(ShowersLimit)
        self.assertEqual(1234, limit.showers)

    def testmodels(self):
        self.ops.models.add(ELASTIC_CROSS_SECTION.mott_drouin1993)
        self.assertEqual(1, len(self.ops.models))
        model = self.ops.models.find(ELASTIC_CROSS_SECTION_TYPE)
        self.assertEqual(ELASTIC_CROSS_SECTION.mott_drouin1993, model)

    def testto_xml(self):
        element = self.ops.to_xml()

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

        children = list(element.find('models'))
        self.assertEqual(1, len(children))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
