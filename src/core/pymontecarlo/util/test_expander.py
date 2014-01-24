#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
from operator import attrgetter
from math import radians as d2r

# Third party modules.

# Local modules.
from pymontecarlo.options.expander import \
    Expander, ExpanderSingleDetector, ExpanderSingleDetectorSameOpening
from pymontecarlo.options.options import Options
from pymontecarlo.options.detector import \
    (TimeDetector, ElectronFractionDetector, ShowersStatisticsDetector,
     PhotonIntensityDetector, PhotonDepthDetector)

# Globals and constants variables.

class TestExpander(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.ops = Options("op1")
        self.ops.beam.energy_eV = [5e3, 10e3, 15e3]

        self.expander = Expander()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testexpand(self):
        opss = self.expander.expand(self.ops)
        self.assertEqual(3, len(opss))

        names = map(attrgetter('name'), opss)
        self.assertIn('op1+energy_eV=5000.0', names)
        self.assertIn('op1+energy_eV=10000.0', names)
        self.assertIn('op1+energy_eV=15000.0', names)

    def testis_expandable(self):
        self.assertTrue(self.expander.is_expandable(self.ops))

        self.ops.beam.energy_eV = [5e3]
        self.assertFalse(self.expander.is_expandable(self.ops))

class TestExpanderSingleDetector(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.ops = Options("op1")
        self.ops.detectors['det1a'] = TimeDetector()
        self.ops.detectors['det2a'] = ElectronFractionDetector()
        self.ops.detectors['det3'] = ShowersStatisticsDetector()

        self.expander = ExpanderSingleDetector([TimeDetector,
                                                ElectronFractionDetector])

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testexpand_noduplicates(self):
        opss = self.expander.expand(self.ops)
        self.assertEqual(1, len(opss))
        self.assertEqual(3, len(opss[0].detectors))

    def testexpand_duplicates(self):
        self.ops.detectors['det1b'] = TimeDetector()
        opss = self.expander.expand(self.ops)

        self.assertEqual(2, len(opss))

        self.assertEqual("op1+0", opss[0].name)
        self.assertEqual(3, len(opss[0].detectors))
        if 'det1a' in opss[0].detectors:
            self.assertNotIn('det1b', opss[0].detectors)
        if 'det1b' in opss[0].detectors:
            self.assertNotIn('det1a', opss[0].detectors)

        self.assertEqual("op1+1", opss[1].name)
        self.assertEqual(3, len(opss[1].detectors))
        if 'det1a' in opss[1].detectors:
            self.assertNotIn('det1b', opss[1].detectors)
        if 'det1a' in opss[1].detectors:
            self.assertNotIn('det1b', opss[1].detectors)

    def testexpand_duplicates2(self):
        self.ops.detectors['det1b'] = TimeDetector()
        self.ops.detectors['det2b'] = ElectronFractionDetector()
        opss = self.expander.expand(self.ops)

        self.assertEqual(4, len(opss))

        self.assertEqual(3, len(opss[0].detectors))
        if 'det1a' in opss[0].detectors:
            self.assertNotIn('det1b', opss[0].detectors)
        if 'det1b' in opss[0].detectors:
            self.assertNotIn('det1a', opss[0].detectors)
        if 'det2a' in opss[0].detectors:
            self.assertNotIn('det2b', opss[0].detectors)
        if 'det2b' in opss[0].detectors:
            self.assertNotIn('det2a', opss[0].detectors)

        self.assertEqual(3, len(opss[1].detectors))
        if 'det1a' in opss[1].detectors:
            self.assertNotIn('det1b', opss[1].detectors)
        if 'det1b' in opss[1].detectors:
            self.assertNotIn('det1a', opss[1].detectors)
        if 'det2a' in opss[1].detectors:
            self.assertNotIn('det2b', opss[1].detectors)
        if 'det2b' in opss[1].detectors:
            self.assertNotIn('det2a', opss[1].detectors)

        self.assertEqual(3, len(opss[0].detectors))
        if 'det1a' in opss[2].detectors:
            self.assertNotIn('det1b', opss[2].detectors)
        if 'det1b' in opss[2].detectors:
            self.assertNotIn('det1a', opss[2].detectors)
        if 'det2a' in opss[2].detectors:
            self.assertNotIn('det2b', opss[2].detectors)
        if 'det2b' in opss[2].detectors:
            self.assertNotIn('det2a', opss[2].detectors)

        self.assertEqual(3, len(opss[0].detectors))
        if 'det1a' in opss[3].detectors:
            self.assertNotIn('det1b', opss[3].detectors)
        if 'det1b' in opss[3].detectors:
            self.assertNotIn('det1a', opss[3].detectors)
        if 'det2a' in opss[3].detectors:
            self.assertNotIn('det2b', opss[3].detectors)
        if 'det2b' in opss[3].detectors:
            self.assertNotIn('det2a', opss[3].detectors)

    def testis_expandable(self):
        self.assertFalse(self.expander.is_expandable(self.ops))

        self.ops.detectors['det1b'] = TimeDetector()
        self.assertTrue(self.expander.is_expandable(self.ops))

        self.ops.detectors['det2b'] = ElectronFractionDetector()
        self.assertTrue(self.expander.is_expandable(self.ops))

class TestExpanderSingleDetectorSameOpening(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.ops = Options("op1")
        self.ops.detectors['det1a'] = \
            PhotonIntensityDetector((d2r(35.0), d2r(45.0)), (0.0, d2r(360.0)))
        self.ops.detectors['det1b'] = \
            PhotonIntensityDetector((d2r(30.0), d2r(40.0)), (0.0, d2r(360.0)))
        self.ops.detectors['det2a'] = \
            PhotonDepthDetector((d2r(30.0), d2r(40.0)), (0.0, d2r(360.0)), 100)
        self.ops.detectors['det3'] = ShowersStatisticsDetector()

        self.expander = ExpanderSingleDetectorSameOpening([])

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testexpand_noduplicates(self):
        del self.ops.detectors['det1a']

        opss = self.expander.expand(self.ops)
        self.assertEqual(1, len(opss))

    def testexpand_duplicates(self):
        opss = self.expander.expand(self.ops)

        self.assertEqual(2, len(opss))

        for i in range(2):
            if 'det1a' in opss[i].detectors:
                self.assertNotIn('det1b', opss[i].detectors)
                self.assertNotIn('det2a', opss[i].detectors)
            if 'det1b' in opss[i].detectors:
                self.assertNotIn('det1a', opss[i].detectors)

    def testis_expandable(self):
        self.assertTrue(self.expander.is_expandable(self.ops))

        del self.ops.detectors['det1a']
        self.assertFalse(self.expander.is_expandable(self.ops))

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
