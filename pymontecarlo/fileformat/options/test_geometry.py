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
from pymontecarlo.fileformat.options.geometry import \
    (_GeometryXMLHandler, SubstrateXMLHandler, InclusionXMLHandler,
     HorizontalLayersXMLHandler, VerticalLayersXMLHandler,
     SphereXMLHandler)

from pymontecarlo.options.geometry import \
    _Geometry, Substrate, Inclusion, HorizontalLayers, VerticalLayers, Sphere
from pymontecarlo.options.material import Material, VACUUM

# Globals and constants variables.

class Test_GeometryXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = _GeometryXMLHandler()

        self.obj = _Geometry(1.1, 2.2)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:_geometry xmlns:mc="http://pymontecarlo.sf.net" rotation="2.2" tilt="1.1" />')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertAlmostEqual(1.1, obj.tilt_rad, 4)
        self.assertAlmostEqual(2.2, obj.rotation_rad, 4)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        self.assertAlmostEqual(1.1, float(element.get('tilt')), 4)
        self.assertAlmostEqual(2.2, float(element.get('rotation')), 4)

class TestSubstrateXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = SubstrateXMLHandler()

        self.obj = Substrate([Material.pure(29), Material.pure(30)], 1.1, 2.2)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:substrate xmlns:mc="http://pymontecarlo.sf.net" rotation="2.2" tilt="1.1"><materials><mc:material _index="1" density="8960.0" name="Copper"><composition><element weightFraction="1.0" z="29" /></composition></mc:material><mc:material _index="2" density="7140.0" name="Zinc"><composition><element weightFraction="1.0" z="30" /></composition></mc:material></materials><body material="1,2" /></mc:substrate>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertAlmostEqual(1.1, obj.tilt_rad, 4)
        self.assertAlmostEqual(2.2, obj.rotation_rad, 4)

        self.assertEqual(2, len(obj.body.material))
        self.assertEqual('Copper', str(obj.body.material[0]))
        self.assertEqual('Zinc', str(obj.body.material[1]))

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        self.assertAlmostEqual(1.1, float(element.get('tilt')), 4)
        self.assertAlmostEqual(2.2, float(element.get('rotation')), 4)
        self.assertEqual('1,2', element.find('body').get('material'))

class TestInclusionXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = InclusionXMLHandler()

        self.obj = Inclusion(Material.pure(29), Material.pure(30), 123.456, 1.1, 2.2)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:inclusion xmlns:mc="http://pymontecarlo.sf.net" rotation="2.2" tilt="1.1"><materials><mc:material _index="1" density="7140.0" name="Zinc"><composition><element weightFraction="1.0" z="30" /></composition></mc:material><mc:material _index="2" density="8960.0" name="Copper"><composition><element weightFraction="1.0" z="29" /></composition></mc:material></materials><substrate material="2" /><inclusion diameter="123.456" material="1" /></mc:inclusion>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertEqual('Copper', str(obj.substrate.material))
        self.assertEqual('Zinc', str(obj.inclusion.material))
        self.assertAlmostEqual(123.456, obj.inclusion.diameter_m, 4)

        self.assertAlmostEqual(1.1, obj.tilt_rad, 4)
        self.assertAlmostEqual(2.2, obj.rotation_rad, 4)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        self.assertAlmostEqual(1.1, float(element.get('tilt')), 4)
        self.assertAlmostEqual(2.2, float(element.get('rotation')), 4)

        subelement = element.find('inclusion')
        self.assertAlmostEqual(123.456, float(subelement.get('diameter')), 4)

class TestHorizontalLayersXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = HorizontalLayersXMLHandler()

        self.obj1 = HorizontalLayers(Material.pure(29), None, 1.1, 2.2)
        self.obj1.add_layer(Material.pure(30), 123.456)
        self.obj1.add_layer(Material.pure(31), 456.789)

        self.obj2 = HorizontalLayers()
        self.obj2.add_layer(Material.pure(30), 123.456)
        self.obj2.add_layer(VACUUM, 50.0)
        self.obj2.add_layer(Material.pure(31), 456.789)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:horizontalLayers xmlns:mc="http://pymontecarlo.sf.net" rotation="2.2" tilt="1.1"><materials><mc:material _index="1" density="7140.0" name="Zinc"><composition><element weightFraction="1.0" z="30" /></composition></mc:material><mc:material _index="2" density="5910.0" name="Gallium"><composition><element weightFraction="1.0" z="31" /></composition></mc:material><mc:material _index="3" density="8960.0" name="Copper"><composition><element weightFraction="1.0" z="29" /></composition></mc:material></materials><substrate material="3" /><layers><layer material="1" thickness="123.456" /><layer material="2" thickness="456.789" /></layers></mc:horizontalLayers>')
        self.element1 = etree.parse(source).getroot()

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:horizontalLayers xmlns:mc="http://pymontecarlo.sf.net" rotation="0.0" tilt="0.0"><materials><mc:material _index="1" density="7140.0" name="Zinc"><composition><element weightFraction="1.0" z="30" /></composition></mc:material><mc:material _index="2" density="5910.0" name="Gallium"><composition><element weightFraction="1.0" z="31" /></composition></mc:material></materials><layers><layer material="1" thickness="123.456" /><layer material="0" thickness="50.0" /><layer material="2" thickness="456.789" /></layers></mc:horizontalLayers>')
        self.element2 = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element1))
        self.assertTrue(self.h.can_parse(self.element2))

    def testparse(self):
        # Horizontal layers 1
        obj = self.h.parse(self.element1)

        self.assertTrue(obj.has_substrate())
        self.assertEqual('Copper', str(obj.substrate.material))

        self.assertEqual(2, len(obj.layers))
        self.assertEqual('Zinc', str(obj.layers[0].material))
        self.assertAlmostEqual(123.456, obj.layers[0].thickness_m)
        self.assertEqual('Gallium', str(obj.layers[1].material))
        self.assertAlmostEqual(456.789, obj.layers[1].thickness_m)

        self.assertAlmostEqual(1.1, obj.tilt_rad, 4)
        self.assertAlmostEqual(2.2, obj.rotation_rad, 4)

        # Horizontal layers 2
        obj = self.h.parse(self.element2)

        self.assertFalse(obj.has_substrate())

        self.assertEqual(3, len(obj.layers))
        self.assertEqual('Zinc', str(obj.layers[0].material))
        self.assertAlmostEqual(123.456, obj.layers[0].thickness_m)
        self.assertEqual('Vacuum', str(obj.layers[1].material))
        self.assertAlmostEqual(50.0, obj.layers[1].thickness_m)
        self.assertEqual('Gallium', str(obj.layers[2].material))
        self.assertAlmostEqual(456.789, obj.layers[2].thickness_m)

        self.assertAlmostEqual(0.0, obj.tilt_rad, 4)
        self.assertAlmostEqual(0.0, obj.rotation_rad, 4)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj1))
        self.assertTrue(self.h.can_convert(self.obj2))

    def testconvert(self):
        # Horizontal layers 1
        element = self.h.convert(self.obj1)

        self.assertAlmostEqual(1.1, float(element.get('tilt')), 4)
        self.assertAlmostEqual(2.2, float(element.get('rotation')), 4)
        self.assertEqual(3, len(list(element.find('materials'))))
        self.assertEqual(2, len(list(element.find('layers'))))

        # Horizontal layers 2
        element = self.h.convert(self.obj2)

        self.assertAlmostEqual(0.0, float(element.get('tilt')), 4)
        self.assertAlmostEqual(0.0, float(element.get('rotation')), 4)
        self.assertEqual(2, len(list(element.find('materials'))))
        self.assertEqual(3, len(list(element.find('layers'))))

class TestVerticalLayersXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = VerticalLayersXMLHandler()

        self.obj1 = VerticalLayers(Material.pure(29), Material.pure(30), None,
                                   tilt_rad=1.1, rotation_rad=2.2)
        self.obj1.add_layer(Material.pure(31), 500.0)

        self.obj2 = VerticalLayers(Material.pure(29), Material.pure(30))
        self.obj2.add_layer(Material.pure(31), 500.0)
        self.obj2.depth_m = 400.0

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:verticalLayers xmlns:mc="http://pymontecarlo.sf.net" rotation="2.2" tilt="1.1"><materials><mc:material _index="1" density="5910.0" name="Gallium"><composition><element weightFraction="1.0" z="31" /></composition></mc:material><mc:material _index="2" density="8960.0" name="Copper"><composition><element weightFraction="1.0" z="29" /></composition></mc:material><mc:material _index="3" density="7140.0" name="Zinc"><composition><element weightFraction="1.0" z="30" /></composition></mc:material></materials><leftSubstrate depth="inf" material="2" /><rightSubstrate depth="inf" material="3" /><layers><layer depth="inf" material="1" thickness="500.0" /></layers></mc:verticalLayers>')
        self.element1 = etree.parse(source).getroot()

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:verticalLayers xmlns:mc="http://pymontecarlo.sf.net" rotation="0.0" tilt="0.0"><materials><mc:material _index="1" density="8960.0" name="Copper"><composition><element weightFraction="1.0" z="29" /></composition></mc:material><mc:material _index="2" density="5910.0" name="Gallium"><composition><element weightFraction="1.0" z="31" /></composition></mc:material><mc:material _index="3" density="7140.0" name="Zinc"><composition><element weightFraction="1.0" z="30" /></composition></mc:material></materials><leftSubstrate depth="400.0" material="1" /><rightSubstrate depth="400.0" material="3" /><layers><layer depth="400.0" material="2" thickness="500.0" /></layers></mc:verticalLayers>')
        self.element2 = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element1))
        self.assertTrue(self.h.can_parse(self.element2))

    def testparse(self):
        # Vertical layers 1
        obj = self.h.parse(self.element1)

        self.assertEqual('Copper', str(obj.left_substrate.material))
        self.assertEqual('Zinc', str(obj.right_substrate.material))

        self.assertEqual('Gallium', str(obj.layers.material))
        self.assertAlmostEqual(500.0, obj.layers.thickness_m, 4)

        self.assertAlmostEqual(1.1, obj.tilt_rad, 4)
        self.assertAlmostEqual(2.2, obj.rotation_rad, 4)

        # Vertical layers 2
        obj = self.h.parse(self.element2)

        self.assertAlmostEqual(400.0, obj.depth_m, 4)

        self.assertEqual('Copper', str(obj.left_substrate.material))
        self.assertEqual('Zinc', str(obj.right_substrate.material))

        self.assertEqual('Gallium', str(obj.layers.material))
        self.assertAlmostEqual(500.0, obj.layers.thickness_m, 4)

        self.assertAlmostEqual(0.0, obj.tilt_rad, 4)
        self.assertAlmostEqual(0.0, obj.rotation_rad, 4)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj1))
        self.assertTrue(self.h.can_convert(self.obj2))

    def testconvert(self):
        # Vertical layers 1
        element = self.h.convert(self.obj1)

        self.assertAlmostEqual(1.1, float(element.get('tilt')), 4)
        self.assertAlmostEqual(2.2, float(element.get('rotation')), 4)
        self.assertEqual(3, len(list(element.find('materials'))))
        self.assertEqual(1, len(list(element.find('layers'))))

        # Vertical layers 2
        element = self.h.convert(self.obj2)

        self.assertAlmostEqual(0.0, float(element.get('tilt')), 4)
        self.assertAlmostEqual(0.0, float(element.get('rotation')), 4)
        self.assertEqual(3, len(list(element.find('materials'))))
        self.assertEqual(1, len(list(element.find('layers'))))

class TestSphereXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = SphereXMLHandler()

        self.obj = Sphere(Material.pure(29), 123.456, 1.1, 2.2)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:sphere xmlns:mc="http://pymontecarlo.sf.net" rotation="2.2" tilt="1.1"><materials><mc:material _index="1" density="8960.0" name="Copper"><composition><element weightFraction="1.0" z="29" /></composition></mc:material></materials><body diameter="123.456" material="1" /></mc:sphere>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertEqual('Copper', str(obj.body.material))
        self.assertAlmostEqual(123.456, obj.body.diameter_m, 4)

        self.assertAlmostEqual(1.1, obj.tilt_rad, 4)
        self.assertAlmostEqual(2.2, obj.rotation_rad, 4)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        self.assertAlmostEqual(1.1, float(element.get('tilt')), 4)
        self.assertAlmostEqual(2.2, float(element.get('rotation')), 4)

        subelement = element.find('body')
        self.assertAlmostEqual(123.456, float(subelement.get('diameter')), 4)

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
