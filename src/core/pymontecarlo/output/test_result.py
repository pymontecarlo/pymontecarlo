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
import os
import tempfile

# Third party modules.
import numpy as np
import h5py

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.output.result import \
    (PhotonIntensityResult,
     PhotonSpectrumResult,
     PhotonDepthResult,
     TimeResult,
     ElectronFractionResult,
     create_intensity_dict,
     create_photondist_dict,
     Trajectory,
     TrajectoryResult,
     ShowersStatisticsResult,
     _ChannelsResult)
from pymontecarlo.util.transition import Transition, K_family

# Globals and constants variables.
from pymontecarlo.input.particle import ELECTRON
from pymontecarlo.input.collision import NO_COLLISION
from pymontecarlo.output.result import EXIT_STATE_ABSORBED

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

        self.results_h5 = os.path.join(os.path.dirname(__file__),
                                      '..', 'testdata', 'results',
                                      'photon_intensity.h5')

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def test__savehdf5__(self):
        fd, filepath = tempfile.mkstemp('.h5')
        hdf5file = h5py.File(filepath, 'w')
        self.r.__savehdf5__(hdf5file, 'det1')

        hdf5group = hdf5file['det1']
        self.assertEqual(3, len(hdf5group))

        dataset = hdf5group['Si K']
        self.assertAlmostEqual(11.0, dataset.attrs['gcf'][0], 4)
        self.assertAlmostEqual(0.1, dataset.attrs['gcf'][1], 4)
        self.assertAlmostEqual(12.0, dataset.attrs['gbf'][0], 4)
        self.assertAlmostEqual(0.2, dataset.attrs['gbf'][1], 4)
        self.assertAlmostEqual(13.0, dataset.attrs['gnf'][0], 4)
        self.assertAlmostEqual(0.3, dataset.attrs['gnf'][1], 4)
        self.assertAlmostEqual(36.0, dataset.attrs['gt'][0], 4)
        self.assertAlmostEqual(0.4, dataset.attrs['gt'][1], 4)
        self.assertAlmostEqual(15.0, dataset.attrs['ecf'][0], 4)
        self.assertAlmostEqual(0.5, dataset.attrs['ecf'][1], 4)
        self.assertAlmostEqual(16.0, dataset.attrs['ebf'][0], 4)
        self.assertAlmostEqual(0.6, dataset.attrs['ebf'][1], 4)
        self.assertAlmostEqual(17.0, dataset.attrs['enf'][0], 4)
        self.assertAlmostEqual(0.7, dataset.attrs['enf'][1], 4)
        self.assertAlmostEqual(48.0, dataset.attrs['et'][0], 4)
        self.assertAlmostEqual(0.8, dataset.attrs['et'][1], 4)

        hdf5file.close()
        os.close(fd)
        os.remove(filepath)

    def test__loadhdf5__(self):
        hdf5file = h5py.File(self.results_h5, 'r')
        r = PhotonIntensityResult.__loadhdf5__(hdf5file, 'det1')

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

        hdf5file.close()

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
#
class TestPhotonSpectrumResult(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        energies_eV = [1.0, 1.5, 2.0, 2.5]
        total_val = [6.0, 9.0, 1.0, 5.0]
        total_unc = [0.1, 0.5, 0.9, 0.05]
        background_val = [1.0, 2.0, 2.0, 0.5]
        background_unc = [0.05, 0.04, 0.03, 0.02]

        total = np.array([energies_eV, total_val, total_unc]).T
        background = np.array([energies_eV, background_val, background_unc]).T

        self.r = PhotonSpectrumResult(total, background)

        self.results_h5 = os.path.join(os.path.dirname(__file__), '..',
                                       'testdata', 'results',
                                       'photonspectrum.h5')

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(1.0, self.r.energy_offset_eV, 4)
        self.assertAlmostEqual(0.5, self.r.energy_channel_width_eV, 4)

    def test__savehdf5__(self):
        fd, filepath = tempfile.mkstemp('.h5')
        hdf5file = h5py.File(filepath, 'w')
        self.r.__savehdf5__(hdf5file, 'det4')

        hdf5group = hdf5file['det4']

        spectrum = hdf5group['total']
        self.assertEqual((4, 3), spectrum.shape)
        self.assertAlmostEqual(1.0, spectrum[0][0], 4)
        self.assertAlmostEqual(6.0, spectrum[0][1], 4)
        self.assertAlmostEqual(0.1, spectrum[0][2], 4)

        spectrum = hdf5group['background']
        self.assertEqual((4, 3), spectrum.shape)
        self.assertAlmostEqual(1.0, spectrum[0][0], 4)
        self.assertAlmostEqual(1.0, spectrum[0][1], 4)
        self.assertAlmostEqual(0.05, spectrum[0][2], 4)

        hdf5file.close()
        os.close(fd)
        os.remove(filepath)

    def test__loadhdf5__(self):
        hdf5file = h5py.File(self.results_h5, 'r')
        r = PhotonSpectrumResult.__loadhdf5__(hdf5file, 'det4')

        self.assertAlmostEqual(1.0, r.energy_offset_eV, 4)
        self.assertAlmostEqual(0.5, r.energy_channel_width_eV, 4)

        spectrum = r.get_total()
        self.assertEqual((4, 3), spectrum.shape)

        spectrum = r.get_background()
        self.assertEqual((4, 3), spectrum.shape)

        hdf5file.close()

    def testget_total(self):
        spectrum = self.r.get_total()

        self.assertEqual((4, 3), spectrum.shape)
        self.assertAlmostEqual(1.0, spectrum[0][0], 4)
        self.assertAlmostEqual(6.0, spectrum[0][1], 4)
        self.assertAlmostEqual(0.1, spectrum[0][2], 4)

    def testget_background(self):
        spectrum = self.r.get_background()

        self.assertEqual((4, 3), spectrum.shape)
        self.assertAlmostEqual(1.0, spectrum[0][0], 4)
        self.assertAlmostEqual(1.0, spectrum[0][1], 4)
        self.assertAlmostEqual(0.05, spectrum[0][2], 4)

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
#
class TestPhotonDepthResultResult(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.t1 = Transition(29, 9, 4)

        gnf_zs = [1.0, 2.0, 3.0, 4.0]
        gnf_values = [0.0, 5.0, 4.0, 1.0]
        gnf_uncs = [0.01, 0.02, 0.03, 0.04]
        gnf = np.array([gnf_zs, gnf_values, gnf_uncs]).T

        gt_zs = [1.0, 2.0, 3.0, 4.0]
        gt_values = [10.0, 15.0, 14.0, 11.0]
        gt_uncs = [0.11, 0.12, 0.13, 0.14]
        gt = np.array([gt_zs, gt_values, gt_uncs]).T

        enf_zs = [1.0, 2.0, 3.0, 4.0]
        enf_values = [20.0, 25.0, 24.0, 21.0]
        enf_uncs = [0.21, 0.22, 0.23, 0.24]
        enf = np.array([enf_zs, enf_values, enf_uncs]).T

        et_zs = [1.0, 2.0, 3.0, 4.0]
        et_values = [30.0, 35.0, 34.0, 31.0]
        et_uncs = [0.31, 0.32, 0.33, 0.34]
        et = np.array([et_zs, et_values, et_uncs]).T

        distributions = create_photondist_dict(self.t1, gnf, gt, enf, et)

        self.r = PhotonDepthResult(distributions)

        self.results_h5 = os.path.join(os.path.dirname(__file__), '..',
                                       'testdata', 'results', 'phirhoz.h5')

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def test__savehdf5__(self):
        fd, filepath = tempfile.mkstemp('.h5')
        hdf5file = h5py.File(filepath, 'w')
        self.r.__savehdf5__(hdf5file, 'det5')

        phirhoz = hdf5file['det5']['Cu La1']['gnf']
        self.assertEqual((4, 3), phirhoz.shape)
        self.assertAlmostEqual(1.0, phirhoz[0][0], 4)
        self.assertAlmostEqual(0.0, phirhoz[0][1], 4)
        self.assertAlmostEqual(0.01, phirhoz[0][2], 4)

        phirhoz = hdf5file['det5']['Cu La1']['gt']
        self.assertEqual((4, 3), phirhoz.shape)
        self.assertAlmostEqual(1.0, phirhoz[0][0], 4)
        self.assertAlmostEqual(10.0, phirhoz[0][1], 4)
        self.assertAlmostEqual(0.11, phirhoz[0][2], 4)

        phirhoz = hdf5file['det5']['Cu La1']['enf']
        self.assertEqual((4, 3), phirhoz.shape)
        self.assertAlmostEqual(1.0, phirhoz[0][0], 4)
        self.assertAlmostEqual(20.0, phirhoz[0][1], 4)
        self.assertAlmostEqual(0.21, phirhoz[0][2], 4)

        phirhoz = hdf5file['det5']['Cu La1']['et']
        self.assertEqual((4, 3), phirhoz.shape)
        self.assertAlmostEqual(1.0, phirhoz[0][0], 4)
        self.assertAlmostEqual(30.0, phirhoz[0][1], 4)
        self.assertAlmostEqual(0.31, phirhoz[0][2], 4)

        hdf5file.close()
        os.close(fd)
        os.remove(filepath)

    def test__loadhdf5__(self):
        hdf5file = h5py.File(self.results_h5, 'r')
        r = PhotonDepthResult.__loadhdf5__(hdf5file, 'det5')

        phirhoz = r.get(self.t1, absorption=False, fluorescence=False)
        self.assertEqual((4, 3), phirhoz.shape)
        self.assertAlmostEqual(1.0, phirhoz[0][0], 4)
        self.assertAlmostEqual(0.0, phirhoz[0][1], 4)
        self.assertAlmostEqual(0.01, phirhoz[0][2], 4)

        phirhoz = r.get(self.t1, absorption=False, fluorescence=True)
        self.assertEqual((4, 3), phirhoz.shape)
        self.assertAlmostEqual(1.0, phirhoz[0][0], 4)
        self.assertAlmostEqual(10.0, phirhoz[0][1], 4)
        self.assertAlmostEqual(0.11, phirhoz[0][2], 4)

        phirhoz = r.get(self.t1, absorption=True, fluorescence=False)
        self.assertEqual((4, 3), phirhoz.shape)
        self.assertAlmostEqual(1.0, phirhoz[0][0], 4)
        self.assertAlmostEqual(20.0, phirhoz[0][1], 4)
        self.assertAlmostEqual(0.21, phirhoz[0][2], 4)

        phirhoz = r.get(self.t1, absorption=True, fluorescence=True)
        self.assertEqual((4, 3), phirhoz.shape)
        self.assertAlmostEqual(1.0, phirhoz[0][0], 4)
        self.assertAlmostEqual(30.0, phirhoz[0][1], 4)
        self.assertAlmostEqual(0.31, phirhoz[0][2], 4)

        hdf5file.close()

    def testexists(self):
        self.assertTrue(self.r.exists(self.t1))
        self.assertTrue(self.r.exists('Cu La1'))
        self.assertFalse(self.r.exists('Cu Ka1'))

    def testget(self):
        phirhoz = self.r.get(self.t1, absorption=False, fluorescence=False)
        self.assertEqual((4, 3), phirhoz.shape)
        self.assertAlmostEqual(1.0, phirhoz[0][0], 4)
        self.assertAlmostEqual(0.0, phirhoz[0][1], 4)
        self.assertAlmostEqual(0.01, phirhoz[0][2], 4)

        phirhoz = self.r.get(self.t1, absorption=False, fluorescence=True)
        self.assertEqual((4, 3), phirhoz.shape)
        self.assertAlmostEqual(1.0, phirhoz[0][0], 4)
        self.assertAlmostEqual(10.0, phirhoz[0][1], 4)
        self.assertAlmostEqual(0.11, phirhoz[0][2], 4)

        phirhoz = self.r.get(self.t1, absorption=True, fluorescence=False)
        self.assertEqual((4, 3), phirhoz.shape)
        self.assertAlmostEqual(1.0, phirhoz[0][0], 4)
        self.assertAlmostEqual(20.0, phirhoz[0][1], 4)
        self.assertAlmostEqual(0.21, phirhoz[0][2], 4)

        phirhoz = self.r.get(self.t1, absorption=True, fluorescence=True)
        self.assertEqual((4, 3), phirhoz.shape)
        self.assertAlmostEqual(1.0, phirhoz[0][0], 4)
        self.assertAlmostEqual(30.0, phirhoz[0][1], 4)
        self.assertAlmostEqual(0.31, phirhoz[0][2], 4)

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

        self.results_h5 = os.path.join(os.path.dirname(__file__),
                                        '..', 'testdata', 'results', 'time.h5')

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(5.0, self.r.simulation_time_s, 4)
        self.assertAlmostEqual(1.0, self.r.simulation_speed_s[0], 4)
        self.assertAlmostEqual(0.5, self.r.simulation_speed_s[1], 4)

    def test__savehdf5__(self):
        fd, filepath = tempfile.mkstemp('.h5')
        hdf5file = h5py.File(filepath, 'w')
        self.r.__savehdf5__(hdf5file, 'det2')

        self.assertAlmostEqual(5.0, hdf5file['det2'].attrs['simulation_time_s'], 4)
        self.assertAlmostEqual(1.0, hdf5file['det2'].attrs['simulation_speed_s'][0], 4)
        self.assertAlmostEqual(0.5, hdf5file['det2'].attrs['simulation_speed_s'][1], 4)

        hdf5file.close()
        os.close(fd)
        os.remove(filepath)

    def test__loadhdf5__(self):
        hdf5file = h5py.File(self.results_h5, 'r')
        r = TimeResult.__loadhdf5__(hdf5file, 'det2')

        self.assertAlmostEqual(5.0, r.simulation_time_s, 4)
        self.assertAlmostEqual(1.0, r.simulation_speed_s[0], 4)
        self.assertAlmostEqual(0.5, r.simulation_speed_s[1], 4)

        hdf5file.close()

class TestShowersStatisticsResult(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.r = ShowersStatisticsResult(6)

        self.results_h5 = os.path.join(os.path.dirname(__file__),
                                        '..', 'testdata', 'results',
                                        'showers_statistics.h5')

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(6, self.r.showers)

    def test__savehdf5__(self):
        fd, filepath = tempfile.mkstemp('.h5')
        hdf5file = h5py.File(filepath, 'w')
        self.r.__savehdf5__(hdf5file, 'det7')

        self.assertEqual(6, hdf5file['det7'].attrs['showers'])

        hdf5file.close()
        os.close(fd)
        os.remove(filepath)

    def test__loadhdf5__(self):
        hdf5file = h5py.File(self.results_h5, 'r')
        r = ShowersStatisticsResult.__loadhdf5__(hdf5file, 'det7')

        self.assertEqual(6, r.showers)

        hdf5file.close()

class TestElectronFractionResult(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.r = ElectronFractionResult((1.0, 0.1), (2.0, 0.2), (3.0, 0.3))

        self.results_h5 = os.path.join(os.path.dirname(__file__),
                                        '..', 'testdata', 'results',
                                        'electron_fraction.h5')

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(1.0, self.r.absorbed[0], 4)
        self.assertAlmostEqual(0.1, self.r.absorbed[1], 4)
        self.assertAlmostEqual(2.0, self.r.backscattered[0], 4)
        self.assertAlmostEqual(0.2, self.r.backscattered[1], 4)
        self.assertAlmostEqual(3.0, self.r.transmitted[0], 4)
        self.assertAlmostEqual(0.3, self.r.transmitted[1], 4)

    def test__savehdf5__(self):
        fd, filepath = tempfile.mkstemp('.h5')
        hdf5file = h5py.File(filepath, 'w')
        self.r.__savehdf5__(hdf5file, 'det3')

        self.assertAlmostEqual(1.0, hdf5file['det3'].attrs['absorbed'][0], 4)
        self.assertAlmostEqual(0.1, hdf5file['det3'].attrs['absorbed'][1], 4)
        self.assertAlmostEqual(2.0, hdf5file['det3'].attrs['backscattered'][0], 4)
        self.assertAlmostEqual(0.2, hdf5file['det3'].attrs['backscattered'][1], 4)
        self.assertAlmostEqual(3.0, hdf5file['det3'].attrs['transmitted'][0], 4)
        self.assertAlmostEqual(0.3, hdf5file['det3'].attrs['transmitted'][1], 4)

        hdf5file.close()
        os.close(fd)
        os.remove(filepath)

    def test__loadhdf5__(self):
        hdf5file = h5py.File(self.results_h5, 'r')
        r = ElectronFractionResult.__loadhdf5__(hdf5file, 'det3')

        self.assertAlmostEqual(1.0, r.absorbed[0], 4)
        self.assertAlmostEqual(0.1, r.absorbed[1], 4)
        self.assertAlmostEqual(2.0, r.backscattered[0], 4)
        self.assertAlmostEqual(0.2, r.backscattered[1], 4)
        self.assertAlmostEqual(3.0, r.transmitted[0], 4)
        self.assertAlmostEqual(0.3, r.transmitted[1], 4)

        hdf5file.close()

class TestTrajectoryResult(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        interactions = np.array([[0.0, 0.0, 1.0, 20e3, -1], [1.0, 1.0, 1.0, 19e3, 2]])
        traj = Trajectory(True, ELECTRON, NO_COLLISION, EXIT_STATE_ABSORBED, interactions)
        self.r = TrajectoryResult([traj])

        self.results_h5 = os.path.join(os.path.dirname(__file__),
                                       '..', 'testdata', 'results', 'trajectory.h5')

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(1, len(self.r))

        trajectory = list(self.r)[0]
        self.assertTrue(trajectory.is_primary())
        self.assertFalse(trajectory.is_secondary())
        self.assertIs(ELECTRON, trajectory.particle)
        self.assertIs(NO_COLLISION, trajectory.collision)
        self.assertEqual(EXIT_STATE_ABSORBED, trajectory.exit_state)
        self.assertEqual(2, len(trajectory.interactions))
        self.assertEqual(5, trajectory.interactions.shape[1])

    def test__savehdf5__(self):
        fd, filepath = tempfile.mkstemp('.h5')
        hdf5file = h5py.File(filepath, 'w')
        self.r.__savehdf5__(hdf5file, 'det6')

        self.assertEqual(1, len(hdf5file['det6']))

        dataset = hdf5file['det6']['trajectory0']
        self.assertTrue(dataset.attrs['primary'])
        self.assertEqual(1, dataset.attrs['particle'])
        self.assertEqual(-1, dataset.attrs['collision'])
        self.assertEqual(3, dataset.attrs['exit_state'])
        self.assertEqual(2, len(dataset))

        hdf5file.close()
        os.close(fd)
        os.remove(filepath)

    def test__loadhdf5__(self):
        hdf5file = h5py.File(self.results_h5, 'r')
        r = TrajectoryResult.__loadhdf5__(hdf5file, 'det6')

        self.assertEqual(1, len(r))

        trajectory = list(r)[0]
        self.assertTrue(trajectory.is_primary())
        self.assertFalse(trajectory.is_secondary())
        self.assertIs(ELECTRON, trajectory.particle)
        self.assertIs(NO_COLLISION, trajectory.collision)
        self.assertEqual(EXIT_STATE_ABSORBED, trajectory.exit_state)
        self.assertEqual(2, len(trajectory.interactions))
        self.assertEqual(5, trajectory.interactions.shape[1])

        hdf5file.close()

class Test_ChannelsResult(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        data = np.array([[0.0, 1.0, 0.1], [1.0, 2.0, 0.2], [2.0, 3.0, 0.3]])
        self.r = _ChannelsResult(data)

        self.results_h5 = os.path.join(os.path.dirname(__file__),
                                       '..', 'testdata', 'results', '_channels.h5')

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(3, len(self.r))

        data = self.r.get_data()
        self.assertAlmostEqual(1.0, data[0][1], 4)
        self.assertAlmostEqual(0.2, data[1][2], 4)

    def test__savehdf5__(self):
        fd, filepath = tempfile.mkstemp('.h5')
        hdf5file = h5py.File(filepath, 'w')
        self.r.__savehdf5__(hdf5file, 'det8')

        dataset = hdf5file['det8']['data']
        self.assertAlmostEqual(1.0, dataset[0][1], 4)
        self.assertAlmostEqual(0.2, dataset[1][2], 4)

        hdf5file.close()
        os.close(fd)
        os.remove(filepath)

    def test__loadhdf5__(self):
        hdf5file = h5py.File(self.results_h5, 'r')
        r = _ChannelsResult.__loadhdf5__(hdf5file, 'det8')

        data = r.get_data()
        self.assertAlmostEqual(1.0, data[0][1], 4)
        self.assertAlmostEqual(0.2, data[1][2], 4)

        hdf5file.close()

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
