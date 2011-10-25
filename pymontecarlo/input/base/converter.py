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
import copy
import warnings

# Third party modules.

# Local modules.

# Globals and constants variables.
dc = copy.deepcopy

class ConversionWarning(Warning):
    pass

class ConversionException(Exception):
    pass

class Converter(object):
    def convert(self, old):
        new = self._create_instance(old)

        self._convert_beam(old, new)
        self._convert_geometry(old, new)
        self._convert_detectors(old, new)
        self._convert_limits(old, new)

        return new

    def _create_instance(self, old):
        raise NotImplementedError

    def _convert_beam(self, old, new):
        if old.beam.__class__ in new.BEAMS:
            new.beam = dc(old.beam)
        else:
            raise ConversionException, "Cannot convert beam"

    def _convert_geometry(self, old, new):
        if old.geometry.__class__ in new.GEOMETRIES:
            new.geometry = dc(old.geometry)
        else:
            raise ConversionException, "Cannot convert geometry"

    def _convert_detectors(self, old, new):
        for key, detector in old.detectors.iteritems():
            if detector.__class__ in new.DETECTORS:
                new.detectors[key] = dc(detector)
            else:
                message = "Detector '%s' of type '%s' was removed" % \
                    (key, detector.__class__.__name__)
                warnings.warn(message, ConversionWarning)

    def _convert_limits(self, old, new):
        for limit in old.limits:
            if limit.__class__ in new.LIMITS:
                new.limits.add(limit)
            else:
                message = "Limit of type '%s' was removed" % \
                    (limit.__class__.__name__)
                warnings.warn(message, ConversionWarning)
