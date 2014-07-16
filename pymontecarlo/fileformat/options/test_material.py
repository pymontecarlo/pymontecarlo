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
from pymontecarlo.fileformat.options.material import \
    MaterialXMLHandler, VACUUMXMLHandler
from pymontecarlo.options.material import Material, VACUUM
from pymontecarlo.options.particle import POSITRON

# Globals and constants variables.

class TestMaterialXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = MaterialXMLHandler()

        self.obj = Material({'Cu': 1.0}, 'Pure Cu', 8960.0, {POSITRON: 52.0})

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:material xmlns:mc="http://pymontecarlo.sf.net" density="8960.0" name="Pure Cu"><composition><element weightFraction="1.0" z="29" /></composition><absorptionEnergy particle="positron">52.0</absorptionEnergy></mc:material>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertEqual('Pure Cu', str(obj))

        self.assertIn(29, obj.composition)
        self.assertAlmostEqual(1.0, obj.composition[29], 4)

        self.assertAlmostEqual(8960.0, obj.density_kg_m3, 4)

        self.assertAlmostEqual(52, obj.absorption_energy_eV[POSITRON], 4)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        self.assertEqual('Pure Cu', element.get('name'))

        children = list(element.find('composition'))
        self.assertEqual(1, len(children))
        self.assertEqual(29, int(children[0].get('z')))
        self.assertEqual('1.0', children[0].get('weightFraction'))

        self.assertEqual('8960.0', element.get('density'))

        children = list(element.findall('absorptionEnergy'))
        self.assertEqual(3, len(children))

        for child in children:
            if child.get('particle') == 'positron':
                self.assertAlmostEqual(52.0, float(child.text), 4)
            else:
                self.assertAlmostEqual(Material.DEFAULT_ABSORPTION_ENERGY_eV, float(child.text), 4)

class TestVACUUMXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = VACUUMXMLHandler()

        self.obj = VACUUM

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:vacuum xmlns:mc="http://pymontecarlo.sf.net" />')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertIs(VACUUM, obj)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        self.assertEqual(0, len(list(element)))

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
