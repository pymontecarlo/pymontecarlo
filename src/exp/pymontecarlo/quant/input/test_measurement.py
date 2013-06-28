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
from pyxray.transition import Ka, La

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.quant.input.measurement import Measurement

from pymontecarlo.input.options import Options
from pymontecarlo.input.detector import PhotonIntensityDetector
from pymontecarlo.input.material import Material
from pymontecarlo.input.geometry import Sphere
from pymontecarlo.quant.input.rule import ElementByDifferenceRule, FixedElementRule

# Globals and constants variables.

class TestMeasurement(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        options = Options('PAP')
        options.beam.energy_eV = 20000

        detector = PhotonIntensityDetector((radians(50.0), radians(55)),
                                           (0.0, radians(360.0)))

        self.m = Measurement(options, options.geometry.body, detector)

        self.m.add_kratio(Ka(29), 0.2470, 0.004)
        self.m.add_rule(ElementByDifferenceRule(79))

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testoptions(self):
        self.assertAlmostEqual(20000, self.m.options.beam.energy_eV, 4)

    def testunknown_body(self):
        self.assertEqual(self.m.unknown_body, self.m.options.geometry.body)

    def testdetector(self):
        self.assertAlmostEqual(0.434867, self.m.detector.solidangle_sr, 4)

    def testadd_kratio(self):
        standard = Sphere(Material('U90', {92: 0.9, 49: 0.1}), 1e-6)
        self.m.add_kratio(La(92), 0.5, standard=standard)

        self.assertTrue(self.m.has_kratio(92))
        self.assertEqual('U90', self.m.get_standards()[92].material.name)
        self.assertAlmostEqual(0.5, self.m.get_kratios()[92][0], 4)
        self.assertAlmostEqual(0.0, self.m.get_kratios()[92][1], 4)
        self.assertIn(La(92), self.m.get_transitions())

        self.m.add_kratio(Ka(13), 0.2, unc=0.125)

        self.assertTrue(self.m.has_kratio(13))
        self.assertEqual('Aluminium', self.m.get_standards()[13].material.name)
        self.assertAlmostEqual(0.2, self.m.get_kratios()[13][0], 4)
        self.assertAlmostEqual(0.125, self.m.get_kratios()[13][1], 4)
        self.assertIn(Ka(13), self.m.get_transitions())

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
        self.m.add_rule(FixedElementRule(14, 0.5))

        self.assertTrue(self.m.has_rule(14))
        self.assertEqual(2, len(self.m.get_rules()))

        self.assertRaises(ValueError, self.m.add_rule, ElementByDifferenceRule(92))
        self.assertRaises(ValueError, self.m.add_rule, FixedElementRule(14, 0.1))
        self.assertRaises(ValueError, self.m.add_rule, FixedElementRule(29, 0.1))

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
        self.assertAlmostEqual(0.247, kratios[29][0], 4)
        self.assertAlmostEqual(0.004, kratios[29][1], 4)

    def testget_standards(self):
        standards = self.m.get_standards()

        self.assertEqual(1, len(standards))
        self.assertEqual('Copper', standards[29].material.name)

    def testget_rules(self):
        rules = self.m.get_rules()

        self.assertEqual(1, len(rules))

    def testfrom_xml(self):
        element = self.m.to_xml()
        m = Measurement.from_xml(element)

        self.assertAlmostEqual(20000, m.options.beam.energy_eV, 4)
        self.assertEqual(m.unknown_body, m.options.geometry.body)
        self.assertAlmostEqual(0.434867, m.detector.solidangle_sr, 4)

        transitions = m.get_transitions()
        self.assertEqual(1, len(transitions))
        self.assertIn(Ka(29), transitions)

        kratios = m.get_kratios()
        self.assertEqual(1, len(kratios))
        self.assertAlmostEqual(0.247, kratios[29][0], 4)
        self.assertAlmostEqual(0.004, kratios[29][1], 4)

        standards = m.get_standards()
        self.assertEqual(1, len(standards))
        self.assertEqual('Copper', standards[29].material.name)

        rules = m.get_rules()
        self.assertEqual(1, len(rules))

    def testto_xml(self):
        element = self.m.to_xml()

        children = list(element.find('kratios'))
        self.assertEqual(1, len(children))

        children = list(element.find('rules'))
        self.assertEqual(1, len(children))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

