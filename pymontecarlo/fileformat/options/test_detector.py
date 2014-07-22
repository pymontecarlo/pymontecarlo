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
from io import BytesIO
import xml.etree.ElementTree as etree
from math import radians

# Third party modules.
from pyxray.transition import Transition

# Local modules.
from pymontecarlo.fileformat.options.detector import \
    (_DelimitedDetectorXMLHandler, _ChannelsDetectorXMLHandler,
     _SpatialDetectorXMLHandler, _EnergyDetectorXMLHandler,
     _PolarAngularDetectorXMLHandler, _AzimuthalAngularDetectorXMLHandler,
     _TransitionsDetectorXMLHandler,
     BackscatteredElectronEnergyDetectorXMLHandler, TransmittedElectronEnergyDetectorXMLHandler,
     BackscatteredElectronPolarAngularDetectorXMLHandler, TransmittedElectronPolarAngularDetectorXMLHandler,
     BackscatteredElectronAzimuthalAngularDetectorXMLHandler, TransmittedElectronAzimuthalAngularDetectorXMLHandler,
     BackscatteredElectronRadialDetectorXMLHandler,
     PhotonSpectrumDetectorXMLHandler, PhotonDepthDetectorXMLHandler,
     PhiZDetectorXMLHandler, PhotonRadialDetectorXMLHandler,
     PhotonEmissionMapDetectorXMLHandler, PhotonIntensityDetectorXMLHandler,
     TimeDetectorXMLHandler, ElectronFractionDetectorXMLHandler,
     ShowersStatisticsDetectorXMLHandler, TrajectoryDetectorXMLHandler)
from pymontecarlo.options.detector import \
    (_DelimitedDetector, _ChannelsDetector, _SpatialDetector, _EnergyDetector,
     _PolarAngularDetector, _AzimuthalAngularDetector, _TransitionsDetector,
     BackscatteredElectronEnergyDetector, TransmittedElectronEnergyDetector,
     BackscatteredElectronPolarAngularDetector, TransmittedElectronPolarAngularDetector,
     BackscatteredElectronAzimuthalAngularDetector, TransmittedElectronAzimuthalAngularDetector,
     BackscatteredElectronRadialDetector,
     PhotonSpectrumDetector, PhotonDepthDetector, PhiZDetector,
     PhotonRadialDetector, PhotonEmissionMapDetector, PhotonIntensityDetector,
     TimeDetector, ElectronFractionDetector, ShowersStatisticsDetector,
     TrajectoryDetector)

# Globals and constants variables.

class Test_DelimitedDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = _DelimitedDetectorXMLHandler()

        self.obj = _DelimitedDetector((radians(35), radians(45)),
                                      (0, radians(360.0)))

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:_delimitedDetector xmlns:mc="http://pymontecarlo.sf.net"><elevation lower="0.6108652381980153" upper="0.7853981633974483" /><azimuth lower="0.0" upper="6.283185307179586" /></mc:_delimitedDetector>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertAlmostEqual(radians(35), obj.elevation_rad[0], 4)
        self.assertAlmostEqual(radians(45), obj.elevation_rad[1], 4)
        self.assertAlmostEqual(0, obj.azimuth_rad[0], 4)
        self.assertAlmostEqual(radians(360.0), obj.azimuth_rad[1], 4)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        subelement = element.find('elevation')
        self.assertAlmostEqual(radians(35), float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(45), float(subelement.get('upper')), 4)

        subelement = element.find('azimuth')
        self.assertAlmostEqual(0, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(360.0), float(subelement.get('upper')), 4)

class Test_ChannelsDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = _ChannelsDetectorXMLHandler()

        self.obj = _ChannelsDetector(10)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:_channelsDetector xmlns:mc="http://pymontecarlo.sf.net"><channels>10</channels></mc:_channelsDetector>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertEqual(10, obj.channels)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        subelement = element.find('channels')
        self.assertEqual(10, int(subelement.text))

class Test_SpatialDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = _SpatialDetectorXMLHandler()

        self.obj = _SpatialDetector((12.34, 56.78), 2,
                                    (21.43, 65.87), 3,
                                    (34.12, 78.56), 4)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:_spatialDetector xmlns:mc="http://pymontecarlo.sf.net"><xlimits lower="12.34" upper="56.78" /><xbins>2</xbins><ylimits lower="21.43" upper="65.87" /><ybins>3</ybins><zlimits lower="34.12" upper="78.56" /><zbins>4</zbins></mc:_spatialDetector>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertAlmostEqual(12.34, obj.xlimits_m[0], 4)
        self.assertAlmostEqual(56.78, obj.xlimits_m[1], 4)
        self.assertEqual(2, obj.xbins)

        self.assertAlmostEqual(21.43, obj.ylimits_m[0], 4)
        self.assertAlmostEqual(65.87, obj.ylimits_m[1], 4)
        self.assertEqual(3, obj.ybins)

        self.assertAlmostEqual(34.12, obj.zlimits_m[0], 4)
        self.assertAlmostEqual(78.56, obj.zlimits_m[1], 4)
        self.assertEqual(4, obj.zbins)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        subelement = element.find('xlimits')
        self.assertAlmostEqual(12.34, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(56.78, float(subelement.get('upper')), 4)

        subelement = element.find('xbins')
        self.assertEqual(2, int(subelement.text))

        subelement = element.find('ylimits')
        self.assertAlmostEqual(21.43, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(65.87, float(subelement.get('upper')), 4)

        subelement = element.find('ybins')
        self.assertEqual(3, int(subelement.text))

        subelement = element.find('zlimits')
        self.assertAlmostEqual(34.12, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(78.56, float(subelement.get('upper')), 4)

        subelement = element.find('zbins')
        self.assertEqual(4, int(subelement.text))

class Test_EnergyDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = _EnergyDetectorXMLHandler()

        self.obj = _EnergyDetector(1000, (12.34, 56.78))

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:_energyDetector xmlns:mc="http://pymontecarlo.sf.net"><channels>1000</channels><limits lower="12.34" upper="56.78" /></mc:_energyDetector>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertAlmostEqual(12.34, obj.limits_eV[0], 4)
        self.assertAlmostEqual(56.78, obj.limits_eV[1], 4)
        self.assertEqual(1000, obj.channels)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        subelement = element.find('limits')
        self.assertAlmostEqual(12.34, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(56.78, float(subelement.get('upper')), 4)

        subelement = element.find('channels')
        self.assertEqual(1000, int(subelement.text))

class Test_PolarAngularDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = _PolarAngularDetectorXMLHandler()

        self.obj = _PolarAngularDetector(50)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:_polarAngularDetector xmlns:mc="http://pymontecarlo.sf.net"><channels>50</channels><limits lower="-1.5707963267948966" upper="1.5707963267948966" /></mc:_polarAngularDetector>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertAlmostEqual(radians(-90), obj.limits_rad[0], 4)
        self.assertAlmostEqual(radians(90), obj.limits_rad[1], 4)
        self.assertEqual(50, obj.channels)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        subelement = element.find('limits')
        self.assertAlmostEqual(radians(-90), float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(90), float(subelement.get('upper')), 4)

        subelement = element.find('channels')
        self.assertEqual(50, int(subelement.text))

class Test_AzimuthalAngularDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = _AzimuthalAngularDetectorXMLHandler()

        self.obj = _AzimuthalAngularDetector(50)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:_azimuthalAngularDetector xmlns:mc="http://pymontecarlo.sf.net"><channels>50</channels><limits lower="0.0" upper="6.283185307179586" /></mc:_azimuthalAngularDetector>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertAlmostEqual(radians(0), obj.limits_rad[0], 4)
        self.assertAlmostEqual(radians(360), obj.limits_rad[1], 4)
        self.assertEqual(50, self.obj.channels)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        subelement = element.find('limits')
        self.assertAlmostEqual(radians(0), float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(360), float(subelement.get('upper')), 4)

        subelement = element.find('channels')
        self.assertEqual(50, int(subelement.text))

class Test_TransitionsDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = _TransitionsDetectorXMLHandler()

        self.t1 = Transition(24, siegbahn='Ka1')
        self.obj = _TransitionsDetector([self.t1])

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:_transitionsDetector xmlns:mc="http://pymontecarlo.sf.net"><transitions><transition z="24" src="4" dest="1" /></transitions></mc:_transitionsDetector>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertEqual(1, len(obj.transitions))
        self.assertEqual(self.t1, obj.transitions[0])

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        subelement = element.find('transitions')
        self.assertEqual(1, len(subelement))

        subsubelement = list(subelement)[0]
        self.assertEqual(24, int(subsubelement.get('z')))
        self.assertEqual(4, int(subsubelement.get('src')))
        self.assertEqual(1, int(subsubelement.get('dest')))

class TestBackscatteredElectronEnergyDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = BackscatteredElectronEnergyDetectorXMLHandler()

        self.obj = BackscatteredElectronEnergyDetector(1000, (12.34, 56.78))

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:backscatteredElectronEnergyDetector xmlns:mc="http://pymontecarlo.sf.net"><channels>1000</channels><limits lower="12.34" upper="56.78" /></mc:backscatteredElectronEnergyDetector>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertAlmostEqual(12.34, obj.limits_eV[0], 4)
        self.assertAlmostEqual(56.78, obj.limits_eV[1], 4)
        self.assertEqual(1000, obj.channels)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        subelement = element.find('limits')
        self.assertAlmostEqual(12.34, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(56.78, float(subelement.get('upper')), 4)

        subelement = element.find('channels')
        self.assertEqual(1000, int(subelement.text))

class TestTransmittedElectronEnergyDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = TransmittedElectronEnergyDetectorXMLHandler()

        self.obj = TransmittedElectronEnergyDetector(1000, (12.34, 56.78))

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:transmittedElectronEnergyDetector xmlns:mc="http://pymontecarlo.sf.net"><channels>1000</channels><limits lower="12.34" upper="56.78" /></mc:transmittedElectronEnergyDetector>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertAlmostEqual(12.34, obj.limits_eV[0], 4)
        self.assertAlmostEqual(56.78, obj.limits_eV[1], 4)
        self.assertEqual(1000, obj.channels)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        subelement = element.find('limits')
        self.assertAlmostEqual(12.34, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(56.78, float(subelement.get('upper')), 4)

        subelement = element.find('channels')
        self.assertEqual(1000, int(subelement.text))

class TestBackscatteredElectronPolarAngularDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = BackscatteredElectronPolarAngularDetectorXMLHandler()

        self.obj = BackscatteredElectronPolarAngularDetector(50)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:backscatteredElectronPolarAngularDetector xmlns:mc="http://pymontecarlo.sf.net"><channels>50</channels><limits lower="-1.5707963267948966" upper="1.5707963267948966" /></mc:backscatteredElectronPolarAngularDetector>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertAlmostEqual(radians(-90), obj.limits_rad[0], 4)
        self.assertAlmostEqual(radians(90), obj.limits_rad[1], 4)
        self.assertEqual(50, obj.channels)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        subelement = element.find('limits')
        self.assertAlmostEqual(radians(-90), float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(90), float(subelement.get('upper')), 4)

        subelement = element.find('channels')
        self.assertEqual(50, int(subelement.text))

class TestTransmittedElectronPolarAngularDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = TransmittedElectronPolarAngularDetectorXMLHandler()

        self.obj = TransmittedElectronPolarAngularDetector(50)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:transmittedElectronPolarAngularDetector xmlns:mc="http://pymontecarlo.sf.net"><channels>50</channels><limits lower="-1.5707963267948966" upper="1.5707963267948966" /></mc:transmittedElectronPolarAngularDetector>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertAlmostEqual(radians(-90), obj.limits_rad[0], 4)
        self.assertAlmostEqual(radians(90), obj.limits_rad[1], 4)
        self.assertEqual(50, obj.channels)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        subelement = element.find('limits')
        self.assertAlmostEqual(radians(-90), float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(90), float(subelement.get('upper')), 4)

        subelement = element.find('channels')
        self.assertEqual(50, int(subelement.text))

class TestBackscatteredElectronAzimuthalAngularDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = BackscatteredElectronAzimuthalAngularDetectorXMLHandler()

        self.obj = BackscatteredElectronAzimuthalAngularDetector(50)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:backscatteredElectronAzimuthalAngularDetector xmlns:mc="http://pymontecarlo.sf.net"><channels>50</channels><limits lower="0.0" upper="6.283185307179586" /></mc:backscatteredElectronAzimuthalAngularDetector>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertAlmostEqual(radians(0), obj.limits_rad[0], 4)
        self.assertAlmostEqual(radians(360), obj.limits_rad[1], 4)
        self.assertEqual(50, self.obj.channels)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        subelement = element.find('limits')
        self.assertAlmostEqual(radians(0), float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(360), float(subelement.get('upper')), 4)

        subelement = element.find('channels')
        self.assertEqual(50, int(subelement.text))

class TestTransmittedElectronAzimuthalAngularDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = TransmittedElectronAzimuthalAngularDetectorXMLHandler()

        self.obj = TransmittedElectronAzimuthalAngularDetector(50)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:transmittedElectronAzimuthalAngularDetector xmlns:mc="http://pymontecarlo.sf.net"><channels>50</channels><limits lower="0.0" upper="6.283185307179586" /></mc:transmittedElectronAzimuthalAngularDetector>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertAlmostEqual(radians(0), obj.limits_rad[0], 4)
        self.assertAlmostEqual(radians(360), obj.limits_rad[1], 4)
        self.assertEqual(50, self.obj.channels)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        subelement = element.find('limits')
        self.assertAlmostEqual(radians(0), float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(360), float(subelement.get('upper')), 4)

        subelement = element.find('channels')
        self.assertEqual(50, int(subelement.text))

class TestBackscatteredElectronRadialDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = BackscatteredElectronRadialDetectorXMLHandler()

        self.obj = BackscatteredElectronRadialDetector(10)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:backscatteredElectronRadialDetector xmlns:mc="http://pymontecarlo.sf.net"><channels>10</channels></mc:backscatteredElectronRadialDetector>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertEqual(10, obj.channels)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        subelement = element.find('channels')
        self.assertEqual(10, int(subelement.text))

class TestPhotonSpectrumDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = PhotonSpectrumDetectorXMLHandler()

        self.obj = PhotonSpectrumDetector((radians(35), radians(45)),
                                          (0, radians(360.0)),
                                          1000, (12.34, 56.78))

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:photonSpectrumDetector xmlns:mc="http://pymontecarlo.sf.net"><elevation lower="0.6108652381980153" upper="0.7853981633974483" /><azimuth lower="0.0" upper="6.283185307179586" /><channels>1000</channels><limits lower="12.34" upper="56.78" /></mc:photonSpectrumDetector>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertAlmostEqual(radians(35), obj.elevation_rad[0], 4)
        self.assertAlmostEqual(radians(45), obj.elevation_rad[1], 4)
        self.assertAlmostEqual(0, obj.azimuth_rad[0], 4)
        self.assertAlmostEqual(radians(360.0), obj.azimuth_rad[1], 4)
        self.assertAlmostEqual(12.34, obj.limits_eV[0], 4)
        self.assertAlmostEqual(56.78, obj.limits_eV[1], 4)
        self.assertEqual(1000, obj.channels)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        subelement = element.find('elevation')
        self.assertAlmostEqual(radians(35), float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(45), float(subelement.get('upper')), 4)

        subelement = element.find('azimuth')
        self.assertAlmostEqual(0, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(360.0), float(subelement.get('upper')), 4)

        subelement = element.find('limits')
        self.assertAlmostEqual(12.34, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(56.78, float(subelement.get('upper')), 4)

        subelement = element.find('channels')
        self.assertEqual(1000, int(subelement.text))

class TestPhotonDepthDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = PhotonDepthDetectorXMLHandler()

        self.obj = PhotonDepthDetector((radians(35), radians(45)),
                                       (0, radians(360.0)), 1000)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:photonDepthDetector xmlns:mc="http://pymontecarlo.sf.net"><elevation lower="0.6108652381980153" upper="0.7853981633974483" /><azimuth lower="0.0" upper="6.283185307179586" /><channels>1000</channels><transitions/></mc:photonDepthDetector>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertAlmostEqual(radians(35), obj.elevation_rad[0], 4)
        self.assertAlmostEqual(radians(45), obj.elevation_rad[1], 4)
        self.assertAlmostEqual(0, obj.azimuth_rad[0], 4)
        self.assertAlmostEqual(radians(360.0), obj.azimuth_rad[1], 4)
        self.assertEqual(1000, obj.channels)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        subelement = element.find('elevation')
        self.assertAlmostEqual(radians(35), float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(45), float(subelement.get('upper')), 4)

        subelement = element.find('azimuth')
        self.assertAlmostEqual(0, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(360.0), float(subelement.get('upper')), 4)

        subelement = element.find('channels')
        self.assertEqual(1000, int(subelement.text))

class TestPhiZDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = PhiZDetectorXMLHandler()

        self.obj = PhiZDetector((radians(35), radians(45)),
                                   (0, radians(360.0)), 1000)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:phiZDetector xmlns:mc="http://pymontecarlo.sf.net"><elevation lower="0.6108652381980153" upper="0.7853981633974483" /><azimuth lower="0.0" upper="6.283185307179586" /><channels>1000</channels><transitions/></mc:phiZDetector>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertAlmostEqual(radians(35), obj.elevation_rad[0], 4)
        self.assertAlmostEqual(radians(45), obj.elevation_rad[1], 4)
        self.assertAlmostEqual(0, obj.azimuth_rad[0], 4)
        self.assertAlmostEqual(radians(360.0), obj.azimuth_rad[1], 4)
        self.assertEqual(1000, obj.channels)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        subelement = element.find('elevation')
        self.assertAlmostEqual(radians(35), float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(45), float(subelement.get('upper')), 4)

        subelement = element.find('azimuth')
        self.assertAlmostEqual(0, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(360.0), float(subelement.get('upper')), 4)

        subelement = element.find('channels')
        self.assertEqual(1000, int(subelement.text))

class TestPhotonRadialDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = PhotonRadialDetectorXMLHandler()

        self.obj = PhotonRadialDetector((radians(35), radians(45)),
                                        (0, radians(360.0)), 1000)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:photonRadialDetector xmlns:mc="http://pymontecarlo.sf.net"><elevation lower="0.6108652381980153" upper="0.7853981633974483" /><azimuth lower="0.0" upper="6.283185307179586" /><channels>1000</channels><transitions/></mc:photonRadialDetector>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertAlmostEqual(radians(35), obj.elevation_rad[0], 4)
        self.assertAlmostEqual(radians(45), obj.elevation_rad[1], 4)
        self.assertAlmostEqual(0, obj.azimuth_rad[0], 4)
        self.assertAlmostEqual(radians(360.0), obj.azimuth_rad[1], 4)
        self.assertEqual(1000, obj.channels)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        subelement = element.find('elevation')
        self.assertAlmostEqual(radians(35), float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(45), float(subelement.get('upper')), 4)

        subelement = element.find('azimuth')
        self.assertAlmostEqual(0, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(360.0), float(subelement.get('upper')), 4)

        subelement = element.find('channels')
        self.assertEqual(1000, int(subelement.text))

class TestPhotonEmissionMapDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = PhotonEmissionMapDetectorXMLHandler()

        self.obj = PhotonEmissionMapDetector((radians(35), radians(45)),
                                             (0, radians(360.0)), 5, 6, 7)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:photonEmissionMapDetector xmlns:mc="http://pymontecarlo.sf.net"><elevation lower="0.6108652381980153" upper="0.7853981633974483" /><azimuth lower="0.0" upper="6.283185307179586" /><xbins>5</xbins><ybins>6</ybins><zbins>7</zbins></mc:photonEmissionMapDetector>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertAlmostEqual(radians(35), obj.elevation_rad[0], 4)
        self.assertAlmostEqual(radians(45), obj.elevation_rad[1], 4)
        self.assertAlmostEqual(0, obj.azimuth_rad[0], 4)
        self.assertAlmostEqual(radians(360.0), obj.azimuth_rad[1], 4)
        self.assertEqual(5, obj.xbins)
        self.assertEqual(6, obj.ybins)
        self.assertEqual(7, obj.zbins)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        subelement = element.find('elevation')
        self.assertAlmostEqual(radians(35), float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(45), float(subelement.get('upper')), 4)

        subelement = element.find('azimuth')
        self.assertAlmostEqual(0, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(360.0), float(subelement.get('upper')), 4)

        subelement = element.find('xbins')
        self.assertEqual(5, int(subelement.text))

        subelement = element.find('ybins')
        self.assertEqual(6, int(subelement.text))

        subelement = element.find('zbins')
        self.assertEqual(7, int(subelement.text))

class TestPhotonIntensityDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = PhotonIntensityDetectorXMLHandler()

        self.obj = PhotonIntensityDetector((radians(35), radians(45)),
                                           (0, radians(360.0)))

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:photonIntensityDetector xmlns:mc="http://pymontecarlo.sf.net"><elevation lower="0.6108652381980153" upper="0.7853981633974483" /><azimuth lower="0.0" upper="6.283185307179586" /><transitions/></mc:photonIntensityDetector>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertAlmostEqual(radians(35), obj.elevation_rad[0], 4)
        self.assertAlmostEqual(radians(45), obj.elevation_rad[1], 4)
        self.assertAlmostEqual(0, obj.azimuth_rad[0], 4)
        self.assertAlmostEqual(radians(360.0), obj.azimuth_rad[1], 4)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        subelement = element.find('elevation')
        self.assertAlmostEqual(radians(35), float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(45), float(subelement.get('upper')), 4)

        subelement = element.find('azimuth')
        self.assertAlmostEqual(0, float(subelement.get('lower')), 4)
        self.assertAlmostEqual(radians(360.0), float(subelement.get('upper')), 4)

class TestTimeDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = TimeDetectorXMLHandler()

        self.obj = TimeDetector()

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:timeDetector xmlns:mc="http://pymontecarlo.sf.net" />')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        self.h.parse(self.element)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        self.h.convert(self.obj)

class TestElectronFractionDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = ElectronFractionDetectorXMLHandler()

        self.obj = ElectronFractionDetector()

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:electronFractionDetector xmlns:mc="http://pymontecarlo.sf.net" />')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        self.h.parse(self.element)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        self.h.convert(self.obj)

class TestShowersStatisticsDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = ShowersStatisticsDetectorXMLHandler()

        self.obj = ShowersStatisticsDetector()

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:showersStatisticsDetector xmlns:mc="http://pymontecarlo.sf.net" />')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        self.h.parse(self.element)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        self.h.convert(self.obj)

class TestTrajectoryDetectorXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = TrajectoryDetectorXMLHandler()

        self.obj = TrajectoryDetector(False)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:trajectoryDetector xmlns:mc="http://pymontecarlo.sf.net"><secondary>false</secondary></mc:trajectoryDetector>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertFalse(obj.secondary)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        subelement = element.find('secondary')
        self.assertEqual('false', subelement.text)

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

