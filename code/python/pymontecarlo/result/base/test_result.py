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
from pymontecarlo.result.base.result import PhotonIntensityResult, create_intensity_dict
from pymontecarlo.util.transition import Transition, K_family

# Globals and constants variables.

class TestPhotonIntensityResult(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        intensities = {}

        self.t1 = Transition(13, 9, 4)
        ints = create_intensity_dict(self.t1,
                                     gcf=(1.0, 0.1), gbf=(2.0, 0.2), gnf=(3.0, 0.3), gt=(6.0, 0.4),
                                     ecf=(5.0, 0.5), ebf=(6.0, 0.6), enf=(7.0, 0.7), et=(18.0, 0.8))
        intensities.update(ints)

        self.t2 = K_family(14)
        ints = create_intensity_dict(self.t2,
                                     gcf=(11.0, 0.1), gbf=(12.0, 0.2), gnf=(13.0, 0.3), gt=(36.0, 0.4),
                                     ecf=(15.0, 0.5), ebf=(16.0, 0.6), enf=(17.0, 0.7), et=(48.0, 0.8))
        intensities.update(ints)

        detector = None
        self.r = PhotonIntensityResult(detector, intensities)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testintensity(self):
        # Transition 1
        val, err = self.r.intensity(self.t1)
        self.assertAlmostEqual(18.0, val, 4)
        self.assertAlmostEqual(0.8, err, 4)

        val, err = self.r.intensity('Al La1')
        self.assertAlmostEqual(18.0, val, 4)
        self.assertAlmostEqual(0.8, err, 4)

        val, err = self.r.intensity(self.t1, absorption=False)
        self.assertAlmostEqual(6.0, val, 4)
        self.assertAlmostEqual(0.4, err, 4)

        val, err = self.r.intensity(self.t1, fluorescence=False)
        self.assertAlmostEqual(7.0, val, 4)
        self.assertAlmostEqual(0.7, err, 4)

        val, err = self.r.intensity(self.t1, absorption=False, fluorescence=False)
        self.assertAlmostEqual(3.0, val, 4)
        self.assertAlmostEqual(0.3, err, 4)

        # Transition 2
        val, err = self.r.intensity(self.t2)
        self.assertAlmostEqual(48.0, val, 4)
        self.assertAlmostEqual(0.8, err, 4)

        val, err = self.r.intensity('Si K')
        self.assertAlmostEqual(48.0, val, 4)
        self.assertAlmostEqual(0.8, err, 4)

        val, err = self.r.intensity(self.t2, absorption=False)
        self.assertAlmostEqual(36.0, val, 4)
        self.assertAlmostEqual(0.4, err, 4)

        val, err = self.r.intensity(self.t2, fluorescence=False)
        self.assertAlmostEqual(17.0, val, 4)
        self.assertAlmostEqual(0.7, err, 4)

        val, err = self.r.intensity(self.t2, absorption=False, fluorescence=False)
        self.assertAlmostEqual(13.0, val, 4)
        self.assertAlmostEqual(0.3, err, 4)

    def testcharacteristic_fluorescence(self):
        # Transition 1
        val, err = self.r.characteristic_fluorescence(self.t1)
        self.assertAlmostEqual(5.0, val, 4)
        self.assertAlmostEqual(0.5, err, 4)

        val, err = self.r.characteristic_fluorescence(self.t1, absorption=False)
        self.assertAlmostEqual(1.0, val, 4)
        self.assertAlmostEqual(0.1, err, 4)

        # Transition 2
        val, err = self.r.characteristic_fluorescence(self.t2)
        self.assertAlmostEqual(15.0, val, 4)
        self.assertAlmostEqual(0.5, err, 4)

        val, err = self.r.characteristic_fluorescence(self.t2, absorption=False)
        self.assertAlmostEqual(11.0, val, 4)
        self.assertAlmostEqual(0.1, err, 4)

    def testbremmstrahlung_fluorescence(self):
        # Transition 1
        val, err = self.r.bremsstrahlung_fluorescence(self.t1)
        self.assertAlmostEqual(6.0, val, 4)
        self.assertAlmostEqual(0.6, err, 4)

        val, err = self.r.bremsstrahlung_fluorescence(self.t1, absorption=False)
        self.assertAlmostEqual(2.0, val, 4)
        self.assertAlmostEqual(0.2, err, 4)

        # Transition 2
        val, err = self.r.bremsstrahlung_fluorescence(self.t2)
        self.assertAlmostEqual(16.0, val, 4)
        self.assertAlmostEqual(0.6, err, 4)

        val, err = self.r.bremsstrahlung_fluorescence(self.t2, absorption=False)
        self.assertAlmostEqual(12.0, val, 4)
        self.assertAlmostEqual(0.2, err, 4)

    def testfluorescence(self):
        # Transition 1
        val, err = self.r.fluorescence(self.t1)
        self.assertAlmostEqual(11.0, val, 4)
        self.assertAlmostEqual(1.5, err, 4)

        val, err = self.r.fluorescence(self.t1, absorption=False)
        self.assertAlmostEqual(3.0, val, 4)
        self.assertAlmostEqual(0.7, err, 4)

        # Transition 2
        val, err = self.r.fluorescence(self.t2)
        self.assertAlmostEqual(31.0, val, 4)
        self.assertAlmostEqual(1.5, err, 4)

        val, err = self.r.fluorescence(self.t2, absorption=False)
        self.assertAlmostEqual(23.0, val, 4)
        self.assertAlmostEqual(0.7, err, 4)

    def testabsorption(self):
        # Transition 1
        val, err = self.r.absorption(self.t1)
        self.assertAlmostEqual(12.0, val, 4)
        self.assertAlmostEqual(1.2, err, 4)

        val, err = self.r.absorption(self.t1, fluorescence=False)
        self.assertAlmostEqual(4.0, val, 4)
        self.assertAlmostEqual(1.0, err, 4)

        # Transition 2
        val, err = self.r.absorption(self.t2)
        self.assertAlmostEqual(12.0, val, 4)
        self.assertAlmostEqual(1.2, err, 4)

        val, err = self.r.absorption(self.t2, fluorescence=False)
        self.assertAlmostEqual(4.0, val, 4)
        self.assertAlmostEqual(1.0, err, 4)

    def testiter_transition(self):
        self.assertEqual(2, len(list(self.r.iter_transitions())))


if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
