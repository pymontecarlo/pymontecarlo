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
import os
from xml.etree.ElementTree import fromstring

# Third party modules.
import numpy as np

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.output.result import \
    (PhotonIntensityResult,
     PhotonSpectrumResult,
     PhiRhoZResult,
     TimeResult,
     ElectronFractionResult,
     create_intensity_dict,
     create_phirhoz_dict,
     Trajectory,
     TrajectoryResult,
     ShowersStatisticsResult,
     _ChannelsResult)
from pymontecarlo.util.transition import Transition, K_family

# Globals and constants variables.
from pymontecarlo.input.particle import ELECTRON, PHOTON
from pymontecarlo.input.collision import NO_COLLISION, HARD_INELASTIC
from pymontecarlo.output.result import EXIT_STATE_ABSORBED, EXIT_STATE_TRANSMITTED

class TestPhotonIntensityResult(TestCase):

    def setUp(self):
        TestCase.setUp(self)

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

        self.r = PhotonIntensityResult(intensities)

        self.results_zip = os.path.join(os.path.dirname(__file__),
                                        '../testdata/results.zip')

    def tearDown(self):
        TestCase.tearDown(self)

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
        r = PhotonIntensityResult.__loadzip__(zipfile, 'det1')

        self.assertEqual(3, len(r._intensities))

        val, err = r.intensity(self.t1)
        self.assertAlmostEqual(18.0, val, 4)
        self.assertAlmostEqual(0.8, err, 4)

        val, err = r.intensity(self.t2)
        self.assertAlmostEqual(48.0, val, 4)
        self.assertAlmostEqual(0.8, err, 4)

        val, err = r.intensity('Cu La')
        self.assertAlmostEqual(78.0 + 18.0, val, 4)
        self.assertAlmostEqual(1.1314, err, 4)

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
        self.assertAlmostEqual(1.1314, err, 4)

    def testhas_intensity(self):
        self.assertTrue(self.r.has_intensity(self.t1))
        self.assertTrue(self.r.has_intensity(self.t2))
        self.assertTrue(self.r.has_intensity(self.t3))
        self.assertFalse(self.r.has_intensity('U Ma'))

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

    def testiter_transitions(self):
        self.assertEqual(3, len(list(self.r.iter_transitions())))

class TestPhotonSpectrumResult(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        total = [6.0, 9.0, 1.0, 5.0]
        total_unc = [0.1, 0.5, 0.9, 0.05]
        background = [1.0, 2.0, 2.0, 0.5]
        background_unc = [0.05, 0.04, 0.03, 0.02]

        self.r = PhotonSpectrumResult(1.0, 0.5, total, total_unc,
                                      background, background_unc)

        self.results_zip = os.path.join(os.path.dirname(__file__),
                                        '../testdata/results.zip')

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(1.0, self.r.energy_offset_eV, 4)
        self.assertAlmostEqual(0.5, self.r.energy_channel_width_eV, 4)

    def test__savezip__(self):
        fp = StringIO()
        zipfile = ZipFile(fp, 'w')
        self.r.__savezip__(zipfile, 'det4')

        reader = csv.reader(zipfile.open('det4.csv', 'r'))
        lines = list(reader)

        self.assertEqual(5, len(lines))
        self.assertEqual(5, len(lines[0]))
        self.assertEqual(5, len(lines[1]))
        self.assertEqual(5, len(lines[2]))
        self.assertEqual(5, len(lines[3]))
        self.assertEqual(5, len(lines[4]))

        self.assertAlmostEqual(1.0, float(lines[1][0]), 4)
        self.assertAlmostEqual(1.5, float(lines[2][0]), 4)

        self.assertAlmostEqual(6.0, float(lines[1][1]), 4)
        self.assertAlmostEqual(0.1, float(lines[1][2]), 4)
        self.assertAlmostEqual(1.0, float(lines[1][3]), 4)
        self.assertAlmostEqual(0.05, float(lines[1][4]), 4)

        zipfile.close()

    def test__loadzip__(self):
        zipfile = ZipFile(self.results_zip, 'r')
        r = PhotonSpectrumResult.__loadzip__(zipfile, 'det4')

        self.assertAlmostEqual(1.0, r.energy_offset_eV, 4)
        self.assertAlmostEqual(0.5, r.energy_channel_width_eV, 4)

        es, ts, tus = r.get_total()
        self.assertEqual(4, len(es))
        self.assertEqual(4, len(ts))
        self.assertEqual(4, len(tus))

        es, bs, bus = r.get_background()
        self.assertEqual(4, len(es))
        self.assertEqual(4, len(bs))
        self.assertEqual(4, len(bus))

        zipfile.close()

    def testget_total(self):
        es, ts, tus = self.r.get_total()

        self.assertEqual(4, len(es))
        self.assertEqual(4, len(ts))
        self.assertEqual(4, len(tus))

        self.assertAlmostEqual(1.0, es[0], 4)
        self.assertAlmostEqual(6.0, ts[0], 4)
        self.assertAlmostEqual(0.1, tus[0], 4)

    def testget_background(self):
        es, bs, bus = self.r.get_background()

        self.assertEqual(4, len(es))
        self.assertEqual(4, len(bs))
        self.assertEqual(4, len(bus))

        self.assertAlmostEqual(1.0, es[0], 4)
        self.assertAlmostEqual(1.0, bs[0], 4)
        self.assertAlmostEqual(0.05, bus[0], 4)

    def testtotal_intensity(self):
        val, unc = self.r.total_intensity(0.0)
        self.assertAlmostEqual(0.0, val, 4)
        self.assertAlmostEqual(0.0, unc, 4)

        val, unc = self.r.total_intensity(1.0)
        self.assertAlmostEqual(6.0, val, 4)
        self.assertAlmostEqual(0.1, unc, 4)

        val, unc = self.r.total_intensity(1.2)
        self.assertAlmostEqual(6.0, val, 4)
        self.assertAlmostEqual(0.1, unc, 4)

        val, unc = self.r.total_intensity(1.5)
        self.assertAlmostEqual(9.0, val, 4)
        self.assertAlmostEqual(0.5, unc, 4)

        val, unc = self.r.total_intensity(2.5)
        self.assertAlmostEqual(5.0, val, 4)
        self.assertAlmostEqual(0.05, unc, 4)

        val, unc = self.r.total_intensity(3.0)
        self.assertAlmostEqual(0.0, val, 4)
        self.assertAlmostEqual(0.0, unc, 4)

    def testbackground_intensity(self):
        val, unc = self.r.background_intensity(0.0)
        self.assertAlmostEqual(0.0, val, 4)
        self.assertAlmostEqual(0.0, unc, 4)

        val, unc = self.r.background_intensity(1.0)
        self.assertAlmostEqual(1.0, val, 4)
        self.assertAlmostEqual(0.05, unc, 4)

        val, unc = self.r.background_intensity(1.2)
        self.assertAlmostEqual(1.0, val, 4)
        self.assertAlmostEqual(0.05, unc, 4)

        val, unc = self.r.background_intensity(1.5)
        self.assertAlmostEqual(2.0, val, 4)
        self.assertAlmostEqual(0.04, unc, 4)

        val, unc = self.r.background_intensity(2.5)
        self.assertAlmostEqual(0.5, val, 4)
        self.assertAlmostEqual(0.02, unc, 4)

        val, unc = self.r.background_intensity(3.0)
        self.assertAlmostEqual(0.0, val, 4)
        self.assertAlmostEqual(0.0, unc, 4)

class TestPhiRhoZResult(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.t1 = Transition(29, 9, 4)

        gnf_zs = [1.0, 2.0, 3.0, 4.0]
        gnf_values = [0.0, 5.0, 4.0, 1.0]
        gnf_uncs = [0.01, 0.02, 0.03, 0.04]

        gt_zs = [1.0, 2.0, 3.0, 4.0]
        gt_values = [10.0, 15.0, 14.0, 11.0]
        gt_uncs = [0.11, 0.12, 0.13, 0.14]

        enf_zs = [1.0, 2.0, 3.0, 4.0]
        enf_values = [20.0, 25.0, 24.0, 21.0]
        enf_uncs = [0.21, 0.22, 0.23, 0.24]

        et_zs = [1.0, 2.0, 3.0, 4.0]
        et_values = [30.0, 35.0, 34.0, 31.0]
        et_uncs = [0.31, 0.32, 0.33, 0.34]

        distributions = \
            create_phirhoz_dict(self.t1,
                                gnf=(gnf_zs, gnf_values, gnf_uncs),
                                gt=(gt_zs, gt_values, gt_uncs),
                                enf=(enf_zs, enf_values, enf_uncs),
                                et=(et_zs, et_values, et_uncs))

        self.r = PhiRhoZResult(distributions)

        self.results_zip = os.path.join(os.path.dirname(__file__),
                                        '../testdata/results.zip')

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def test__savezip__(self):
        fp = StringIO()
        zipfile = ZipFile(fp, 'w')
        self.r.__savezip__(zipfile, 'det5')

        names = zipfile.namelist()
        self.assertIn('det5+Cu_La1+gnf.csv', names)
        self.assertIn('det5+Cu_La1+gt.csv', names)
        self.assertIn('det5+Cu_La1+enf.csv', names)
        self.assertIn('det5+Cu_La1+et.csv', names)

        zipfile.close()

    def test__loadzip__(self):
        zipfile = ZipFile(self.results_zip, 'r')
        r = PhiRhoZResult.__loadzip__(zipfile, 'det5')

        zs, values, uncs = r.get(self.t1, absorption=False, fluorescence=False)
        self.assertEqual(4, len(zs))
        self.assertEqual(4, len(values))
        self.assertEqual(4, len(uncs))
        self.assertAlmostEqual(1.0, zs[0], 4)
        self.assertAlmostEqual(0.0, values[0], 4)
        self.assertAlmostEqual(0.01, uncs[0], 4)

        zs, values, uncs = r.get(self.t1, absorption=False, fluorescence=True)
        self.assertEqual(4, len(zs))
        self.assertEqual(4, len(values))
        self.assertEqual(4, len(uncs))
        self.assertAlmostEqual(1.0, zs[0], 4)
        self.assertAlmostEqual(10.0, values[0], 4)
        self.assertAlmostEqual(0.11, uncs[0], 4)

        zs, values, uncs = r.get(self.t1, absorption=True, fluorescence=False)
        self.assertEqual(4, len(zs))
        self.assertEqual(4, len(values))
        self.assertEqual(4, len(uncs))
        self.assertAlmostEqual(1.0, zs[0], 4)
        self.assertAlmostEqual(20.0, values[0], 4)
        self.assertAlmostEqual(0.21, uncs[0], 4)

        zs, values, uncs = r.get(self.t1, absorption=True, fluorescence=True)
        self.assertEqual(4, len(zs))
        self.assertEqual(4, len(values))
        self.assertEqual(4, len(uncs))
        self.assertAlmostEqual(1.0, zs[0], 4)
        self.assertAlmostEqual(30.0, values[0], 4)
        self.assertAlmostEqual(0.31, uncs[0], 4)
#
        zipfile.close()

    def testexists(self):
        self.assertTrue(self.r.exists(self.t1))
        self.assertTrue(self.r.exists('Cu La1'))
        self.assertFalse(self.r.exists('Cu Ka1'))

    def testget(self):
        zs, values, uncs = self.r.get(self.t1, absorption=False, fluorescence=False)
        self.assertEqual(4, len(zs))
        self.assertEqual(4, len(values))
        self.assertEqual(4, len(uncs))
        self.assertAlmostEqual(1.0, zs[0], 4)
        self.assertAlmostEqual(0.0, values[0], 4)
        self.assertAlmostEqual(0.01, uncs[0], 4)

        zs, values, uncs = self.r.get(self.t1, absorption=False, fluorescence=True)
        self.assertEqual(4, len(zs))
        self.assertEqual(4, len(values))
        self.assertEqual(4, len(uncs))
        self.assertAlmostEqual(1.0, zs[0], 4)
        self.assertAlmostEqual(10.0, values[0], 4)
        self.assertAlmostEqual(0.11, uncs[0], 4)

        zs, values, uncs = self.r.get(self.t1, absorption=True, fluorescence=False)
        self.assertEqual(4, len(zs))
        self.assertEqual(4, len(values))
        self.assertEqual(4, len(uncs))
        self.assertAlmostEqual(1.0, zs[0], 4)
        self.assertAlmostEqual(20.0, values[0], 4)
        self.assertAlmostEqual(0.21, uncs[0], 4)

        zs, values, uncs = self.r.get(self.t1, absorption=True, fluorescence=True)
        self.assertEqual(4, len(zs))
        self.assertEqual(4, len(values))
        self.assertEqual(4, len(uncs))
        self.assertAlmostEqual(1.0, zs[0], 4)
        self.assertAlmostEqual(30.0, values[0], 4)
        self.assertAlmostEqual(0.31, uncs[0], 4)

    def testintegral(self):
        val = self.r.integral(self.t1, absorption=False, fluorescence=False)
        self.assertAlmostEqual(10.0, val, 4)

        val = self.r.integral(self.t1, absorption=False, fluorescence=True)
        self.assertAlmostEqual(50.0, val, 4)

        val = self.r.integral(self.t1, absorption=True, fluorescence=False)
        self.assertAlmostEqual(90.0, val, 4)

        val = self.r.integral(self.t1, absorption=True, fluorescence=True)
        self.assertAlmostEqual(130.0, val, 4)

    def testfchi(self):
        val = self.r.fchi(self.t1, fluorescence=False)
        self.assertAlmostEqual(9.0, val, 4)

        val = self.r.fchi(self.t1, fluorescence=True)
        self.assertAlmostEqual(2.6, val, 4)

    def testiter_transition(self):
        self.assertEqual(1, len(list(self.r.iter_transitions())))

class TestTimeResult(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.r = TimeResult(5.0, (1.0, 0.5))

        self.results_zip = os.path.join(os.path.dirname(__file__),
                                        '../testdata/results.zip')

    def tearDown(self):
        TestCase.tearDown(self)

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
        r = TimeResult.__loadzip__(zipfile, 'det2')

        self.assertAlmostEqual(5.0, r.simulation_time_s, 4)
        self.assertAlmostEqual(1.0, r.simulation_speed_s[0], 4)
        self.assertAlmostEqual(0.5, r.simulation_speed_s[1], 4)

        zipfile.close()

class TestShowersStatisticsResult(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.r = ShowersStatisticsResult(6)

        self.results_zip = os.path.join(os.path.dirname(__file__),
                                        '../testdata/results.zip')

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(6, self.r.showers)

    def test__savezip__(self):
        fp = StringIO()
        zipfile = ZipFile(fp, 'w')
        self.r.__savezip__(zipfile, 'det7')

        element = fromstring(zipfile.open('det7.xml', 'r').read())

        self.assertEqual(1, len(element))

        zipfile.close()

    def test__loadzip__(self):
        zipfile = ZipFile(self.results_zip, 'r')
        r = ShowersStatisticsResult.__loadzip__(zipfile, 'det7')

        self.assertEqual(6, r.showers)

        zipfile.close()

class TestElectronFractionResult(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.r = ElectronFractionResult((1.0, 0.1), (2.0, 0.2), (3.0, 0.3))

        self.results_zip = os.path.join(os.path.dirname(__file__),
                                        '../testdata/results.zip')

    def tearDown(self):
        TestCase.tearDown(self)

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
        r = ElectronFractionResult.__loadzip__(zipfile, 'det3')

        self.assertAlmostEqual(1.0, r.absorbed[0], 4)
        self.assertAlmostEqual(0.1, r.absorbed[1], 4)
        self.assertAlmostEqual(2.0, r.backscattered[0], 4)
        self.assertAlmostEqual(0.2, r.backscattered[1], 4)
        self.assertAlmostEqual(3.0, r.transmitted[0], 4)
        self.assertAlmostEqual(0.3, r.transmitted[1], 4)

        zipfile.close()

class TestTrajectoryResult(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        interactions = np.array([[0.0, 0.0, 1.0, 20e3, -1], [1.0, 1.0, 1.0, 19e3, 2]])
        traj = Trajectory(True, ELECTRON, None, EXIT_STATE_ABSORBED, interactions)
        self.r = TrajectoryResult([traj])

        self.results_zip = os.path.join(os.path.dirname(__file__),
                                        '../testdata/results.zip')

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(1, len(self.r))

        trajectory = list(self.r)[0]
        self.assertTrue(trajectory.is_primary())
        self.assertFalse(trajectory.is_secondary())
        self.assertIs(ELECTRON, trajectory.particle)
        self.assertIsNone(trajectory.collision)
        self.assertEqual(EXIT_STATE_ABSORBED, trajectory.exit_state)
        self.assertEqual(2, len(trajectory.interactions))
        self.assertEqual(5, trajectory.interactions.shape[1])

    def test__savezip__(self):
        fp = StringIO()
        zipfile = ZipFile(fp, 'w')
        self.r.__savezip__(zipfile, 'det6')

        zipfile.close()

    def test__loadzip__(self):
        zipfile = ZipFile(self.results_zip, 'r')
        r = TrajectoryResult.__loadzip__(zipfile, 'det6')

        self.assertEqual(337, len(r))

        trajectory = list(r)[0]
        self.assertTrue(trajectory.is_primary())
        self.assertFalse(trajectory.is_secondary())
        self.assertIs(ELECTRON, trajectory.particle)
        self.assertIs(NO_COLLISION, trajectory.collision)
        self.assertEqual(EXIT_STATE_ABSORBED, trajectory.exit_state)
        self.assertEqual(317, len(trajectory.interactions))
        self.assertEqual(5, trajectory.interactions.shape[1])

        zipfile.close()

    def testfilter(self):
        zipfile = ZipFile(self.results_zip, 'r')
        r = TrajectoryResult.__loadzip__(zipfile, 'det6')
        zipfile.close()

        trajs = list(r.filter())
        self.assertEqual(337, len(trajs))

        trajs = list(r.filter(is_primary=True))
        self.assertEqual(50, len(trajs))

        trajs = list(r.filter(is_primary=False))
        self.assertEqual(287, len(trajs))

        trajs = list(r.filter(particles=ELECTRON))
        self.assertEqual(337, len(trajs))

        trajs = list(r.filter(particles=PHOTON))
        self.assertEqual(0, len(trajs))

        trajs = list(r.filter(collisions=HARD_INELASTIC))
        self.assertEqual(246, len(trajs))

        trajs = list(r.filter(exit_states=EXIT_STATE_TRANSMITTED))
        self.assertEqual(12, len(trajs))

        trajs = list(r.filter(is_primary=False, exit_states=EXIT_STATE_TRANSMITTED))
        self.assertEqual(0, len(trajs))

class Test_ChannelsResult(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        data = np.array([[0.0, 1.0, 0.1], [1.0, 2.0, 0.2], [2.0, 3.0, 0.3]])
        self.r = _ChannelsResult(data)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(3, len(self.r))

        data = self.r.get_data()
        self.assertAlmostEqual(1.0, data[0][1], 4)
        self.assertAlmostEqual(0.2, data[1][2], 4)

    def test__loadzip__(self):
        fp = StringIO()
        zipfile = ZipFile(fp, 'w')
        self.r.__savezip__(zipfile, 'det8')
        zipfile.close()

        zipfile = ZipFile(fp, 'r')
        r = _ChannelsResult.__loadzip__(zipfile, 'det8')
        zipfile.close()

        self.assertEqual(3, len(r))

        data = r.get_data()
        self.assertAlmostEqual(1.0, data[0][1], 4)
        self.assertAlmostEqual(0.2, data[1][2], 4)

    def test__savezip__(self):
        fp = StringIO()
        zipfile = ZipFile(fp, 'w')
        self.r.__savezip__(zipfile, 'det8')

        zipfile.close()

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
