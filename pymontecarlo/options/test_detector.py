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
from math import radians

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.options.detector import \
    (_DelimitedDetector, _ChannelsDetector, _EnergyDetector, _SpatialDetector,
     _PolarAngularDetector, _AzimuthalAngularDetector,
     PhotonSpectrumDetector, PhotonDepthDetector, PhiZDetector, 
     PhotonRadialDetector, PhotonEmissionMapDetector,
    TimeDetector, ElectronFractionDetector, TrajectoryDetector,
    ShowersStatisticsDetector)

# Globals and constants variables.

class Test_DelimitedDetector(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.d = _DelimitedDetector((radians(35), radians(45)),
                                    (0, radians(360.0)))

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(radians(35), self.d.elevation_rad[0], 4)
        self.assertAlmostEqual(radians(45), self.d.elevation_rad[1], 4)
        self.assertAlmostEqual(35, self.d.elevation_deg[0], 2)
        self.assertAlmostEqual(45, self.d.elevation_deg[1], 2)
        self.assertAlmostEqual(radians(35), self.d.elevation_rad.lower, 4)
        self.assertAlmostEqual(radians(45), self.d.elevation_rad.upper, 4)
        self.assertAlmostEqual(35, self.d.elevation_deg.lower, 2)
        self.assertAlmostEqual(45, self.d.elevation_deg.upper, 2)

        self.assertAlmostEqual(0, self.d.azimuth_rad[0], 4)
        self.assertAlmostEqual(radians(360.0), self.d.azimuth_rad[1], 4)
        self.assertAlmostEqual(0, self.d.azimuth_deg[0], 2)
        self.assertAlmostEqual(360.0, self.d.azimuth_deg[1], 2)
        self.assertAlmostEqual(0, self.d.azimuth_rad.lower, 4)
        self.assertAlmostEqual(radians(360.0), self.d.azimuth_rad.upper, 4)
        self.assertAlmostEqual(0, self.d.azimuth_deg.lower, 2)
        self.assertAlmostEqual(360.0, self.d.azimuth_deg.upper, 2)

        self.assertAlmostEqual(0.704001, self.d.solidangle_sr, 4)

        self.assertAlmostEqual(radians(40), self.d.takeoffangle_rad, 4)
        self.assertAlmostEqual(40, self.d.takeoffangle_deg, 2)

    def test__repr__(self):
        expected = '<_DelimitedDetector(elevation=35.0 to 45.0 deg, azimuth=0.0 to 360.0 deg)>'
        self.assertEqual(expected, repr(self.d))

    def testannular(self):
        det = _DelimitedDetector.annular(radians(40), radians(5))

        self.assertAlmostEqual(radians(35), det.elevation_rad[0], 4)
        self.assertAlmostEqual(radians(45), det.elevation_rad[1], 4)
        self.assertAlmostEqual(35, det.elevation_deg[0], 2)
        self.assertAlmostEqual(45, det.elevation_deg[1], 2)

        self.assertAlmostEqual(0, det.azimuth_rad[0], 4)
        self.assertAlmostEqual(radians(360.0), det.azimuth_rad[1], 4)
        self.assertAlmostEqual(0, det.azimuth_deg[0], 2)
        self.assertAlmostEqual(360.0, det.azimuth_deg[1], 2)

    def testannular2(self):
        det = _DelimitedDetector.annular(radians(40), [radians(5), radians(1)])

        self.assertAlmostEqual(radians(35), det.elevation_rad[0].lower, 4)
        self.assertAlmostEqual(radians(45), det.elevation_rad[0].upper, 4)
        self.assertAlmostEqual(radians(39), det.elevation_rad[1].lower, 4)
        self.assertAlmostEqual(radians(41), det.elevation_rad[1].upper, 4)

        self.assertAlmostEqual(0, det.azimuth_rad[0], 4)
        self.assertAlmostEqual(radians(360.0), det.azimuth_rad[1], 4)
        self.assertAlmostEqual(0, det.azimuth_deg[0], 2)
        self.assertAlmostEqual(360.0, det.azimuth_deg[1], 2)

    def testelevation_rad(self):
        self.assertRaises(ValueError, self.d.__setattr__, 'elevation_rad', (-4, 0))
        self.assertRaises(ValueError, self.d.__setattr__, 'elevation_rad', (0, 4))
        self.assertRaises(ValueError, self.d.__setattr__, 'elevation_rad', (1, 1))
        self.assertRaises(ValueError, self.d.__setattr__, 'elevation_rad', 0)

    def testazimuth_rad(self):
        self.assertRaises(ValueError, self.d.__setattr__, 'azimuth_rad', (-1, 0))
        self.assertRaises(ValueError, self.d.__setattr__, 'azimuth_rad', (0, 7))
        self.assertRaises(ValueError, self.d.__setattr__, 'azimuth_rad', (1, 1))
        self.assertRaises(ValueError, self.d.__setattr__, 'azimuth_rad', 0)

    def testsolidangle_sr(self):
        det = _DelimitedDetector.annular(radians(40), [radians(5), radians(1)])

        solidangles = det.solidangle_sr

        self.assertEqual(2, len(solidangles))
        self.assertAlmostEqual(0.704001, solidangles[0], 4)
        self.assertAlmostEqual(0.140972, solidangles[1], 4)

    def testtakeoffangle(self):
        det = _DelimitedDetector.annular([radians(40), radians(41)], radians(5))

        self.assertAlmostEqual(radians(40), det.takeoffangle_rad[0], 4)
        self.assertAlmostEqual(40, det.takeoffangle_deg[0], 2)
        self.assertAlmostEqual(radians(41), det.takeoffangle_rad[1], 4)
        self.assertAlmostEqual(41, det.takeoffangle_deg[1], 2)

class Test_ChannelsDetector(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.d = _ChannelsDetector(10)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(10, self.d.channels)

    def testchannels(self):
        self.assertRaises(ValueError, self.d.__setattr__, 'channels', 0)

class Test_SpatialDetector(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.d = _SpatialDetector((12.34, 56.78), 2,
                                  (21.43, 65.87), 3,
                                  (34.12, 78.56), 4)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(12.34, self.d.xlimits_m[0], 4)
        self.assertAlmostEqual(56.78, self.d.xlimits_m[1], 4)
        self.assertAlmostEqual(12.34, self.d.xlimits_m.lower, 4)
        self.assertAlmostEqual(56.78, self.d.xlimits_m.upper, 4)
        self.assertEqual(2, self.d.xbins)

        self.assertAlmostEqual(21.43, self.d.ylimits_m[0], 4)
        self.assertAlmostEqual(65.87, self.d.ylimits_m[1], 4)
        self.assertEqual(3, self.d.ybins)

        self.assertAlmostEqual(34.12, self.d.zlimits_m[0], 4)
        self.assertAlmostEqual(78.56, self.d.zlimits_m[1], 4)
        self.assertEqual(4, self.d.zbins)

    def test__repr__(self):
        expected = '<_SpatialDetector(x=12.34 to 56.78 m (2), y=21.43 to 65.87 m (3), z=34.12 to 78.56 m (4))>'
        self.assertEqual(expected, repr(self.d))

    def testxbins(self):
        self.assertRaises(ValueError, self.d.__setattr__, 'xbins', 0)

    def testybins(self):
        self.assertRaises(ValueError, self.d.__setattr__, 'ybins', 0)

    def testzbins(self):
        self.assertRaises(ValueError, self.d.__setattr__, 'zbins', 0)

class Test_EnergyDetector(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.d = _EnergyDetector(1000, (12.34, 56.78))

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(12.34, self.d.limits_eV[0], 4)
        self.assertAlmostEqual(56.78, self.d.limits_eV[1], 4)
        self.assertEqual(1000, self.d.channels)

    def test__repr__(self):
        expected = '<_EnergyDetector(limits=12.34 to 56.78 eV, channels=1000)>'
        self.assertEqual(expected, repr(self.d))

    def testlimits(self):
        self.assertRaises(ValueError, setattr, self.d, 'limits_eV', (-1.0, 5.0))
        self.assertRaises(ValueError, setattr, self.d, 'limits_eV', (5.0, -1.0))

class Test_PolarAngularDetector(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.d = _PolarAngularDetector(50)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(radians(-90), self.d.limits_rad[0], 4)
        self.assertAlmostEqual(radians(90), self.d.limits_rad[1], 4)
        self.assertEqual(50, self.d.channels)

    def test__repr__(self):
        self.assertTrue(repr(self.d).startswith('<_PolarAngularDetector('))

class Test_AzimuthalAngularDetector(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.d = _AzimuthalAngularDetector(50)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(radians(0), self.d.limits_rad[0], 4)
        self.assertAlmostEqual(radians(360), self.d.limits_rad[1], 4)
        self.assertEqual(50, self.d.channels)

    def test__repr__(self):
        self.assertTrue(repr(self.d).startswith('<_AzimuthalAngularDetector('))

class TestPhotonSpectrumDetector(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.d = PhotonSpectrumDetector((radians(35), radians(45)),
                                        (0, radians(360.0)),
                                        1000, (12.34, 56.78))

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(radians(35), self.d.elevation_rad[0], 4)
        self.assertAlmostEqual(radians(45), self.d.elevation_rad[1], 4)
        self.assertAlmostEqual(0, self.d.azimuth_rad[0], 4)
        self.assertAlmostEqual(radians(360.0), self.d.azimuth_rad[1], 4)
        self.assertAlmostEqual(12.34, self.d.limits_eV[0], 4)
        self.assertAlmostEqual(56.78, self.d.limits_eV[1], 4)
        self.assertEqual(1000, self.d.channels)

    def test__repr__(self):
        expected = '<PhotonSpectrumDetector(elevation=35.0 to 45.0 deg, azimuth=0.0 to 360.0 deg, limits=12.34 to 56.78 eV, channels=1000)>'
        self.assertEqual(expected, repr(self.d))

class TestPhotonDepthDetector(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.d = PhotonDepthDetector((radians(35), radians(45)),
                                     (0, radians(360.0)), 1000)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(radians(35), self.d.elevation_rad[0], 4)
        self.assertAlmostEqual(radians(45), self.d.elevation_rad[1], 4)
        self.assertAlmostEqual(0, self.d.azimuth_rad[0], 4)
        self.assertAlmostEqual(radians(360.0), self.d.azimuth_rad[1], 4)
        self.assertEqual(1000, self.d.channels)

    def test__repr__(self):
        expected = '<PhotonDepthDetector(elevation=35.0 to 45.0 deg, azimuth=0.0 to 360.0 deg, channels=1000)>'
        self.assertEqual(expected, repr(self.d))

class TestPhiZDetector(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.d = PhiZDetector((radians(35), radians(45)),
                                     (0, radians(360.0)), 1000)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(radians(35), self.d.elevation_rad[0], 4)
        self.assertAlmostEqual(radians(45), self.d.elevation_rad[1], 4)
        self.assertAlmostEqual(0, self.d.azimuth_rad[0], 4)
        self.assertAlmostEqual(radians(360.0), self.d.azimuth_rad[1], 4)
        self.assertEqual(1000, self.d.channels)

    def test__repr__(self):
        expected = '<PhiZDetector(elevation=35.0 to 45.0 deg, azimuth=0.0 to 360.0 deg, channels=1000)>'
        self.assertEqual(expected, repr(self.d))

class TestPhotonRadialDetector(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.d = PhotonRadialDetector((radians(35), radians(45)),
                                      (0, radians(360.0)), 1000)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(radians(35), self.d.elevation_rad[0], 4)
        self.assertAlmostEqual(radians(45), self.d.elevation_rad[1], 4)
        self.assertAlmostEqual(0, self.d.azimuth_rad[0], 4)
        self.assertAlmostEqual(radians(360.0), self.d.azimuth_rad[1], 4)
        self.assertEqual(1000, self.d.channels)

    def test__repr__(self):
        expected = '<PhotonRadialDetector(elevation=35.0 to 45.0 deg, azimuth=0.0 to 360.0 deg, channels=1000)>'
        self.assertEqual(expected, repr(self.d))

class TestPhotonEmissionMapDetector(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.d = PhotonEmissionMapDetector((radians(35), radians(45)),
                                           (0, radians(360.0)), 5, 6, 7)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(radians(35), self.d.elevation_rad[0], 4)
        self.assertAlmostEqual(radians(45), self.d.elevation_rad[1], 4)
        self.assertAlmostEqual(0, self.d.azimuth_rad[0], 4)
        self.assertAlmostEqual(radians(360.0), self.d.azimuth_rad[1], 4)
        self.assertEqual(5, self.d.xbins)
        self.assertEqual(6, self.d.ybins)
        self.assertEqual(7, self.d.zbins)

    def test__repr__(self):
        expected = '<PhotonEmissionMapDetector(elevation=35.0 to 45.0 deg, azimuth=0.0 to 360.0 deg, bins=(5, 6, 7))>'
        self.assertEqual(expected, repr(self.d))

class TestTimeDetector(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.d = TimeDetector()

    def tearDown(self):
        TestCase.tearDown(self)

class TestElectronFractionDetector(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.d = ElectronFractionDetector()

    def tearDown(self):
        TestCase.tearDown(self)

class TestShowersStatisticsDetector(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.d = ShowersStatisticsDetector()

    def tearDown(self):
        TestCase.tearDown(self)

class TestTrajectoryDetector(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.d = TrajectoryDetector(False)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertFalse(self.d.secondary)

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
