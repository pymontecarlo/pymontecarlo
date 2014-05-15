#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging

# Third party modules.
from pyxray.transition import Transition, K_family
import h5py
import numpy as np

# Local modules.
from pymontecarlo.fileformat.results.result import \
    (PhotonIntensityResultHDF5Handler, PhotonSpectrumResultHDF5Handler,
     PhotonDepthResultHDF5Handler, PhotonRadialResultHDF5Handler,
     TimeResultHDF5Handler, ShowersStatisticsResultHDF5Handler,
     ElectronFractionResultHDF5Handler, TrajectoryResultHDF5Handler,
     BackscatteredElectronEnergyResultHDF5Handler,
     TransmittedElectronEnergyResultHDF5Handler,
     BackscatteredElectronPolarAngularResultHDF5Handler,
     BackscatteredElectronRadialResultHDF5Handler)

from pymontecarlo.results.result import \
    (PhotonKey, PhotonIntensityResult, PhotonSpectrumResult,
     PhotonDepthResult, PhotonRadialResult, create_photondist_dict,
     TimeResult, ShowersStatisticsResult, ElectronFractionResult,
     Trajectory, TrajectoryResult, BackscatteredElectronEnergyResult,
     TransmittedElectronEnergyResult, BackscatteredElectronPolarAngularResult,
     BackscatteredElectronRadialResult)

# Globals and constants variables.
from pymontecarlo.options.particle import ELECTRON
from pymontecarlo.options.collision import NO_COLLISION
from pymontecarlo.results.result import EXIT_STATE_ABSORBED

class TestPhotonIntensityResultHDF5Handler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.hdf5file = h5py.File('test.h5', 'a', driver='core', backing_store=False)
        self.h = PhotonIntensityResultHDF5Handler()

        t1 = Transition(29, 9, 4)
        t2 = K_family(14)
        t3 = Transition(29, siegbahn='La2')

        intensities = {}
        intensities[PhotonKey(t1, False, PhotonKey.P)] = (3.0, 0.3)
        intensities[PhotonKey(t1, False, PhotonKey.C)] = (1.0, 0.1)
        intensities[PhotonKey(t1, False, PhotonKey.B)] = (2.0, 0.2)
        intensities[PhotonKey(t1, True, PhotonKey.P)] = (7.0, 0.7)
        intensities[PhotonKey(t1, True, PhotonKey.C)] = (5.0, 0.5)
        intensities[PhotonKey(t1, True, PhotonKey.B)] = (6.0, 0.6)

        intensities[PhotonKey(t2, False, PhotonKey.P)] = (13.0, 0.3)
        intensities[PhotonKey(t2, False, PhotonKey.C)] = (11.0, 0.1)
        intensities[PhotonKey(t2, False, PhotonKey.B)] = (12.0, 0.2)
        intensities[PhotonKey(t2, True, PhotonKey.P)] = (17.0, 0.7)
        intensities[PhotonKey(t2, True, PhotonKey.C)] = (15.0, 0.5)
        intensities[PhotonKey(t2, True, PhotonKey.B)] = (16.0, 0.6)

        intensities[PhotonKey(t3, False, PhotonKey.P)] = (23.0, 0.3)
        intensities[PhotonKey(t3, False, PhotonKey.C)] = (21.0, 0.1)
        intensities[PhotonKey(t3, False, PhotonKey.B)] = (22.0, 0.2)
        intensities[PhotonKey(t3, True, PhotonKey.P)] = (27.0, 0.7)
        intensities[PhotonKey(t3, True, PhotonKey.C)] = (25.0, 0.5)
        intensities[PhotonKey(t3, True, PhotonKey.B)] = (26.0, 0.6)

        self.obj = PhotonIntensityResult(intensities)

        self.group = self.h.convert(self.obj, self.hdf5file.create_group('det'))

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.hdf5file.close()

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.group))

    def testparse(self):
        obj = self.h.parse(self.group)

        self.assertEqual(18, len(obj._intensities))

        val, err = obj.intensity(Transition(29, 9, 4))
        self.assertAlmostEqual(18.0, val, 4)
        self.assertAlmostEqual(1.0488, err, 4)

        val, err = obj.intensity(K_family(14))
        self.assertAlmostEqual(48.0, val, 4)
        self.assertAlmostEqual(1.0488, err, 4)

        val, err = obj.intensity('Cu La')
        self.assertAlmostEqual(78.0 + 18.0, val, 4)
        self.assertAlmostEqual(1.4832, err, 4)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        group = self.hdf5file['det']

        self.assertEqual(3, len(group))

        dataset = group['Si K']
        self.assertAlmostEqual(11.0, dataset.attrs['gcf'][0], 4)
        self.assertAlmostEqual(0.1, dataset.attrs['gcf'][1], 4)
        self.assertAlmostEqual(12.0, dataset.attrs['gbf'][0], 4)
        self.assertAlmostEqual(0.2, dataset.attrs['gbf'][1], 4)
        self.assertAlmostEqual(13.0, dataset.attrs['gnf'][0], 4)
        self.assertAlmostEqual(0.3, dataset.attrs['gnf'][1], 4)
        self.assertAlmostEqual(15.0, dataset.attrs['ecf'][0], 4)
        self.assertAlmostEqual(0.5, dataset.attrs['ecf'][1], 4)
        self.assertAlmostEqual(16.0, dataset.attrs['ebf'][0], 4)
        self.assertAlmostEqual(0.6, dataset.attrs['ebf'][1], 4)
        self.assertAlmostEqual(17.0, dataset.attrs['enf'][0], 4)
        self.assertAlmostEqual(0.7, dataset.attrs['enf'][1], 4)

class TestPhotonSpectrumResultHDF5Handler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.hdf5file = h5py.File('test.h5', 'a', driver='core', backing_store=False)
        self.h = PhotonSpectrumResultHDF5Handler()

        energies_eV = [1.0, 1.5, 2.0, 2.5]
        total_val = [6.0, 9.0, 1.0, 5.0]
        total_unc = [0.1, 0.5, 0.9, 0.05]
        background_val = [1.0, 2.0, 2.0, 0.5]
        background_unc = [0.05, 0.04, 0.03, 0.02]

        total = np.array([energies_eV, total_val, total_unc]).T
        background = np.array([energies_eV, background_val, background_unc]).T
        self.obj = PhotonSpectrumResult(total, background)

        self.group = self.h.convert(self.obj, self.hdf5file.create_group('det'))

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.hdf5file.close()

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.group))

    def testparse(self):
        obj = self.h.parse(self.group)

        self.assertAlmostEqual(1.0, obj.energy_offset_eV, 4)
        self.assertAlmostEqual(0.5, obj.energy_channel_width_eV, 4)

        spectrum = obj.get_total()
        self.assertEqual((4, 3), spectrum.shape)

        spectrum = obj.get_background()
        self.assertEqual((4, 3), spectrum.shape)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        group = self.hdf5file['det']

        spectrum = group['total']
        self.assertEqual((4, 3), spectrum.shape)
        self.assertAlmostEqual(1.0, spectrum[0][0], 4)
        self.assertAlmostEqual(6.0, spectrum[0][1], 4)
        self.assertAlmostEqual(0.1, spectrum[0][2], 4)

        spectrum = group['background']
        self.assertEqual((4, 3), spectrum.shape)
        self.assertAlmostEqual(1.0, spectrum[0][0], 4)
        self.assertAlmostEqual(1.0, spectrum[0][1], 4)
        self.assertAlmostEqual(0.05, spectrum[0][2], 4)

class TestPhotonDepthResultHDF5Handler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.hdf5file = h5py.File('test.h5', 'a', driver='core', backing_store=False)
        self.h = PhotonDepthResultHDF5Handler()

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

        distributions = create_photondist_dict(Transition(29, 9, 4), gnf, gt, enf, et)
        self.obj = PhotonDepthResult(distributions)

        self.group = self.h.convert(self.obj, self.hdf5file.create_group('det'))

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.hdf5file.close()

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.group))

    def testparse(self):
        obj = self.h.parse(self.group)

        phirhoz = obj.get(Transition(29, 9, 4), absorption=False, fluorescence=False)
        self.assertEqual((4, 3), phirhoz.shape)
        self.assertAlmostEqual(1.0, phirhoz[0][0], 4)
        self.assertAlmostEqual(0.0, phirhoz[0][1], 4)
        self.assertAlmostEqual(0.01, phirhoz[0][2], 4)

        phirhoz = obj.get(Transition(29, 9, 4), absorption=False, fluorescence=True)
        self.assertEqual((4, 3), phirhoz.shape)
        self.assertAlmostEqual(1.0, phirhoz[0][0], 4)
        self.assertAlmostEqual(10.0, phirhoz[0][1], 4)
        self.assertAlmostEqual(0.11, phirhoz[0][2], 4)

        phirhoz = obj.get(Transition(29, 9, 4), absorption=True, fluorescence=False)
        self.assertEqual((4, 3), phirhoz.shape)
        self.assertAlmostEqual(1.0, phirhoz[0][0], 4)
        self.assertAlmostEqual(20.0, phirhoz[0][1], 4)
        self.assertAlmostEqual(0.21, phirhoz[0][2], 4)

        phirhoz = obj.get(Transition(29, 9, 4), absorption=True, fluorescence=True)
        self.assertEqual((4, 3), phirhoz.shape)
        self.assertAlmostEqual(1.0, phirhoz[0][0], 4)
        self.assertAlmostEqual(30.0, phirhoz[0][1], 4)
        self.assertAlmostEqual(0.31, phirhoz[0][2], 4)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        group = self.hdf5file['det']

        phirhoz = group['Cu L3-M5']['gnf']
        self.assertEqual((4, 3), phirhoz.shape)
        self.assertAlmostEqual(1.0, phirhoz[0][0], 4)
        self.assertAlmostEqual(0.0, phirhoz[0][1], 4)
        self.assertAlmostEqual(0.01, phirhoz[0][2], 4)

        phirhoz = group['Cu L3-M5']['gt']
        self.assertEqual((4, 3), phirhoz.shape)
        self.assertAlmostEqual(1.0, phirhoz[0][0], 4)
        self.assertAlmostEqual(10.0, phirhoz[0][1], 4)
        self.assertAlmostEqual(0.11, phirhoz[0][2], 4)

        phirhoz = group['Cu L3-M5']['enf']
        self.assertEqual((4, 3), phirhoz.shape)
        self.assertAlmostEqual(1.0, phirhoz[0][0], 4)
        self.assertAlmostEqual(20.0, phirhoz[0][1], 4)
        self.assertAlmostEqual(0.21, phirhoz[0][2], 4)

        phirhoz = group['Cu L3-M5']['et']
        self.assertEqual((4, 3), phirhoz.shape)
        self.assertAlmostEqual(1.0, phirhoz[0][0], 4)
        self.assertAlmostEqual(30.0, phirhoz[0][1], 4)
        self.assertAlmostEqual(0.31, phirhoz[0][2], 4)

class TestPhotonRadialResultHDF5Handler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.hdf5file = h5py.File('test.h5', 'a', driver='core', backing_store=False)
        self.h = PhotonRadialResultHDF5Handler()

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

        distributions = create_photondist_dict(Transition(29, 9, 4), gnf, gt, enf, et)
        self.obj = PhotonRadialResult(distributions)

        self.group = self.h.convert(self.obj, self.hdf5file.create_group('det'))

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.hdf5file.close()

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.group))

    def testparse(self):
        obj = self.h.parse(self.group)

        radial = obj.get(Transition(29, 9, 4), absorption=False, fluorescence=False)
        self.assertEqual((4, 3), radial.shape)
        self.assertAlmostEqual(1.0, radial[0][0], 4)
        self.assertAlmostEqual(0.0, radial[0][1], 4)
        self.assertAlmostEqual(0.01, radial[0][2], 4)

        radial = obj.get(Transition(29, 9, 4), absorption=False, fluorescence=True)
        self.assertEqual((4, 3), radial.shape)
        self.assertAlmostEqual(1.0, radial[0][0], 4)
        self.assertAlmostEqual(10.0, radial[0][1], 4)
        self.assertAlmostEqual(0.11, radial[0][2], 4)

        radial = obj.get(Transition(29, 9, 4), absorption=True, fluorescence=False)
        self.assertEqual((4, 3), radial.shape)
        self.assertAlmostEqual(1.0, radial[0][0], 4)
        self.assertAlmostEqual(20.0, radial[0][1], 4)
        self.assertAlmostEqual(0.21, radial[0][2], 4)

        radial = obj.get(Transition(29, 9, 4), absorption=True, fluorescence=True)
        self.assertEqual((4, 3), radial.shape)
        self.assertAlmostEqual(1.0, radial[0][0], 4)
        self.assertAlmostEqual(30.0, radial[0][1], 4)
        self.assertAlmostEqual(0.31, radial[0][2], 4)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        group = self.hdf5file['det']

        radial = group['Cu L3-M5']['gnf']
        self.assertEqual((4, 3), radial.shape)
        self.assertAlmostEqual(1.0, radial[0][0], 4)
        self.assertAlmostEqual(0.0, radial[0][1], 4)
        self.assertAlmostEqual(0.01, radial[0][2], 4)

        radial = group['Cu L3-M5']['gt']
        self.assertEqual((4, 3), radial.shape)
        self.assertAlmostEqual(1.0, radial[0][0], 4)
        self.assertAlmostEqual(10.0, radial[0][1], 4)
        self.assertAlmostEqual(0.11, radial[0][2], 4)

        radial = group['Cu L3-M5']['enf']
        self.assertEqual((4, 3), radial.shape)
        self.assertAlmostEqual(1.0, radial[0][0], 4)
        self.assertAlmostEqual(20.0, radial[0][1], 4)
        self.assertAlmostEqual(0.21, radial[0][2], 4)

        radial = group['Cu L3-M5']['et']
        self.assertEqual((4, 3), radial.shape)
        self.assertAlmostEqual(1.0, radial[0][0], 4)
        self.assertAlmostEqual(30.0, radial[0][1], 4)
        self.assertAlmostEqual(0.31, radial[0][2], 4)

class TestTimeResultHDF5Handler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.hdf5file = h5py.File('test.h5', 'a', driver='core', backing_store=False)
        self.h = TimeResultHDF5Handler()

        self.obj = TimeResult(5.0, (1.0, 0.5))

        self.group = self.h.convert(self.obj, self.hdf5file.create_group('det'))

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.hdf5file.close()

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.group))

    def testparse(self):
        obj = self.h.parse(self.group)

        self.assertAlmostEqual(5.0, obj.simulation_time_s, 4)
        self.assertAlmostEqual(1.0, obj.simulation_speed_s[0], 4)
        self.assertAlmostEqual(0.5, obj.simulation_speed_s[1], 4)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        group = self.hdf5file['det']

        self.assertAlmostEqual(5.0, group.attrs['simulation_time_s'], 4)
        self.assertAlmostEqual(1.0, group.attrs['simulation_speed_s'][0], 4)
        self.assertAlmostEqual(0.5, group.attrs['simulation_speed_s'][1], 4)

class TestShowersStatisticsResultHDF5Handler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.hdf5file = h5py.File('test.h5', 'a', driver='core', backing_store=False)
        self.h = ShowersStatisticsResultHDF5Handler()

        self.obj = ShowersStatisticsResult(6)

        self.group = self.h.convert(self.obj, self.hdf5file.create_group('det'))

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.hdf5file.close()

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.group))

    def testparse(self):
        obj = self.h.parse(self.group)

        self.assertEqual(6, obj.showers)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        group = self.hdf5file['det']

        self.assertEqual(6, group.attrs['showers'])

class TestElectronFractionResultHDF5Handler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.hdf5file = h5py.File('test.h5', 'a', driver='core', backing_store=False)
        self.h = ElectronFractionResultHDF5Handler()

        self.obj = ElectronFractionResult((1.0, 0.1), (2.0, 0.2), (3.0, 0.3))

        self.group = self.h.convert(self.obj, self.hdf5file.create_group('det'))

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.hdf5file.close()

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.group))

    def testparse(self):
        obj = self.h.parse(self.group)

        self.assertAlmostEqual(1.0, obj.absorbed[0], 4)
        self.assertAlmostEqual(0.1, obj.absorbed[1], 4)
        self.assertAlmostEqual(2.0, obj.backscattered[0], 4)
        self.assertAlmostEqual(0.2, obj.backscattered[1], 4)
        self.assertAlmostEqual(3.0, obj.transmitted[0], 4)
        self.assertAlmostEqual(0.3, obj.transmitted[1], 4)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        group = self.hdf5file['det']

        self.assertAlmostEqual(1.0, group.attrs['absorbed'][0], 4)
        self.assertAlmostEqual(0.1, group.attrs['absorbed'][1], 4)
        self.assertAlmostEqual(2.0, group.attrs['backscattered'][0], 4)
        self.assertAlmostEqual(0.2, group.attrs['backscattered'][1], 4)
        self.assertAlmostEqual(3.0, group.attrs['transmitted'][0], 4)
        self.assertAlmostEqual(0.3, group.attrs['transmitted'][1], 4)

class TestTrajectoryResultHDF5Handler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.hdf5file = h5py.File('test.h5', 'a', driver='core', backing_store=False)
        self.h = TrajectoryResultHDF5Handler()

        interactions = np.array([[0.0, 0.0, 1.0, 20e3, -1], [1.0, 1.0, 1.0, 19e3, 2]])
        traj = Trajectory(True, ELECTRON, NO_COLLISION, EXIT_STATE_ABSORBED, interactions)
        self.obj = TrajectoryResult([traj])

        self.group = self.h.convert(self.obj, self.hdf5file.create_group('det'))

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.hdf5file.close()

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.group))

    def testparse(self):
        obj = self.h.parse(self.group)

        self.assertEqual(1, len(obj))

        trajectory = list(obj)[0]
        self.assertTrue(trajectory.is_primary())
        self.assertFalse(trajectory.is_secondary())
        self.assertIs(ELECTRON, trajectory.particle)
        self.assertIs(NO_COLLISION, trajectory.collision)
        self.assertEqual(EXIT_STATE_ABSORBED, trajectory.exit_state)
        self.assertEqual(2, len(trajectory.interactions))
        self.assertEqual(5, trajectory.interactions.shape[1])

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        group = self.hdf5file['det']

        dataset = group['trajectory0']
        self.assertTrue(dataset.attrs['primary'])
        self.assertEqual(1, dataset.attrs['particle'])
        self.assertEqual(-1, dataset.attrs['collision'])
        self.assertEqual(3, dataset.attrs['exit_state'])
        self.assertEqual(2, len(dataset))

class TestBackscatteredElectronEnergyResultHDF5Handler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.hdf5file = h5py.File('test.h5', 'a', driver='core', backing_store=False)
        self.h = BackscatteredElectronEnergyResultHDF5Handler()

        data = np.array([[0.0, 1.0, 0.1], [1.0, 2.0, 0.2], [2.0, 3.0, 0.3]])
        self.obj = BackscatteredElectronEnergyResult(data)

        self.group = self.h.convert(self.obj, self.hdf5file.create_group('det'))

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.hdf5file.close()

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.group))

    def testparse(self):
        obj = self.h.parse(self.group)

        data = obj.get_data()
        self.assertAlmostEqual(1.0, data[0][1], 4)
        self.assertAlmostEqual(0.2, data[1][2], 4)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        group = self.hdf5file['det']

        dataset = group['data']
        self.assertAlmostEqual(1.0, dataset[0][1], 4)
        self.assertAlmostEqual(0.2, dataset[1][2], 4)

class TestTransmittedElectronEnergyResultHDF5Handler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.hdf5file = h5py.File('test.h5', 'a', driver='core', backing_store=False)
        self.h = TransmittedElectronEnergyResultHDF5Handler()

        data = np.array([[0.0, 1.0, 0.1], [1.0, 2.0, 0.2], [2.0, 3.0, 0.3]])
        self.obj = TransmittedElectronEnergyResult(data)

        self.group = self.h.convert(self.obj, self.hdf5file.create_group('det'))

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.hdf5file.close()

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.group))

    def testparse(self):
        obj = self.h.parse(self.group)

        data = obj.get_data()
        self.assertAlmostEqual(1.0, data[0][1], 4)
        self.assertAlmostEqual(0.2, data[1][2], 4)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        group = self.hdf5file['det']

        dataset = group['data']
        self.assertAlmostEqual(1.0, dataset[0][1], 4)
        self.assertAlmostEqual(0.2, dataset[1][2], 4)

class TestBackscatteredElectronPolarAngularResultHDF5Handler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.hdf5file = h5py.File('test.h5', 'a', driver='core', backing_store=False)
        self.h = BackscatteredElectronPolarAngularResultHDF5Handler()

        data = np.array([[0.0, 1.0, 0.1], [1.0, 2.0, 0.2], [2.0, 3.0, 0.3]])
        self.obj = BackscatteredElectronPolarAngularResult(data)

        self.group = self.h.convert(self.obj, self.hdf5file.create_group('det'))

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.hdf5file.close()

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.group))

    def testparse(self):
        obj = self.h.parse(self.group)

        data = obj.get_data()
        self.assertAlmostEqual(1.0, data[0][1], 4)
        self.assertAlmostEqual(0.2, data[1][2], 4)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        group = self.hdf5file['det']

        dataset = group['data']
        self.assertAlmostEqual(1.0, dataset[0][1], 4)
        self.assertAlmostEqual(0.2, dataset[1][2], 4)

class TestBackscatteredElectronRadialResultHDF5Handler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.hdf5file = h5py.File('test.h5', 'a', driver='core', backing_store=False)
        self.h = BackscatteredElectronRadialResultHDF5Handler()

        data = np.array([[0.0, 1.0, 0.1], [1.0, 2.0, 0.2], [2.0, 3.0, 0.3]])
        self.obj = BackscatteredElectronRadialResult(data)

        self.group = self.h.convert(self.obj, self.hdf5file.create_group('det'))

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.hdf5file.close()

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.group))

    def testparse(self):
        obj = self.h.parse(self.group)

        data = obj.get_data()
        self.assertAlmostEqual(1.0, data[0][1], 4)
        self.assertAlmostEqual(0.2, data[1][2], 4)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        group = self.hdf5file['det']

        dataset = group['data']
        self.assertAlmostEqual(1.0, dataset[0][1], 4)
        self.assertAlmostEqual(0.2, dataset[1][2], 4)

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
