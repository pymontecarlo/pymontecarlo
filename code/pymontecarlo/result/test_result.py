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
from StringIO import StringIO
from zipfile import ZipFile
import csv
from math import radians
from xml.etree.ElementTree import fromstring

# Third party modules.

# Local modules.
from pymontecarlo.result.result import \
    PhotonIntensityResult, TimeResult, ElectronFractionResult, create_intensity_dict
from pymontecarlo.input.detector import \
    PhotonIntensityDetector, TimeDetector, ElectronFractionDetector
from pymontecarlo.util.transition import Transition, K_family

import DrixUtilities.Files as Files

# Globals and constants variables.

class TestPhotonIntensityResult(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        intensities = {}

        self.t1 = Transition(29, 9, 4)
        ints = create_intensity_dict(self.t1,
                                     gcf=(1.0, 0.1), gbf=(2.0, 0.2), gnf=(3.0, 0.3), gt=(6.0, 0.4),
                                     ecf=(5.0, 0.5), ebf=(6.0, 0.6), enf=(7.0, 0.7), et=(18.0, 0.8))
        intensities.update(ints)

        self.t2 = K_family(14)
        ints = create_intensity_dict(self.t2,
                                     gcf=(11.0, 0.1), gbf=(12.0, 0.2), gnf=(13.0, 0.3), gt=(36.0, 0.4),
                                     ecf=(15.0, 0.5), ebf=(16.0, 0.6), enf=(17.0, 0.7), et=(48.0, 0.8))
        intensities.update(ints)

        self.t3 = Transition(29, siegbahn='La2')
        ints = create_intensity_dict(self.t3,
                                     gcf=(21.0, 0.1), gbf=(22.0, 0.2), gnf=(23.0, 0.3), gt=(66.0, 0.4),
                                     ecf=(25.0, 0.5), ebf=(26.0, 0.6), enf=(27.0, 0.7), et=(78.0, 0.8))
        intensities.update(ints)

        self.det = PhotonIntensityDetector((radians(35), radians(45)),
                                           (0, radians(360.0)))
        self.r = PhotonIntensityResult(self.det, intensities)

        self.results_zip = \
            Files.getCurrentModulePath(__file__, '../testdata/results.zip')

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def test__savezip__(self):
        fp = StringIO()
        zipfile = ZipFile(fp, 'w')
        self.r.__savezip__(zipfile, 'det1')

        reader = csv.reader(zipfile.open('det1.csv', 'r'))
        lines = list(reader)

        self.assertEqual(4, len(lines))
        self.assertEqual(18, len(lines[0]))
        self.assertEqual(18, len(lines[1]))
        self.assertEqual(18, len(lines[2]))
        self.assertEqual(18, len(lines[3]))

        zipfile.close()

    def test__loadzip__(self):
        zipfile = ZipFile(self.results_zip, 'r')
        r = PhotonIntensityResult.__loadzip__(zipfile, 'det1', self.det)

        self.assertEqual(3, len(r._intensities))

        val, err = r.intensity(self.t1)
        self.assertAlmostEqual(18.0, val, 4)
        self.assertAlmostEqual(0.8, err, 4)

        val, err = r.intensity(self.t2)
        self.assertAlmostEqual(48.0, val, 4)
        self.assertAlmostEqual(0.8, err, 4)

        val, err = r.intensity('Cu La')
        self.assertAlmostEqual(78.0 + 18.0, val, 4)
        self.assertAlmostEqual(4.378803, err, 4)

        zipfile.close()

    def testintensity(self):
        # Transition 1
        val, err = self.r.intensity(self.t1)
        self.assertAlmostEqual(18.0, val, 4)
        self.assertAlmostEqual(0.8, err, 4)

        val, err = self.r.intensity('Cu La1')
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

        # Transition 1 + 3
        val, err = self.r.intensity('Cu La')
        self.assertAlmostEqual(78.0 + 18.0, val, 4)
        self.assertAlmostEqual(4.378803, err, 4)

    def testhas_intensity(self):
        self.assertTrue(self.r.has_intensity(self.t1))
        self.assertTrue(self.r.has_intensity(self.t2))
        self.assertTrue(self.r.has_intensity(self.t3))
        self.assertFalse(self.r.has_intensity('Cu Ma'))

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
        self.assertEqual(3, len(list(self.r.iter_transitions())))

class TestTimeResult(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.det = TimeDetector()
        self.r = TimeResult(self.det, 5.0, (1.0, 0.5))

        self.results_zip = \
            Files.getCurrentModulePath(__file__, '../testdata/results.zip')

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(5.0, self.r.simulation_time_s, 4)
        self.assertAlmostEqual(1.0, self.r.simulation_speed_s[0], 4)
        self.assertAlmostEqual(0.5, self.r.simulation_speed_s[1], 4)

    def test__savezip__(self):
        fp = StringIO()
        zipfile = ZipFile(fp, 'w')
        self.r.__savezip__(zipfile, 'det2')

        element = fromstring(zipfile.open('det2.xml', 'r').read())

        self.assertEqual(2, len(element))

        zipfile.close()

    def test__loadzip__(self):
        zipfile = ZipFile(self.results_zip, 'r')
        r = TimeResult.__loadzip__(zipfile, 'det2', self.det)

        self.assertAlmostEqual(5.0, r.simulation_time_s, 4)
        self.assertAlmostEqual(1.0, r.simulation_speed_s[0], 4)
        self.assertAlmostEqual(0.5, r.simulation_speed_s[1], 4)

        zipfile.close()

class TestElectronFractionResult(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.det = ElectronFractionDetector()
        self.r = ElectronFractionResult(self.det, (1.0, 0.1), (2.0, 0.2), (3.0, 0.3))

        self.results_zip = \
            Files.getCurrentModulePath(__file__, '../testdata/results.zip')

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(1.0, self.r.absorbed[0], 4)
        self.assertAlmostEqual(0.1, self.r.absorbed[1], 4)
        self.assertAlmostEqual(2.0, self.r.backscattered[0], 4)
        self.assertAlmostEqual(0.2, self.r.backscattered[1], 4)
        self.assertAlmostEqual(3.0, self.r.transmitted[0], 4)
        self.assertAlmostEqual(0.3, self.r.transmitted[1], 4)

    def test__savezip__(self):
        fp = StringIO()
        zipfile = ZipFile(fp, 'w')
        self.r.__savezip__(zipfile, 'det3')

        element = fromstring(zipfile.open('det3.xml', 'r').read())

        self.assertEqual(3, len(element))

        zipfile.close()

    def test__loadzip__(self):
        zipfile = ZipFile(self.results_zip, 'r')
        r = ElectronFractionResult.__loadzip__(zipfile, 'det3', self.det)

        self.assertAlmostEqual(1.0, r.absorbed[0], 4)
        self.assertAlmostEqual(0.1, r.absorbed[1], 4)
        self.assertAlmostEqual(2.0, r.backscattered[0], 4)
        self.assertAlmostEqual(0.2, r.backscattered[1], 4)
        self.assertAlmostEqual(3.0, r.transmitted[0], 4)
        self.assertAlmostEqual(0.3, r.transmitted[1], 4)

        zipfile.close()

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
