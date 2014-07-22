#!/usr/bin/env python
"""
================================================================================
:mod:`model` -- XML handler for models
================================================================================

.. module:: model
   :synopsis: XML handler for models

.. inheritance-diagram:: pymontecarlo.fileformat.options.model

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
from pyxray.transition import Transition

# Local modules.
from pymontecarlo.fileformat.xmlhandler import _XMLHandler

from pymontecarlo.options.model import \
    _Model, RegisteredModel, ModelType, UserDefinedMassAbsorptionCoefficientModel

# Globals and constants variables.

class _ModelXMLHandler(_XMLHandler):

    TAG = '{http://pymontecarlo.sf.net}_model'
    CLASS = _Model

    def parse(self, element):
        name = element.get('name')
        type_ = ModelType(element.get('type'))
        reference = element.get('reference', '')
        return _Model(type_, name, reference)

    def convert(self, obj):
        element = _XMLHandler.convert(self, obj)

        element.set('name', str(obj.name))
        element.set('type', str(obj.type))
        element.set('reference', str(obj.reference))

        return element

class RegisteredModelXMLHandler(_ModelXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}model'
    CLASS = RegisteredModel

    def parse(self, element):
        tmpmodel = _ModelXMLHandler.parse(self, element)
        return RegisteredModel(tmpmodel.type, tmpmodel.name)

class UserDefinedMassAbsorptionCoefficientModelXMLHandler(_ModelXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}userDefinedMassAbsorptionCoefficientModel'
    CLASS = UserDefinedMassAbsorptionCoefficientModel

    def parse(self, element):
        tmpmodel = _ModelXMLHandler.parse(self, element)

        subelement = element.find('{http://pymontecarlo.sf.net}model')
        if subelement is None:
            raise ValueError("Element 'model' not found")
        base_model = self._parse_handlers('pymontecarlo.fileformat.options.model', subelement)

        model = UserDefinedMassAbsorptionCoefficientModel(base_model,
                                                          tmpmodel.reference)

        for subelement in element.iter('mac'):
            absorber = int(subelement.get('absorber'))

            if 'energy' in subelement.attrib:
                energy_or_transition = float(subelement.get('energy'))
            else:
                z = int(subelement.get('z'))
                src = int(subelement.get('src'))
                dest = int(subelement.get('dest'))
                energy_or_transition = Transition(z, src, dest)

            mac_m2_kg = float(subelement.text)
            model.add(absorber, energy_or_transition, mac_m2_kg)

        return model

    def convert(self, obj):
        element = _ModelXMLHandler.convert(self, obj)

        subelement = self._convert_handlers('pymontecarlo.fileformat.options.model', obj.base_model)
        element.append(subelement)

        for key, value in obj.defined_macs.items():
            absorber, energy_or_transition = key

            subelement = etree.SubElement(element, 'mac')
            subelement.set('absorber', str(absorber))

            if isinstance(energy_or_transition, Transition):
                subelement.set('z', str(energy_or_transition.z))
                subelement.set('src', str(energy_or_transition.src.index))
                subelement.set('dest', str(energy_or_transition.dest.index))
            else:
                subelement.set('energy', str(energy_or_transition))

            subelement.text = str(value)

        return element
