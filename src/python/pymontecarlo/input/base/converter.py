#!/usr/bin/env python
"""
================================================================================
:mod:`converter` -- Base class for conversion of options
================================================================================

.. module:: converter
   :synopsis: Base class for conversion of options

.. inheritance-diagram:: pymontecarlo.input.base.converter

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import warnings

# Third party modules.

# Local modules.

# Globals and constants variables.

class ConversionWarning(Warning):
    pass

class ConversionException(Exception):
    pass

class Converter(object):
    """
    Base class of all converters.
    
    Derived class shall modify the following class variables to specify
    the allowable classes for each of these parameters:
    
        * :var:`BEAM`
        * :var:`GEOMETRIES`
        * :var:`DETECTORS`
        * :var:`LIMITS`
    """

    BEAMS = []
    GEOMETRIES = []
    DETECTORS = []
    LIMITS = []

    def convert(self, options):
        """
        Converts the beam, geometry, detectors and limits to be compatible
        with Casino2.
        This method may raise :exc:`ConversionException` if some parameters
        cannot be converted.
        If a parameter is modified or removed during the conversion, a
        :class:`ConversionWarning` is issued.
        If no conversion is required, the parameter (and its object) are left
        intact.
        
        :arg options: options
        """
        self._convert_beam(options)
        self._convert_geometry(options)
        self._convert_detectors(options)
        self._convert_limits(options)

    def _convert_beam(self, options):
        if options.beam.__class__ not in self.BEAMS:
            raise ConversionException, "Cannot convert beam"

    def _convert_geometry(self, options):
        if options.geometry.__class__ not in self.GEOMETRIES:
            raise ConversionException, "Cannot convert geometry"

    def _convert_detectors(self, options):
        for key in options.detectors.keys():
            detector = options.detectors[key]
            if detector.__class__ not in self.DETECTORS:
                options.detectors.pop(key)

                message = "Detector '%s' of type '%s' cannot be converted. It was removed" % \
                    (key, detector.__class__.__name__)
                warnings.warn(message, ConversionWarning)

    def _convert_limits(self, options):
        for limit in list(options.limits):
            if limit.__class__ not in self.LIMITS:
                options.limits.discard(limit)

                message = "Limit of type '%s' cannot be converted. It was removed" % \
                    (limit.__class__.__name__)
                warnings.warn(message, ConversionWarning)
