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
from pymontecarlo.util.relaxation_data import Transition
from pymontecarlo.input.detector import \
    (_DelimitedDetector, _ChannelsDetector, _SpatialDetector,
     _TransitionDetector, _EnergyDetector, _PolarAngularDetector,
     _AzimuthalAngularDetector, PhotonSpectrumDetector, PhiRhoZDetector)

# Globals and constants variables.

class Test_DelimitedDetector(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.d = _DelimitedDetector((radians(35), radians(45)),
                                    (0, radians(360.0)))

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(radians(35), self.d.elevation[0], 4)
        self.assertAlmostEqual(radians(45), self.d.elevation[1], 4)
        self.assertAlmostEqual(0, self.d.azimuth[0], 4)
        self.assertAlmostEqual(radians(360.0), self.d.azimuth[1], 4)
        self.assertAlmostEqual(0.70400115, self.d.solid_angle, 4)

    def testfrom_xml(self):
        element = self.d.to_xml()
        d = _DelimitedDetector.from_xml(element)

        self.assertAlmostEqual(radians(35), d.elevation[0], 4)
        self.assertAlmostEqual(radians(45), d.elevation[1], 4)
        self.assertAlmostEqual(0, d.azimuth[0], 4)
        self.assertAlmostEqual(radians(360.0), d.azimuth[1], 4)

    def testelevation(self):
        self.assertRaises(ValueError, self.d.__setattr__, 'elevation', (-4, 0))
        self.assertRaises(ValueError, self.d.__setattr__, 'elevation', (0, 4))
        self.assertRaises(TypeError, self.d.__setattr__, 'elevation', 0)

    def testazimuth(self):
        self.assertRaises(ValueError, self.d.__setattr__, 'azimuth', (-1, 0))
        self.assertRaises(ValueError, self.d.__setattr__, 'azimuth', (0, 7))
        self.assertRaises(TypeError, self.d.__setattr__, 'azimuth', 0)

    def testto_xml(self):
        element = self.d.to_xml()

        self.assertAlmostEqual(radians(35), float(element.get('elevation_min')), 4)
        self.assertAlmostEqual(radians(45), float(element.get('elevation_max')), 4)
        self.assertAlmostEqual(0, float(element.get('azimuth_min')), 4)
        self.assertAlmostEqual(radians(360.0), float(element.get('azimuth_max')), 4)

class Test_ChannelsDetector(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.d = _ChannelsDetector((12.34, 56.78), 1000, (10, 60))

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(12.34, self.d.limits[0], 4)
        self.assertAlmostEqual(56.78, self.d.limits[1], 4)
        self.assertEqual(1000, self.d.channels)

    def testfrom_xml(self):
        element = self.d.to_xml()
        d = _ChannelsDetector.from_xml(element)

        self.assertAlmostEqual(12.34, d.limits[0], 4)
        self.assertAlmostEqual(56.78, d.limits[1], 4)
        self.assertEqual(1000, d.channels)

    def testlimits(self):
        self.assertRaises(ValueError, self.d.__setattr__, 'limits', (8, 56.78))
        self.assertRaises(ValueError, self.d.__setattr__, 'limits', (12.34, 62))

    def testchannels(self):
        self.assertRaises(ValueError, self.d.__setattr__, 'channels', 0)

    def testto_xml(self):
        element = self.d.to_xml()

        self.assertAlmostEqual(12.34, float(element.get('limit_min')), 4)
        self.assertAlmostEqual(56.78, float(element.get('limit_max')), 4)
        self.assertEqual(1000, int(element.get('channels')))

class Test_SpatialDetector(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.d = _SpatialDetector((12.34, 56.78), 2,
                                  (21.43, 65.87), 3,
                                  (34.12, 78.56), 4,
                                  (10, 60), (20, 70), (30, 80))

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(12.34, self.d.xlimits[0], 4)
        self.assertAlmostEqual(56.78, self.d.xlimits[1], 4)
        self.assertEqual(2, self.d.xbins)

        self.assertAlmostEqual(21.43, self.d.ylimits[0], 4)
        self.assertAlmostEqual(65.87, self.d.ylimits[1], 4)
        self.assertEqual(3, self.d.ybins)

        self.assertAlmostEqual(34.12, self.d.zlimits[0], 4)
        self.assertAlmostEqual(78.56, self.d.zlimits[1], 4)
        self.assertEqual(4, self.d.zbins)

    def testfrom_xml(self):
        element = self.d.to_xml()
        d = _SpatialDetector.from_xml(element)

        self.assertAlmostEqual(12.34, d.xlimits[0], 4)
        self.assertAlmostEqual(56.78, d.xlimits[1], 4)
        self.assertEqual(2, d.xbins)

        self.assertAlmostEqual(21.43, d.ylimits[0], 4)
        self.assertAlmostEqual(65.87, d.ylimits[1], 4)
        self.assertEqual(3, d.ybins)

        self.assertAlmostEqual(34.12, d.zlimits[0], 4)
        self.assertAlmostEqual(78.56, d.zlimits[1], 4)
        self.assertEqual(4, d.zbins)

    def testxlimits(self):
        self.assertRaises(ValueError, self.d.__setattr__, 'xlimits', (9, 56.78))
        self.assertRaises(ValueError, self.d.__setattr__, 'xlimits', (12.34, 61))

    def testylimits(self):
        self.assertRaises(ValueError, self.d.__setattr__, 'ylimits', (19, 65.87))
        self.assertRaises(ValueError, self.d.__setattr__, 'ylimits', (21.34, 71))

    def testzlimits(self):
        self.assertRaises(ValueError, self.d.__setattr__, 'zlimits', (29, 78.56))
        self.assertRaises(ValueError, self.d.__setattr__, 'zlimits', (34.12, 81))

    def testxbins(self):
        self.assertRaises(ValueError, self.d.__setattr__, 'xbins', 0)

    def testybins(self):
        self.assertRaises(ValueError, self.d.__setattr__, 'ybins', 0)

    def testzbins(self):
        self.assertRaises(ValueError, self.d.__setattr__, 'zbins', 0)

    def testto_xml(self):
        element = self.d.to_xml()

        self.assertAlmostEqual(12.34, float(element.get('xlimit_min')), 4)
        self.assertAlmostEqual(56.78, float(element.get('xlimit_max')), 4)
        self.assertEqual(2, int(element.get('xbins')))

        self.assertAlmostEqual(21.43, float(element.get('ylimit_min')), 4)
        self.assertAlmostEqual(65.87, float(element.get('ylimit_max')), 4)
        self.assertEqual(3, int(element.get('ybins')))

        self.assertAlmostEqual(34.12, float(element.get('zlimit_min')), 4)
        self.assertAlmostEqual(78.56, float(element.get('zlimit_max')), 4)
        self.assertEqual(4, int(element.get('zbins')))

class Test_TransitionDetector(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        transition = Transition(29, siegbahn='Ka1')
        self.d = _TransitionDetector(transition)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('Cu Ka1', str(self.d.transition))

    def testfrom_xml(self):
        element = self.d.to_xml()
        d = _TransitionDetector.from_xml(element)

        self.assertEqual('Cu Ka1', str(d.transition))

    def testto_xml(self):
        element = self.d.to_xml()

        child = list(element.find('transition'))[0]
        self.assertEqual(29, int(child.get('z')))
        self.assertEqual(4, int(child.get('src')))
        self.assertEqual(1, int(child.get('dest')))

class Test_EnergyDetector(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.d = _EnergyDetector((12.34, 56.78), 1000)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(12.34, self.d.limits[0], 4)
        self.assertAlmostEqual(56.78, self.d.limits[1], 4)
        self.assertEqual(1000, self.d.channels)
        self.assertAlmostEqual(0.0, self.d._extremums[0], 4)
        self.assertEqual(float('inf'), self.d._extremums[1], 4)

    def testfrom_xml(self):
        element = self.d.to_xml()
        d = _EnergyDetector.from_xml(element)

        self.assertAlmostEqual(12.34, d.limits[0], 4)
        self.assertAlmostEqual(56.78, d.limits[1], 4)
        self.assertEqual(1000, d.channels)
        self.assertAlmostEqual(0.0, d._extremums[0], 4)
        self.assertEqual(float('inf'), d._extremums[1], 4)

    def testto_xml(self):
        element = self.d.to_xml()

        self.assertAlmostEqual(12.34, float(element.get('limit_min')), 4)
        self.assertAlmostEqual(56.78, float(element.get('limit_max')), 4)
        self.assertEqual(1000, int(element.get('channels')))

class Test_PolarAngularDetector(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.d = _PolarAngularDetector(50)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(radians(-90), self.d.limits[0], 4)
        self.assertAlmostEqual(radians(90), self.d.limits[1], 4)
        self.assertEqual(50, self.d.channels)
        self.assertAlmostEqual(radians(-90), self.d._extremums[0], 4)
        self.assertAlmostEqual(radians(90), self.d._extremums[1], 4)

    def testfrom_xml(self):
        element = self.d.to_xml()
        d = _PolarAngularDetector.from_xml(element)

        self.assertAlmostEqual(radians(-90), d.limits[0], 4)
        self.assertAlmostEqual(radians(90), d.limits[1], 4)
        self.assertEqual(50, d.channels)
        self.assertAlmostEqual(radians(-90), d._extremums[0], 4)
        self.assertAlmostEqual(radians(90), d._extremums[1], 4)

    def testto_xml(self):
        element = self.d.to_xml()

        self.assertAlmostEqual(radians(-90), float(element.get('limit_min')), 4)
        self.assertAlmostEqual(radians(90), float(element.get('limit_max')), 4)
        self.assertEqual(50, int(element.get('channels')))

class Test_AzimuthalAngularDetector(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.d = _AzimuthalAngularDetector(50)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(radians(0), self.d.limits[0], 4)
        self.assertAlmostEqual(radians(360), self.d.limits[1], 4)
        self.assertEqual(50, self.d.channels)
        self.assertAlmostEqual(radians(0), self.d._extremums[0], 4)
        self.assertAlmostEqual(radians(360), self.d._extremums[1], 4)

    def testfrom_xml(self):
        element = self.d.to_xml()
        d = _AzimuthalAngularDetector.from_xml(element)

        self.assertAlmostEqual(radians(0), d.limits[0], 4)
        self.assertAlmostEqual(radians(360), d.limits[1], 4)
        self.assertEqual(50, self.d.channels)
        self.assertAlmostEqual(radians(0), d._extremums[0], 4)
        self.assertAlmostEqual(radians(360), d._extremums[1], 4)

    def testto_xml(self):
        element = self.d.to_xml()

        self.assertAlmostEqual(radians(0), float(element.get('limit_min')), 4)
        self.assertAlmostEqual(radians(360), float(element.get('limit_max')), 4)
        self.assertEqual(50, int(element.get('channels')))

class TestPhotonSpectrumDetector(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.d = PhotonSpectrumDetector((radians(35), radians(45)),
                                        (0, radians(360.0)),
                                        (12.34, 56.78), 1000)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(radians(35), self.d.elevation[0], 4)
        self.assertAlmostEqual(radians(45), self.d.elevation[1], 4)
        self.assertAlmostEqual(0, self.d.azimuth[0], 4)
        self.assertAlmostEqual(radians(360.0), self.d.azimuth[1], 4)
        self.assertAlmostEqual(12.34, self.d.limits[0], 4)
        self.assertAlmostEqual(56.78, self.d.limits[1], 4)
        self.assertEqual(1000, self.d.channels)

    def testfrom_xml(self):
        element = self.d.to_xml()
        d = PhotonSpectrumDetector.from_xml(element)

        self.assertAlmostEqual(radians(35), d.elevation[0], 4)
        self.assertAlmostEqual(radians(45), d.elevation[1], 4)
        self.assertAlmostEqual(0, d.azimuth[0], 4)
        self.assertAlmostEqual(radians(360.0), d.azimuth[1], 4)
        self.assertAlmostEqual(12.34, d.limits[0], 4)
        self.assertAlmostEqual(56.78, d.limits[1], 4)
        self.assertEqual(1000, d.channels)

    def testto_xml(self):
        element = self.d.to_xml()

        self.assertEqual("PhotonSpectrumDetector", element.tag)

        self.assertAlmostEqual(radians(35), float(element.get('elevation_min')), 4)
        self.assertAlmostEqual(radians(45), float(element.get('elevation_max')), 4)
        self.assertAlmostEqual(0, float(element.get('azimuth_min')), 4)
        self.assertAlmostEqual(radians(360.0), float(element.get('azimuth_max')), 4)
        self.assertAlmostEqual(12.34, float(element.get('limit_min')), 4)
        self.assertAlmostEqual(56.78, float(element.get('limit_max')), 4)
        self.assertEqual(1000, int(element.get('channels')))

class TestPhiRhoZDetector(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        transition = Transition(29, siegbahn='Ka1')
        self.d = PhiRhoZDetector((-12.34, -56.78), 1000, transition)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(-56.78, self.d.limits[0], 4)
        self.assertAlmostEqual(-12.34, self.d.limits[1], 4)
        self.assertEqual(1000, self.d.channels)
        self.assertEqual('Cu Ka1', str(self.d.transition))

    def testfrom_xml(self):
        element = self.d.to_xml()
        d = PhiRhoZDetector.from_xml(element)

        self.assertAlmostEqual(-56.78, d.limits[0], 4)
        self.assertAlmostEqual(-12.34, d.limits[1], 4)
        self.assertEqual(1000, d.channels)
        self.assertEqual('Cu Ka1', str(d.transition))

    def testto_xml(self):
        element = self.d.to_xml()

        self.assertEqual("PhiRhoZDetector", element.tag)

        self.assertAlmostEqual(-56.78, float(element.get('limit_min')), 4)
        self.assertAlmostEqual(-12.34, float(element.get('limit_max')), 4)
        self.assertEqual(1000, int(element.get('channels')))

        child = list(element.find('transition'))[0]
        self.assertEqual(29, int(child.get('z')))
        self.assertEqual(4, int(child.get('src')))
        self.assertEqual(1, int(child.get('dest')))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
