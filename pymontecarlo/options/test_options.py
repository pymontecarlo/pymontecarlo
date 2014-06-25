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
import copy

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.program.test_config import DummyProgram

from pymontecarlo.options.options import Options
from pymontecarlo.options.detector import BackscatteredElectronEnergyDetector
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.options.model import ELASTIC_CROSS_SECTION

# Globals and constants variables.

class TestOptions(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.ops = Options(name="Test")

        self.ops.programs.add(DummyProgram())

        self.ops.beam.energy_eV = 1234

        self.ops.detectors['bse'] = BackscatteredElectronEnergyDetector(1000, (0, 1234))
        self.ops.limits.add(ShowersLimit(5678))
        self.ops.models.add(ELASTIC_CROSS_SECTION.rutherford)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(1, len(self.ops.programs))

        self.assertAlmostEqual(1234, self.ops.beam.energy_eV, 4)

        self.assertEqual(1, len(self.ops.detectors))
        det = self.ops.detectors['bse']
        self.assertAlmostEqual(0, det.limits_eV[0], 4)
        self.assertAlmostEqual(1234, det.limits_eV[1], 4)
        self.assertEqual(1000, det.channels)

        self.assertEqual(1, len(self.ops.limits))
        limit = list(self.ops.limits.iterclass(ShowersLimit))[0]
        self.assertEqual(5678, limit.showers)

        self.assertEqual(1, len(self.ops.models))
        models = list(self.ops.models.iterclass(ELASTIC_CROSS_SECTION))
        self.assertEqual(1, len(models))
        self.assertEqual(ELASTIC_CROSS_SECTION.rutherford, models[0])

    def testcopy(self):
        uuid = self.ops.uuid
        ops = copy.copy(self.ops)

        self.assertEqual(1, len(ops.programs))

        self.assertAlmostEqual(1234, self.ops.beam.energy_eV, 4)
        self.assertAlmostEqual(1234, ops.beam.energy_eV, 4)
        self.assertEqual(self.ops.beam, ops.beam)

        self.assertNotEqual(uuid, ops.uuid)
        self.assertEqual(uuid, self.ops.uuid)

        ops.beam.energy_eV = 5678
        self.assertAlmostEqual(5678, self.ops.beam.energy_eV, 4)
        self.assertAlmostEqual(5678, ops.beam.energy_eV, 4)

    def testdeepcopy(self):
        uuid = self.ops.uuid
        ops = copy.deepcopy(self.ops)

        self.assertEqual(1, len(ops.programs))

        self.assertAlmostEqual(1234, self.ops.beam.energy_eV, 4)
        self.assertAlmostEqual(1234, ops.beam.energy_eV, 4)
        self.assertNotEqual(self.ops.beam, ops.beam)

        self.assertNotEqual(uuid, ops.uuid)
        self.assertEqual(uuid, self.ops.uuid)

        ops.beam.energy_eV = 5678
        self.assertAlmostEqual(1234, self.ops.beam.energy_eV, 4)
        self.assertAlmostEqual(5678, ops.beam.energy_eV, 4)

        self.assertIsNot(list(self.ops.limits)[0], list(ops.limits)[0])

    def testuuid(self):
        uuid = self.ops.uuid
        self.assertEqual(uuid, self.ops.uuid)

    def testdetectors(self):
        dets = list(self.ops.detectors.iterclass(BackscatteredElectronEnergyDetector))
        self.assertEqual(1, len(dets))
        self.assertEqual('bse', dets[0][0])

        dets = list(self.ops.detectors.iterclass(ShowersLimit))
        self.assertEqual(0, len(dets))

    def testdetectors_multiple(self):
        self.ops.detectors['bse'] = \
            [BackscatteredElectronEnergyDetector(1000, (0, 1234)),
             BackscatteredElectronEnergyDetector(2000, (1234, 5678))]

        dets = list(self.ops.detectors.iterclass(BackscatteredElectronEnergyDetector))
        self.assertEqual(2, len(dets))
        self.assertEqual('bse', dets[0][0])
        self.assertEqual('bse', dets[1][0])

    def testlimits(self):
        self.ops.limits.add(ShowersLimit(1234))
        self.assertEqual(1, len(self.ops.limits))

        limits = list(self.ops.limits.iterclass(ShowersLimit))
        self.assertEqual(1, len(limits))

    def testmodels(self):
        self.ops.models.add(ELASTIC_CROSS_SECTION.mott_drouin1993)
        self.assertEqual(2, len(self.ops.models))
        models = list(self.ops.models.iterclass(ELASTIC_CROSS_SECTION))
        self.assertEqual(2, len(models))
        
        self.ops.models.add(ELASTIC_CROSS_SECTION.mott_drouin1993)
        self.assertEqual(2, len(self.ops.models))

    def testto_from_element(self):
        element = self.ops.toelement()
        obj = Options.fromelement(element)

        self.assertEqual(1, len(obj.programs))

        self.assertAlmostEqual(1234, obj.beam.energy_eV, 4)

        self.assertEqual(1, len(obj.detectors))
        det = obj.detectors['bse']
        self.assertAlmostEqual(0, det.limits_eV[0], 4)
        self.assertAlmostEqual(1234, det.limits_eV[1], 4)
        self.assertEqual(1000, det.channels)

        self.assertEqual(1, len(obj.limits))
        limits = list(obj.limits.iterclass(ShowersLimit))
        self.assertEqual(1, len(limits))
        self.assertEqual(5678, limits[0].showers)

        self.assertEqual(1, len(obj.models))
        models = list(obj.models.iterclass(ELASTIC_CROSS_SECTION))
        self.assertEqual(1, len(models))
        self.assertEqual(ELASTIC_CROSS_SECTION.rutherford, models[0])

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
