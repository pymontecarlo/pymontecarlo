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

# Third party modules.

# Local modules.
from pymontecarlo.input.base.geometry import \
    _Geometry, Substrate, Inclusion, MultiLayers, GrainBoundaries
from pymontecarlo.input.base.material import pure
from pymontecarlo.input.base.body import Layer

# Globals and constants variables.

class Test_Geometry(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.g = _Geometry(1.1, 2.2)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(1.1, self.g.tilt, 4)
        self.assertAlmostEqual(2.2, self.g.rotation, 4)

    def testfrom_xml(self):
        element = self.g.to_xml()
        g = _Geometry.from_xml(element)

        self.assertAlmostEqual(1.1, g.tilt, 4)
        self.assertAlmostEqual(2.2, g.rotation, 4)

    def testto_xml(self):
        element = self.g.to_xml()

        self.assertEqual('_Geometry', element.tag)

        self.assertAlmostEqual(1.1, float(element.get('tilt')), 4)
        self.assertAlmostEqual(2.2, float(element.get('rotation')), 4)

class TestSubstrate(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.g = Substrate(pure(29))

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('Copper', str(self.g.material))

    def testfrom_xml(self):
        self.g.tilt = 1.1
        self.g.rotation = 2.2
        element = self.g.to_xml()
        g = Substrate.from_xml(element)

        self.assertEqual('Copper', str(g.material))
        self.assertAlmostEqual(1.1, g.tilt, 4)
        self.assertAlmostEqual(2.2, g.rotation, 4)

    def testbody(self):
        self.assertEqual(self.g.material, self.g.body.material)

    def testget_bodies(self):
        self.assertEqual(1, len(self.g.get_bodies()))

    def testto_xml(self):
        element = self.g.to_xml()

        self.assertEqual('Substrate', element.tag)

        child = list(element.find('material'))[0]
        self.assertEqual('Copper', child.get('name'))

class TestInclusion(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.g = Inclusion(pure(29), pure(30), 123.456)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('Copper', str(self.g.substrate_material))
        self.assertEqual('Zinc', str(self.g.inclusion_material))
        self.assertAlmostEqual(123.456, self.g.inclusion_diameter, 4)

    def testfrom_xml(self):
        self.g.tilt = 1.1
        self.g.rotation = 2.2
        element = self.g.to_xml()
        g = Inclusion.from_xml(element)

        self.assertEqual('Copper', str(g.substrate_material))
        self.assertEqual('Zinc', str(g.inclusion_material))
        self.assertAlmostEqual(123.456, g.inclusion_diameter, 4)

        self.assertAlmostEqual(1.1, g.tilt, 4)
        self.assertAlmostEqual(2.2, g.rotation, 4)

    def testsubstrate_body(self):
        self.assertEqual(self.g.substrate_material, self.g.substrate_body.material)

    def testinclusion_body(self):
        self.assertEqual(self.g.inclusion_material, self.g.inclusion_body.material)

    def testinclusion_diameter(self):
        self.assertAlmostEqual(123.456, self.g.inclusion_diameter, 4)

        self.assertRaises(ValueError, self.g.__setattr__, 'inclusion_diameter', -1)

    def testget_bodies(self):
        self.assertEqual(2, len(self.g.get_bodies()))

    def testto_xml(self):
        element = self.g.to_xml()

        self.assertEqual('Inclusion', element.tag)

        child = list(element.find('substrateMaterial'))[0]
        self.assertEqual('Copper', child.get('name'))

        child = list(element.find('inclusionMaterial'))[0]
        self.assertEqual('Zinc', child.get('name'))

        self.assertAlmostEqual(123.456, float(element.get('inclusionDiameter')), 4)

class TestMultiLayers(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.g1 = MultiLayers(pure(29))
        self.g2 = MultiLayers(None)

        l1 = Layer(pure(30), 123.456)
        l2 = Layer(pure(31), 456.789)

        self.g1.layers.extend([l1, l2])
        self.g2.layers.extend([l1, l2])

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        # Multi-layers 1
        self.assertTrue(self.g1.has_substrate())
        self.assertEqual('Copper', str(self.g1.substrate_material))

        self.assertEqual(2, len(self.g1.layers))
        self.assertEqual('Zinc', str(self.g1.layers[0].material))
        self.assertEqual('Gallium', str(self.g1.layers[1].material))

        # Multi-layers 2
        self.assertFalse(self.g2.has_substrate())

        self.assertEqual(2, len(self.g2.layers))
        self.assertEqual('Zinc', str(self.g2.layers[0].material))
        self.assertEqual('Gallium', str(self.g2.layers[1].material))

    def testfrom_xml(self):
        # Multi-layers 1
        self.g1.tilt = 1.1
        self.g1.rotation = 2.2
        element = self.g1.to_xml()
        g1 = MultiLayers.from_xml(element)

        self.assertTrue(g1.has_substrate())
        self.assertEqual('Copper', str(g1.substrate_material))

        self.assertEqual(2, len(g1.layers))
        self.assertEqual('Zinc', str(g1.layers[0].material))
        self.assertEqual('Gallium', str(g1.layers[1].material))

        self.assertAlmostEqual(1.1, g1.tilt, 4)
        self.assertAlmostEqual(2.2, g1.rotation, 4)

        # Multi-layers 2
        element = self.g2.to_xml()
        g2 = MultiLayers.from_xml(element)

        self.assertFalse(g2.has_substrate())

        self.assertEqual(2, len(g2.layers))
        self.assertEqual('Zinc', str(g2.layers[0].material))
        self.assertEqual('Gallium', str(g2.layers[1].material))

    def testsubstrate_material(self):
        self.g1.substrate_material = None
        self.assertFalse(self.g1.has_substrate())
        self.assertRaises(RuntimeError, self.g1.__getattribute__, 'substrate_material')

    def testsubstrate_body(self):
        self.assertEqual(self.g1.substrate_material, self.g1.substrate_body.material)

    def testget_bodies(self):
        self.assertEqual(3, len(self.g1.get_bodies()))
        self.assertEqual(2, len(self.g2.get_bodies()))

    def testto_xml(self):
        # Multi-layers 1
        element = self.g1.to_xml()

        self.assertEqual('MultiLayers', element.tag)

        children = list(element.find('layers'))
        self.assertEqual(2, len(children))

        children = list(element.find('substrateMaterial'))
        self.assertEqual(1, len(children))
        self.assertEqual('Copper', children[0].get('name'))

        # Multi-layers 2
        element = self.g2.to_xml()

        self.assertEqual('MultiLayers', element.tag)

        children = list(element.find('layers'))
        self.assertEqual(2, len(children))

        children = list(element.find('substrateMaterial'))
        self.assertEqual(0, len(children))

class TestGrainBoundaries(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.g = GrainBoundaries(pure(29), pure(30))
        self.g.layers.append(Layer(pure(31), 456.789))

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('Copper', str(self.g.left_material))
        self.assertEqual('Zinc', str(self.g.right_material))

        self.assertEqual(1, len(self.g.layers))
        self.assertEqual('Gallium', str(self.g.layers[0].material))

    def testfrom_xml(self):
        self.g.tilt = 1.1
        self.g.rotation = 2.2
        element = self.g.to_xml()
        g = GrainBoundaries.from_xml(element)

        self.assertEqual('Copper', str(g.left_material))
        self.assertEqual('Zinc', str(g.right_material))

        self.assertEqual(1, len(g.layers))
        self.assertEqual('Gallium', str(g.layers[0].material))

        self.assertAlmostEqual(1.1, g.tilt, 4)
        self.assertAlmostEqual(2.2, g.rotation, 4)

    def testleft_body(self):
        self.assertEqual(self.g.left_material, self.g.left_body.material)

    def testright_body(self):
        self.assertEqual(self.g.right_material, self.g.right_body.material)

    def testget_bodies(self):
        self.assertEqual(3, len(self.g.get_bodies()))

    def testto_xml(self):
        # Multi-layers 1
        element = self.g.to_xml()

        self.assertEqual('GrainBoundaries', element.tag)

        children = list(element.find('layers'))
        self.assertEqual(1, len(children))

        child = list(element.find('leftMaterial'))[0]
        self.assertEqual('Copper', child.get('name'))

        child = list(element.find('rightMaterial'))[0]
        self.assertEqual('Zinc', child.get('name'))


if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
