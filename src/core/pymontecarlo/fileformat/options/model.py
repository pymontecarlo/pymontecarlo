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

# Third party modules.

# Local modules.
from pymontecarlo.fileformat.xmlhandler import _XMLHandler

from pymontecarlo.options.model import Model, ModelType

# Globals and constants variables.

class ModelXMLHandler(_XMLHandler):

    TAG = '{http://pymontecarlo.sf.net}model'
    CLASS = Model

    def parse(self, element):
        name = element.get('name')
        type_ = ModelType(element.get('type'))
        return Model(type_, name)

    def convert(self, obj):
        element = _XMLHandler.convert(self, obj)

        element.set('name', str(obj.name))
        element.set('type', str(obj.type))

        return element

