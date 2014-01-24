#!/usr/bin/env python
"""
================================================================================
:mod:`material` -- XML handler for material
================================================================================

.. module:: material
   :synopsis: XML handler for material

.. inheritance-diagram:: pymontecarlo.fileformat.options.material

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
from pymontecarlo.options.material import Material, VACUUM, _Vacuum
from pymontecarlo.options.particle import PARTICLES

# Globals and constants variables.
_PARTICLES_LOOKUP = dict(zip(map(str, PARTICLES), PARTICLES))

class MaterialXMLHandler(_XMLHandler):

    TAG = '{http://pymontecarlo.sf.net}material'
    CLASS = Material

    def parse(self, element):
        composition = {}
        subelement = element.find('composition')
        if subelement is None:
            raise ValueError("Element 'composition' not found")
        for subsubelement in subelement.iter('element'):
            wf = float(subsubelement.get('weightFraction'))
            z = int(subsubelement.get('z'))
            composition[z] = wf

        name = element.get('name')

        density_kg_m3 = float(element.get('density'))

        absorption_energy_eV = {}
        for subelement in element.iter('absorptionEnergy'):
            particle = _PARTICLES_LOOKUP[subelement.get('particle')]
            energy_eV = float(subelement.text)
            absorption_energy_eV[particle] = energy_eV

        return Material(composition, name, density_kg_m3, absorption_energy_eV)

    def convert(self, obj):
        element = _XMLHandler.convert(self, obj)

        subelement = etree.SubElement(element, 'composition')
        for z, wf in obj.composition.items():
            subsubelement = etree.SubElement(subelement, 'element')
            subsubelement.set('z', str(z))
            subsubelement.set('weightFraction', str(wf))

        element.set('name', obj.name)

        element.set('density', str(obj.density_kg_m3))

        for particle, energy_eV in obj.absorption_energy_eV.items():
            subelement = etree.SubElement(element, 'absorptionEnergy')
            subelement.set('particle', str(particle))
            subelement.text = str(energy_eV)

        return element

class VACUUMXMLHandler(_XMLHandler):

    TAG = '{http://pymontecarlo.sf.net}vacuum'
    CLASS = _Vacuum

    def parse(self, element):
        return VACUUM

    def convert(self, obj):
        return _XMLHandler.convert(self, obj)
