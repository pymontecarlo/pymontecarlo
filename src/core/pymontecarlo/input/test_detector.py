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

from pymontecarlo.input.detector import \
    (_DelimitedDetector, _ChannelsDetector,
     _SpatialDetector, _EnergyDetector,
     _PolarAngularDetector, _AzimuthalAngularDetector,
     PhotonSpectrumDetector, PhotonDepthDetector, PhotonRadialDetector,
     PhotonEmissionMapDetector,
     TimeDetector, ElectronFractionDetector, TrajectoryDetector,
     ShowersStatisticsDetector)
from pymontecarlo.input.xmlmapper import mapper

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

        self.assertAlmostEqual(0, self.d.azimuth_rad[0], 4)
        self.assertAlmostEqual(radians(360.0), self.d.azimuth_rad[1], 4)
        self.assertAlmostEqual(0, self.d.azimuth_deg[0], 2)
        self.assertAlmostEqual(360.0, self.d.azimuth_deg[1], 2)

        self.assertAlmostEqual(0.704001, self.d.solidangle_sr, 4)

        self.assertAlmostEqual(radians(40), self.d.takeoffangle_rad, 4)
        self.assertAlmostEqual(40, self.d.takeoffangle_deg, 2)

    def test__repr__(self):
        expected = '<_DelimitedDetector(elevation=35.0 to 45.0 deg, azimuth=0.0 to 360.0 deg)>'
        self.assertEquals(expected, repr(self.d))

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

    def testelevation_rad(self):
        self.assertRaises(ValueError, self.d.__setattr__, 'elevation_rad', (-4, 0))
        self.assertRaises(ValueError, self.d.__setattr__, 'elevation_rad', (0, 4))
        self.assertRaises(ValueError, self.d.__setattr__, 'elevation_rad', (1, 1))
        self.assertRaises(TypeError, self.d.__setattr__, 'elevation_rad', 0)

    def testazimuth_rad(self):
        self.assertRaises(ValueError, self.d.__setattr__, 'azimuth_rad', (-1, 0))
        self.assertRaises(ValueError, self.d.__setattr__, 'azimuth_rad', (0, 7))
        self.assertRaises(ValueError, self.d.__setattr__, 'azimuth_rad', (1, 1))
        self.assertRaises(TypeError, self.d.__setattr__, 'azimuth_rad', 0)

    def testfrom_xml(self):
        element = mapper.to_xml(self.d)
        d = mapper.from_xml(element)

        self.assertAlmostEqual(radians(35), d.elevation_rad[0], 4)
        self.assertAlmostEqual(radians(45), d.elevation_rad[1], 4)
        self.assertAlmostEqual(0, d.azimuth_rad[0], 4)
        self.assertAlmostEqual(radians(360.0), d.azimuth_rad[1], 4)

    def testto_xml(self):
        element = mapper.to_xml(self.d)

        subelement = list(element.find('elevation'))[0]
        self.assertAlmostEqual(radians(35), float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(45), float(subelement.get('upper')), 4)

        subelement = list(element.find('azimuth'))[0]
        self.assertAlmostEqual(0, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(360.0), float(subelement.get('upper')), 4)

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

    def testfrom_xml(self):
        element = mapper.to_xml(self.d)
        d = mapper.from_xml(element)

        self.assertEqual(10, d.channels)

    def testto_xml(self):
        element = mapper.to_xml(self.d)

        self.assertEqual(10, int(element.get('channels')))

#class Test_BoundedChannelsDetector(TestCase):
#
#    def setUp(self):
#        TestCase.setUp(self)
#
#        self.d = _BoundedChannelsDetector((10, 60))
#
#    def tearDown(self):
#        TestCase.tearDown(self)
#
#    def testskeleton(self):
#        self.assertTrue(True)
#
#    def test_set_limits(self):
#        self.assertRaises(ValueError, self.d._set_limits, (8, 56.78))
#        self.assertRaises(ValueError, self.d._set_limits, (12.34, 62))
#
#    def testchannels(self):
#        self.assertRaises(ValueError, self.d.__setattr__, 'channels', 0)
#
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
        self.assertEquals(expected, repr(self.d))

    def testxbins(self):
        self.assertRaises(ValueError, self.d.__setattr__, 'xbins', 0)

    def testybins(self):
        self.assertRaises(ValueError, self.d.__setattr__, 'ybins', 0)

    def testzbins(self):
        self.assertRaises(ValueError, self.d.__setattr__, 'zbins', 0)

    def testfrom_xml(self):
        element = mapper.to_xml(self.d)
        d = mapper.from_xml(element)

        self.assertAlmostEqual(12.34, d.xlimits_m[0], 4)
        self.assertAlmostEqual(56.78, d.xlimits_m[1], 4)
        self.assertEqual(2, d.xbins)

        self.assertAlmostEqual(21.43, d.ylimits_m[0], 4)
        self.assertAlmostEqual(65.87, d.ylimits_m[1], 4)
        self.assertEqual(3, d.ybins)

        self.assertAlmostEqual(34.12, d.zlimits_m[0], 4)
        self.assertAlmostEqual(78.56, d.zlimits_m[1], 4)
        self.assertEqual(4, d.zbins)

    def testto_xml(self):
        element = mapper.to_xml(self.d)

        subelement = list(element.find('xlimits'))[0]
        self.assertAlmostEqual(12.34, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(56.78, float(subelement.get('upper')), 4)
        self.assertEqual(2, int(element.get('xbins')))

        subelement = list(element.find('ylimits'))[0]
        self.assertAlmostEqual(21.43, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(65.87, float(subelement.get('upper')), 4)
        self.assertEqual(3, int(element.get('ybins')))

        subelement = list(element.find('zlimits'))[0]
        self.assertAlmostEqual(34.12, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(78.56, float(subelement.get('upper')), 4)
        self.assertEqual(4, int(element.get('zbins')))

class Test_EnergyDetector(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.d = _EnergyDetector((12.34, 56.78), 1000)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(12.34, self.d.limits_eV[0], 4)
        self.assertAlmostEqual(56.78, self.d.limits_eV[1], 4)
        self.assertEqual(1000, self.d.channels)

    def test__repr__(self):
        expected = '<_EnergyDetector(limits=12.34 to 56.78 eV, channels=1000)>'
        self.assertEquals(expected, repr(self.d))

    def testlimits(self):
        self.assertRaises(ValueError, setattr, self.d, 'limits_eV', (-1.0, 5.0))
        self.assertRaises(ValueError, setattr, self.d, 'limits_eV', (5.0, -1.0))

    def testfrom_xml(self):
        element = mapper.to_xml(self.d)
        d = mapper.from_xml(element)

        self.assertAlmostEqual(12.34, d.limits_eV[0], 4)
        self.assertAlmostEqual(56.78, d.limits_eV[1], 4)
        self.assertEqual(1000, d.channels)

    def testto_xml(self):
        element = mapper.to_xml(self.d)

        subelement = list(element.find('limits'))[0]
        self.assertAlmostEqual(12.34, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(56.78, float(subelement.get('upper')), 4)
        self.assertEqual(1000, int(element.get('channels')))
#
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
        expected = '<_PolarAngularDetector(limits=-1.57079632679 to 1.57079632679 rad, channels=50)>'
        self.assertEquals(expected, repr(self.d))

    def testfrom_xml(self):
        element = mapper.to_xml(self.d)
        d = mapper.from_xml(element)

        self.assertAlmostEqual(radians(-90), d.limits_rad[0], 4)
        self.assertAlmostEqual(radians(90), d.limits_rad[1], 4)
        self.assertEqual(50, d.channels)

    def testto_xml(self):
        element = mapper.to_xml(self.d)

        subelement = list(element.find('limits'))[0]
        self.assertAlmostEqual(radians(-90), float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(90), float(subelement.get('upper')), 4)
        self.assertEqual(50, int(element.get('channels')))

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
        expected = '<_AzimuthalAngularDetector(limits=0 to 6.28318530718 rad, channels=50)>'
        self.assertEquals(expected, repr(self.d))

    def testfrom_xml(self):
        element = mapper.to_xml(self.d)
        d = mapper.from_xml(element)

        self.assertAlmostEqual(radians(0), d.limits_rad[0], 4)
        self.assertAlmostEqual(radians(360), d.limits_rad[1], 4)
        self.assertEqual(50, self.d.channels)

    def testto_xml(self):
        element = mapper.to_xml(self.d)

        subelement = list(element.find('limits'))[0]
        self.assertAlmostEqual(radians(0), float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(360), float(subelement.get('upper')), 4)
        self.assertEqual(50, int(element.get('channels')))
#
class TestPhotonSpectrumDetector(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.d = PhotonSpectrumDetector((radians(35), radians(45)),
                                        (0, radians(360.0)),
                                        (12.34, 56.78), 1000)

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
        self.assertEquals(expected, repr(self.d))

    def testfrom_xml(self):
        element = mapper.to_xml(self.d)
        d = mapper.from_xml(element)

        self.assertAlmostEqual(radians(35), d.elevation_rad[0], 4)
        self.assertAlmostEqual(radians(45), d.elevation_rad[1], 4)
        self.assertAlmostEqual(0, d.azimuth_rad[0], 4)
        self.assertAlmostEqual(radians(360.0), d.azimuth_rad[1], 4)
        self.assertAlmostEqual(12.34, d.limits_eV[0], 4)
        self.assertAlmostEqual(56.78, d.limits_eV[1], 4)
        self.assertEqual(1000, d.channels)

    def testto_xml(self):
        element = mapper.to_xml(self.d)

        subelement = list(element.find('elevation'))[0]
        self.assertAlmostEqual(radians(35), float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(45), float(subelement.get('upper')), 4)

        subelement = list(element.find('azimuth'))[0]
        self.assertAlmostEqual(0, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(360.0), float(subelement.get('upper')), 4)

        subelement = list(element.find('limits'))[0]
        self.assertAlmostEqual(12.34, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(56.78, float(subelement.get('upper')), 4)

        self.assertEqual(1000, int(element.get('channels')))
#
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
        self.assertEquals(expected, repr(self.d))

    def testfrom_xml(self):
        element = mapper.to_xml(self.d)
        d = mapper.from_xml(element)

        self.assertAlmostEqual(radians(35), d.elevation_rad[0], 4)
        self.assertAlmostEqual(radians(45), d.elevation_rad[1], 4)
        self.assertAlmostEqual(0, d.azimuth_rad[0], 4)
        self.assertAlmostEqual(radians(360.0), d.azimuth_rad[1], 4)
        self.assertEqual(1000, d.channels)

    def testto_xml(self):
        element = mapper.to_xml(self.d)

        subelement = list(element.find('elevation'))[0]
        self.assertAlmostEqual(radians(35), float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(45), float(subelement.get('upper')), 4)

        subelement = list(element.find('azimuth'))[0]
        self.assertAlmostEqual(0, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(360.0), float(subelement.get('upper')), 4)

        self.assertEqual(1000, int(element.get('channels')))

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
        self.assertEquals(expected, repr(self.d))

    def testfrom_xml(self):
        element = mapper.to_xml(self.d)
        d = mapper.from_xml(element)

        self.assertAlmostEqual(radians(35), d.elevation_rad[0], 4)
        self.assertAlmostEqual(radians(45), d.elevation_rad[1], 4)
        self.assertAlmostEqual(0, d.azimuth_rad[0], 4)
        self.assertAlmostEqual(radians(360.0), d.azimuth_rad[1], 4)
        self.assertEqual(1000, d.channels)

    def testto_xml(self):
        element = mapper.to_xml(self.d)

        subelement = list(element.find('elevation'))[0]
        self.assertAlmostEqual(radians(35), float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(45), float(subelement.get('upper')), 4)

        subelement = list(element.find('azimuth'))[0]
        self.assertAlmostEqual(0, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(360.0), float(subelement.get('upper')), 4)

        self.assertEqual(1000, int(element.get('channels')))

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
        self.assertEquals(expected, repr(self.d))

    def testfrom_xml(self):
        element = mapper.to_xml(self.d)
        d = mapper.from_xml(element)

        self.assertAlmostEqual(radians(35), d.elevation_rad[0], 4)
        self.assertAlmostEqual(radians(45), d.elevation_rad[1], 4)
        self.assertAlmostEqual(0, d.azimuth_rad[0], 4)
        self.assertAlmostEqual(radians(360.0), d.azimuth_rad[1], 4)
        self.assertEqual(5, d.xbins)
        self.assertEqual(6, d.ybins)
        self.assertEqual(7, d.zbins)

    def testto_xml(self):
        element = mapper.to_xml(self.d)

        subelement = list(element.find('elevation'))[0]
        self.assertAlmostEqual(radians(35), float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(45), float(subelement.get('upper')), 4)

        subelement = list(element.find('azimuth'))[0]
        self.assertAlmostEqual(0, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(360.0), float(subelement.get('upper')), 4)

        self.assertEqual(5, int(element.get('xbins')))
        self.assertEqual(6, int(element.get('ybins')))
        self.assertEqual(7, int(element.get('zbins')))
#
class TestTimeDetector(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.d = TimeDetector()

    def tearDown(self):
        TestCase.tearDown(self)

    def testfrom_xml(self):
        element = mapper.to_xml(self.d)
        mapper.from_xml(element)

    def testto_xml(self):
        mapper.to_xml(self.d)

class TestElectronFractionDetector(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.d = ElectronFractionDetector()

    def tearDown(self):
        TestCase.tearDown(self)

    def testfrom_xml(self):
        element = mapper.to_xml(self.d)
        mapper.from_xml(element)

    def testto_xml(self):
        mapper.to_xml(self.d)

class TestShowersStatisticsDetector(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.d = ShowersStatisticsDetector()

    def tearDown(self):
        TestCase.tearDown(self)

    def testfrom_xml(self):
        element = mapper.to_xml(self.d)
        mapper.from_xml(element)

    def testto_xml(self):
        mapper.to_xml(self.d)

class TestTrajectoryDetector(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.d = TrajectoryDetector(False)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertFalse(self.d.secondary)

    def testfrom_xml(self):
        element = mapper.to_xml(self.d)
        d = mapper.from_xml(element)

        self.assertFalse(d.secondary)

    def testto_xml(self):
        element = mapper.to_xml(self.d)

        self.assertEqual('false', element.get('secondary'))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
