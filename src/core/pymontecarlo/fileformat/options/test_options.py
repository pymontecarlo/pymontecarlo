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

# Third party modules.

# Local modules.
from pymontecarlo.fileformat.options.options import OptionsXMLHandler

from pymontecarlo.options.options import Options
from pymontecarlo.options.detector import BackscatteredElectronEnergyDetector
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.options.model import ELASTIC_CROSS_SECTION

# Globals and constants variables.

class TestOptionsXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = OptionsXMLHandler()

        self.obj = Options(name="Test")
        self.obj.beam.energy_eV = 1234

        self.obj.detectors['bse'] = BackscatteredElectronEnergyDetector(1000, (0, 1234))
        self.obj.limits.add(ShowersLimit(5678))
        self.obj.models.add(ELASTIC_CROSS_SECTION.rutherford)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:options xmlns:mc="http://pymontecarlo.sf.net" name="Test" uuid="51d62e0261f2449eb41a74e4cb4501e0" version="7"><beam><mc:pencilBeam aperture="0.0" energy="1234.0" particle="electron"><origin x="0.0" y="0.0" z="1.0" /><direction u="0.0" v="0.0" w="-1.0" /></mc:pencilBeam></beam><geometry><mc:substrate rotation="0.0" tilt="0.0"><materials><mc:material _index="1" density="19300.0" name="Gold"><composition><element weightFraction="1.0" z="79" /></composition></mc:material></materials><body material="1" /></mc:substrate></geometry><detectors><mc:backscatteredElectronEnergyDetector _key="bse"><channels>1000</channels><limits lower="0.0" upper="1234.0" /></mc:backscatteredElectronEnergyDetector></detectors><limits><mc:showersLimit showers="5678" /></limits><models><mc:model name="Rutherford" type="elastic cross section" /></models></mc:options>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertEqual("Test", obj.name)
        self.assertEqual('51d62e0261f2449eb41a74e4cb4501e0', obj.uuid)

        self.assertAlmostEqual(1234, obj.beam.energy_eV, 4)

        self.assertEqual(1, len(obj.detectors))
        det = obj.detectors['bse']
        self.assertAlmostEqual(0, det.limits_eV[0], 4)
        self.assertAlmostEqual(1234, det.limits_eV[1], 4)
        self.assertEqual(1000, det.channels)

        self.assertEqual(1, len(obj.limits))
        limits = list(obj.limits.iterclass(ShowersLimit))
        self.assertEqual(1, len(limits))
        self.assertEqual(5678, limits[0].showers)

        self.assertEqual(1, len(obj.models))
        models = list(obj.models.iterclass(ELASTIC_CROSS_SECTION))
        self.assertEqual(1, len(models))
        self.assertEqual(ELASTIC_CROSS_SECTION.rutherford, models[0])

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        self.assertEqual('Test', element.get('name'))

        self.assertEqual(self.obj.uuid, element.get('uuid'))

        children = list(element.find('beam'))
        self.assertEqual(1, len(children))

        children = list(element.find('geometry'))
        self.assertEqual(1, len(children))

        children = list(element.find('detectors'))
        self.assertEqual(1, len(children))

        children = list(element.find('limits'))
        self.assertEqual(1, len(children))

        children = list(element.find('models'))
        self.assertEqual(1, len(children))

    def testconvert2(self):
        uuid = self.obj.uuid
        element = self.h.convert(self.obj)
        self.assertEqual(uuid, element.get('uuid'))

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
