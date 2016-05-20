#!/usr/bin/env python
"""
================================================================================
:mod:`beam` -- XML handler for beams
================================================================================

.. module:: beam
   :synopsis: XML handler for beams

.. inheritance-diagram:: pymontecarlo.fileformat.options.beam

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

# Local modules.
from pymontecarlo.fileformat.xmlhandler import _XMLHandler

from pymontecarlo.options.beam import PencilBeam, GaussianBeam, GaussianExpTailBeam
from pymontecarlo.options.particle import PARTICLES

# Globals and constants variables.
_PARTICLES_LOOKUP = dict(zip(map(str, PARTICLES), PARTICLES))

class PencilBeamXMLHandler(_XMLHandler):

    TAG = '{http://pymontecarlo.sf.net}pencilBeam'
    CLASS = PencilBeam

    def parse(self, element):
        energy_eV = self._parse_numerical_parameter(element, 'energy')
        particle = list(map(_PARTICLES_LOOKUP.get,
                            self._parse_text_parameter(element, 'particle')))

        subelement = element.find('origin')
        if subelement is None:
            raise ValueError("Element 'origin' not found")
        origin_x = self._parse_numerical_parameter(subelement, 'x')
        origin_y = self._parse_numerical_parameter(subelement, 'y')
        origin_z = self._parse_numerical_parameter(subelement, 'z')
        origin_m = list(zip(origin_x, origin_y, origin_z))

        subelement = element.find('direction')
        if subelement is None:
            raise ValueError("Element 'direction' not found")
        direction_u = self._parse_numerical_parameter(subelement, 'u')
        direction_v = self._parse_numerical_parameter(subelement, 'v')
        direction_w = self._parse_numerical_parameter(subelement, 'w')
        direction = list(zip(direction_u, direction_v, direction_w))

        aperture_rad = self._parse_numerical_parameter(element, 'aperture')

        return PencilBeam(energy_eV, particle, origin_m, direction, aperture_rad)

    def convert(self, obj):
        element = _XMLHandler.convert(self, obj)

        self._convert_numerical_parameter(element, obj.energy_eV, 'energy')
        self._convert_text_parameter(element, obj.particle, 'particle')

        subelement = etree.SubElement(element, 'origin')
        self._convert_numerical_parameter(subelement, obj.origin_m.x, 'x')
        self._convert_numerical_parameter(subelement, obj.origin_m.y, 'y')
        self._convert_numerical_parameter(subelement, obj.origin_m.z, 'z')

        subelement = etree.SubElement(element, 'direction')
        self._convert_numerical_parameter(subelement, obj.direction.u, 'u')
        self._convert_numerical_parameter(subelement, obj.direction.v, 'v')
        self._convert_numerical_parameter(subelement, obj.direction.w, 'w')

        self._convert_numerical_parameter(element, obj.aperture_rad, 'aperture')

        return element

class GaussianBeamXMLHandler(PencilBeamXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}gaussianBeam'
    CLASS = GaussianBeam

    def parse(self, element):
        beam = PencilBeamXMLHandler.parse(self, element)

        diameter_m = self._parse_numerical_parameter(element, 'diameter')

        return GaussianBeam(beam.energy_eV, diameter_m, beam.particle,
                            beam.origin_m, beam.direction, beam.aperture_rad)

    def convert(self, obj):
        element = PencilBeamXMLHandler.convert(self, obj)

        self._convert_numerical_parameter(element, obj.diameter_m, 'diameter')

        return element

class GaussianExpTailBeamXMLHandler(PencilBeamXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}gaussianExpTailBeam'
    CLASS = GaussianExpTailBeam

    def parse(self, element):
        beam = GaussianBeamXMLHandler.parse(self, element)

        skirt_threshold = self._parse_numerical_parameter(element, 'skirtThreshold')
        skirt_factor = self._parse_numerical_parameter(element, 'skirtFactor')

        return GaussianExpTailBeam(beam.energy_eV, beam.diameter_m,
                                   skirt_threshold, skirt_factor,
                                   beam.particle,
                                   beam.origin_m, beam.direction, beam.aperture_rad)

    def convert(self, obj):
        element = GaussianBeamXMLHandler.convert(self, obj)

        self._convert_numerical_parameter(element, obj.skirt_threshold, 'skirtThreshold')
        self._convert_numerical_parameter(element, obj.skirt_factor, 'skirtFactor')

        return element
