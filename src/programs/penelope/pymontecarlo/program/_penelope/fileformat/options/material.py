#!/usr/bin/env python
"""
================================================================================
:mod:`material` -- XML handler for material
================================================================================

.. module:: material
   :synopsis: XML handler for material

.. inheritance-diagram:: pymontecarlo.program._penelope.fileformat.options.material

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
from pymontecarlo.fileformat.options.material import \
    MaterialXMLHandler as _MaterialXMLHandler
from pymontecarlo.program._penelope.options.material import \
    Material, InteractionForcing

# Globals and constants variables.
from pymontecarlo.options.particle import PARTICLES
_PARTICLES_LOOKUP = dict(zip(map(str, PARTICLES), PARTICLES))
from pymontecarlo.options.collision import COLLISIONS
_COLLISIONS_LOOKUP = dict(zip(map(str, COLLISIONS), COLLISIONS))

class MaterialXMLHandler(_MaterialXMLHandler):

    TAG = '{http://pymontecarlo.sf.net/penelope}material'
    CLASS = Material

    def parse(self, element):
        mat = _MaterialXMLHandler.parse(self, element)

        elastic_scattering = (float(element.get('c1')), float(element.get('c2')))
        cutoff_energy_inelastic_eV = float(element.get('wcc'))
        cutoff_energy_bremsstrahlung_eV = float(element.get('wcr'))

        interaction_forcings = []
        for subelement in element.findall('interactionForcing'):
            particle = _PARTICLES_LOOKUP[subelement.get('particle')]
            collision = _COLLISIONS_LOOKUP[subelement.get('collision')]
            forcer = float(subelement.get('forcer'))
            weight = (float(subelement.get('wlow')),
                      float(subelement.get('whigh')))
            interaction_forcings.append(InteractionForcing(particle, collision,
                                                           forcer, weight))

        maximum_step_length_m = float(element.get('dsmax'))

        return Material(mat.composition, mat.name, mat.density_kg_m3,
                        mat.absorption_energy_eV, elastic_scattering,
                        cutoff_energy_inelastic_eV,
                        cutoff_energy_bremsstrahlung_eV,
                        interaction_forcings, maximum_step_length_m)

    def convert(self, obj):
        element = _MaterialXMLHandler.convert(self, obj)

        element.set('c1', str(obj.elastic_scattering.c1))
        element.set('c2', str(obj.elastic_scattering.c2))
        element.set('wcc', str(obj.cutoff_energy_inelastic_eV))
        element.set('wcr', str(obj.cutoff_energy_bremsstrahlung_eV))

        for intforce in obj.interaction_forcings:
            subelement = etree.SubElement(element, 'interactionForcing')
            subelement.set('particle', str(intforce.particle))
            subelement.set('collision', str(intforce.collision))
            subelement.set('forcer', str(intforce.forcer))
            subelement.set('wlow', str(intforce.weight[0]))
            subelement.set('whigh', str(intforce.weight[1]))

        element.set('dsmax', str(obj.maximum_step_length_m))

        return element
