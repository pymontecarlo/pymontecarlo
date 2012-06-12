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
from math import radians

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.analysis.measurement import Measurement

from pymontecarlo.input.options import Options
from pymontecarlo.input.detector import PhotonIntensityDetector
from pymontecarlo.input.material import Material
from pymontecarlo.util.transition import Ka, La
from pymontecarlo.analysis.rule import ElementByDifference, FixedElement

# Globals and constants variables.

class TestMeasurement(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        options = Options('PAP')
        options.beam.energy_eV = 20000
        options.detectors['xray'] = \
            PhotonIntensityDetector((radians(52.5), radians(52.5)),
                                    (0.0, radians(360.0)))

        self.m = Measurement(options, options.geometry.body, 'xray')

        self.m.add_kratio(Ka(29), 0.2470)
        self.m.add_rule(ElementByDifference(79))

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testoptions(self):
        self.assertAlmostEqual(20000, self.m.options.beam.energy_eV, 4)

    def testunknown_body(self):
        self.assertEqual(self.m.unknown_body, self.m.options.geometry.body)

    def testdetector_key(self):
        self.assertEqual('xray', self.m.detector_key)

    def testadd_kratio(self):
        standard = Material('U90', {92: 0.9, 49: 0.1})
        self.m.add_kratio(La(92), 0.5, standard)

        self.assertTrue(self.m.has_kratio(92))
        self.assertEqual('U90', self.m.get_standards()[92].name)
        self.assertAlmostEqual(0.5, self.m.get_kratios()[92], 4)
        self.assertIn(La(92), self.m.get_transitions())

        self.assertRaises(ValueError, self.m.add_kratio, Ka(92), 0.1)
        self.assertRaises(ValueError, self.m.add_kratio, Ka(79), 0.1)
        self.assertRaises(ValueError, self.m.add_kratio, Ka(14), -0.1)

    def testremove_kratio(self):
        self.m.remove_kratio(29)
        self.assertFalse(self.m.has_kratio(29))
        self.assertEqual(0, len(self.m.get_standards()))
        self.assertEqual(0, len(self.m.get_kratios()))
        self.assertEqual(0, len(self.m.get_transitions()))

    def testhas_kratio(self):
        self.assertTrue(self.m.has_kratio(29))
        self.assertFalse(self.m.has_kratio(79))

    def testadd_rule(self):
        self.m.add_rule(FixedElement(14, 0.5))

        self.assertTrue(self.m.has_rule(14))
        self.assertEqual(2, len(self.m.get_rules()))

        self.assertRaises(ValueError, self.m.add_rule, ElementByDifference(92))
        self.assertRaises(ValueError, self.m.add_rule, FixedElement(14, 0.1))
        self.assertRaises(ValueError, self.m.add_rule, FixedElement(29, 0.1))

    def testremove_rule(self):
        self.m.remove_rule(79)
        self.assertFalse(self.m.has_rule(79))
        self.assertEqual(0, len(self.m.get_rules()))

    def testhas_rule(self):
        self.assertTrue(self.m.has_rule(79))
        self.assertFalse(self.m.has_rule(29))

    def testget_transitions(self):
        transitions = self.m.get_transitions()

        self.assertEqual(1, len(transitions))
        self.assertIn(Ka(29), transitions)

    def testget_kratios(self):
        kratios = self.m.get_kratios()

        self.assertEqual(1, len(kratios))
        self.assertAlmostEqual(0.247, kratios[29], 4)

    def testget_standards(self):
        standards = self.m.get_standards()

        self.assertEqual(1, len(standards))
        self.assertEqual('Copper', standards[29].name)

    def testget_rules(self):
        rules = self.m.get_rules()

        self.assertEqual(1, len(rules))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
