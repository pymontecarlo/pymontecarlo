#!/usr/bin/env python
"""
================================================================================
:mod:`geometry` -- XML handler for geometries
================================================================================

.. module:: geometry
   :synopsis: XML handler for geometries

.. inheritance-diagram:: pymontecarlo.fileformat.options.geometry

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import xml.etree.ElementTree as etree

# Third party modules.
import numpy as np

# Local modules.
from pymontecarlo.fileformat.xmlhandler import _XMLHandler

from pymontecarlo.options.geometry import \
    _Geometry, Substrate, Inclusion, HorizontalLayers, VerticalLayers, Sphere
from pymontecarlo.options.material import VACUUM

# Globals and constants variables.

class _GeometryXMLHandler(_XMLHandler):

    TAG = '{http://pymontecarlo.sf.net}_geometry'
    CLASS = _Geometry

    def parse(self, element):
        tilt_rad = self._parse_numerical_parameter(element, 'tilt')
        rotation_rad = self._parse_numerical_parameter(element, 'rotation')
        return _Geometry(tilt_rad, rotation_rad)

    def _parse_materials(self, element):
        subelement = element.find('materials')
        if subelement is None:
            raise ValueError("Element 'materials' not found")

        materials_lookup = {0: VACUUM}
        for i, subsubelement in enumerate(subelement, 1):
            material = self._parse_handlers('pymontecarlo.fileformat.options.material', subsubelement)
            materials_lookup[i] = material

        return materials_lookup

    def convert(self, obj):
        element = _XMLHandler.convert(self, obj)

        self._convert_numerical_parameter(element, obj.tilt_rad, 'tilt')
        self._convert_numerical_parameter(element, obj.rotation_rad, 'rotation')

        return element

    def _convert_materials(self, element, materials):
        subelement = etree.SubElement(element, 'materials')

        materials_lookup = {VACUUM: 0}
        for i, material in enumerate(materials, 1):
            subsubelement = self._convert_handlers('pymontecarlo.fileformat.options.material', material)
            subsubelement.set('_index', str(i))
            subelement.append(subsubelement)
            materials_lookup[material] = i

        return materials_lookup

class SubstrateXMLHandler(_GeometryXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}substrate'
    CLASS = Substrate

    def parse(self, element):
        geo = _GeometryXMLHandler.parse(self, element)

        materials_lookup = self._parse_materials(element)

        subelement = element.find('body')
        if subelement is None:
            raise ValueError("Element 'body' not found")
        indexes = self._parse_numerical_parameter(subelement, 'material')
        material = list(map(materials_lookup.get, indexes))

        return Substrate(material, geo.tilt_rad, geo.rotation_rad)

    def convert(self, obj):
        element = _GeometryXMLHandler.convert(self, obj)

        materials_lookup = self._convert_materials(element, obj.get_materials())

        subelement = etree.SubElement(element, 'body')
        indexes = sorted(map(materials_lookup.get,
                             np.array(obj.body.material, ndmin=1)))
        self._convert_numerical_parameter(subelement, indexes, 'material')

        return element

class InclusionXMLHandler(_GeometryXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}inclusion'
    CLASS = Inclusion

    def parse(self, element):
        geo = _GeometryXMLHandler.parse(self, element)

        materials_lookup = self._parse_materials(element)

        subelement = element.find('substrate')
        if subelement is None:
            raise ValueError("Element 'substrate' not found")
        indexes = self._parse_numerical_parameter(subelement, 'material')
        substrate_material = list(map(materials_lookup.get, indexes))

        subelement = element.find('inclusion')
        if subelement is None:
            raise ValueError("Element 'inclusion' not found")
        indexes = self._parse_numerical_parameter(subelement, 'material')
        inclusion_material = list(map(materials_lookup.get, indexes))
        inclusion_diameter_m = self._parse_numerical_parameter(subelement, 'diameter')

        return Inclusion(substrate_material, inclusion_material, inclusion_diameter_m,
                         geo.tilt_rad, geo.rotation_rad)

    def convert(self, obj):
        element = _GeometryXMLHandler.convert(self, obj)

        materials_lookup = self._convert_materials(element, obj.get_materials())

        subelement = etree.SubElement(element, 'substrate')
        indexes = sorted(map(materials_lookup.get,
                             np.array(obj.substrate.material, ndmin=1)))
        self._convert_numerical_parameter(subelement, indexes, 'material')

        subelement = etree.SubElement(element, 'inclusion')
        indexes = sorted(map(materials_lookup.get,
                             np.array(obj.inclusion.material, ndmin=1)))
        self._convert_numerical_parameter(subelement, indexes, 'material')
        self._convert_numerical_parameter(subelement, obj.inclusion.diameter_m, 'diameter')

        return element

class HorizontalLayersXMLHandler(_GeometryXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}horizontalLayers'
    CLASS = HorizontalLayers

    def parse(self, element):
        geo = _GeometryXMLHandler.parse(self, element)

        materials_lookup = self._parse_materials(element)

        subelement = element.find('substrate')
        if subelement is None:
            substrate_material = VACUUM
        else:
            indexes = self._parse_numerical_parameter(subelement, 'material')
            substrate_material = list(map(materials_lookup.get, indexes))

        obj = HorizontalLayers(substrate_material, None,
                               geo.tilt_rad, geo.rotation_rad)

        subelement = element.find('layers')
        if subelement is None:
            raise ValueError("Element 'layers' not found")
        for subsubelement in subelement:
            indexes = self._parse_numerical_parameter(subsubelement, 'material')
            material = list(map(materials_lookup.get, indexes))
            thickness_m = self._parse_numerical_parameter(subsubelement, 'thickness')
            obj.add_layer(material, thickness_m)

        return obj

    def convert(self, obj):
        element = _GeometryXMLHandler.convert(self, obj)

        materials_lookup = self._convert_materials(element, obj.get_materials())

        if obj.has_substrate():
            subelement = etree.SubElement(element, 'substrate')
            indexes = sorted(map(materials_lookup.get,
                                 np.array(obj.substrate.material, ndmin=1)))
            self._convert_numerical_parameter(subelement, indexes, 'material')

        subelement = etree.SubElement(element, 'layers')
        for layer in np.array(obj.layers, ndmin=1):
            subsubelement = etree.SubElement(subelement, 'layer')
            indexes = sorted(map(materials_lookup.get,
                                 np.array(layer.material, ndmin=1)))
            self._convert_numerical_parameter(subsubelement, indexes, 'material')
            self._convert_numerical_parameter(subsubelement, layer.thickness_m, 'thickness')

        return element

class VerticalLayersXMLHandler(_GeometryXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}verticalLayers'
    CLASS = VerticalLayers

    def parse(self, element):
        geo = _GeometryXMLHandler.parse(self, element)

        materials_lookup = self._parse_materials(element)

        subelement = element.find('left')
        if subelement is None:
            raise ValueError("Element 'left' not found")
        indexes = self._parse_numerical_parameter(subelement, 'material')
        left_material = list(map(materials_lookup.get, indexes))
        left_depth_m = self._parse_numerical_parameter(subelement, 'depth')

        subelement = element.find('right')
        if subelement is None:
            raise ValueError("Element 'right' not found")
        indexes = self._parse_numerical_parameter(subelement, 'material')
        right_material = list(map(materials_lookup.get, indexes))
        right_depth_m = self._parse_numerical_parameter(subelement, 'depth')

        obj = VerticalLayers(left_material, right_material, None,
                             geo.tilt_rad, geo.rotation_rad)

        obj.left_substrate.depth_m = left_depth_m
        obj.right_substrate.depth_m = right_depth_m

        subelement = element.find('layers')
        if subelement is None:
            raise ValueError("Element 'layers' not found")
        for subsubelement in subelement:
            indexes = self._parse_numerical_parameter(subsubelement, 'material')
            material = list(map(materials_lookup.get, indexes))
            thickness_m = self._parse_numerical_parameter(subsubelement, 'thickness')
            depth_m = self._parse_numerical_parameter(subsubelement, 'depth')
            obj.add_layer(material, thickness_m, depth_m)

        return obj

    def convert(self, obj):
        element = _GeometryXMLHandler.convert(self, obj)

        materials_lookup = self._convert_materials(element, obj.get_materials())

        subelement = etree.SubElement(element, 'left')
        indexes = sorted(map(materials_lookup.get,
                             np.array(obj.left_substrate.material, ndmin=1)))
        self._convert_numerical_parameter(subelement, indexes, 'material')
        self._convert_numerical_parameter(subelement, obj.left_substrate.depth_m, 'depth')

        subelement = etree.SubElement(element, 'right')
        indexes = sorted(map(materials_lookup.get,
                             np.array(obj.right_substrate.material, ndmin=1)))
        self._convert_numerical_parameter(subelement, indexes, 'material')
        self._convert_numerical_parameter(subelement, obj.right_substrate.depth_m, 'depth')

        subelement = etree.SubElement(element, 'layers')
        for layer in np.array(obj.layers, ndmin=1):
            subsubelement = etree.SubElement(subelement, 'layer')
            indexes = sorted(map(materials_lookup.get,
                                 np.array(layer.material, ndmin=1)))
            self._convert_numerical_parameter(subsubelement, indexes, 'material')
            self._convert_numerical_parameter(subsubelement, layer.thickness_m, 'thickness')
            self._convert_numerical_parameter(subsubelement, layer.depth_m, 'depth')

        return element

class SphereXMLHandler(_GeometryXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}sphere'
    CLASS = Sphere

    def parse(self, element):
        geo = _GeometryXMLHandler.parse(self, element)

        materials_lookup = self._parse_materials(element)

        subelement = element.find('body')
        if subelement is None:
            raise ValueError("Element 'body' not found")
        indexes = self._parse_numerical_parameter(subelement, 'material')
        material = list(map(materials_lookup.get, indexes))
        diameter_m = self._parse_numerical_parameter(subelement, 'diameter')

        return Sphere(material, diameter_m, geo.tilt_rad, geo.rotation_rad)

    def convert(self, obj):
        element = _GeometryXMLHandler.convert(self, obj)

        materials_lookup = self._convert_materials(element, obj.get_materials())

        subelement = etree.SubElement(element, 'body')
        indexes = sorted(map(materials_lookup.get,
                             np.array(obj.body.material, ndmin=1)))
        self._convert_numerical_parameter(subelement, indexes, 'material')
        self._convert_numerical_parameter(subelement, obj.body.diameter_m, 'diameter')

        return element