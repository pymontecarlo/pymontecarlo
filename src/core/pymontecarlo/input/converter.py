#!/usr/bin/env python
"""
================================================================================
:mod:`converter` -- Base class for conversion of options
================================================================================

.. module:: converter
   :synopsis: Base class for conversion of options

.. inheritance-diagram:: pymontecarlo.input.converter

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
from pymontecarlo.input.parameter import expand

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
    
        * :attr:`BEAM`: list of allowable beam classes
        * :attr:`GEOMETRIES`: list of allowable geometry classes
        * :attr:`DETECTORS`: list of allowable detector classes
        * :attr:`LIMITS`: list of allowable limit classes
        * :attr:`MODELS`: dictionary of allowable models 
            (key: model type, value: list of allowable models)
        * :attr:`DEFAULT_MODELS`: dictionary of default models
            (key: model type, value: default model)
            
    .. note::
    
       The keys for :attr:`MODELS` and :attr:`DEFAULT_MODELS` have to be the same.
    """

    BEAMS = []
    GEOMETRIES = []
    DETECTORS = []
    LIMITS = []
    MODELS = {}
    DEFAULT_MODELS = {}

    def convert(self, options):
        """
        Performs two tasks:
        
          1. Expand the options to create single options that the Monte Carlo
             program can run
          2. Converts the beam, geometry, detectors and limits to be compatible
             with the Monte Carlo program.
             
        This method may raise :exc:`ConversionException` if some parameters
        cannot be converted.
        If a parameter is modified or removed during the conversion, a
        :class:`ConversionWarning` is issued.
        If no conversion is required, the parameter (and its object) are left
        intact.
        
        This method returns a list of options, corresponding to the expanded
        options.
        
        :arg options: options
        """
        list_options = []
        
        for options in self._expand(options):
            if not self._convert_beam(options): continue
            if not self._convert_geometry(options): continue
            if not self._convert_detectors(options): continue
            if not self._convert_limits(options): continue
            if not self._convert_models(options): continue

            list_options.append(options)

        if not list_options:
            warnings.warn("No options could be converted", ConversionWarning)

        return list_options

    def _expand(self, options):
        return expand(options)

    def _convert_beam(self, options):
        clasz = options.beam.__class__
        if clasz not in self.BEAMS:
            message = "Cannot convert beam (%s). This options definition was removed." % \
                clasz.__name__
            warnings.warn(message, ConversionWarning)
            return False

        return True

    def _convert_geometry(self, options):
        # Check class
        clasz = options.geometry.__class__
        if clasz not in self.GEOMETRIES:
            message = "Cannot convert geometry (%s). This options definition was removed." % \
                clasz.__name__
            warnings.warn(message, ConversionWarning)
            return False

        # Calculate materials
        for material in options.geometry.get_materials():
            material.calculate()

        return True

    def _convert_detectors(self, options):
        for key in options.detectors.keys():
            detector = options.detectors[key]
            if detector.__class__ not in self.DETECTORS:
                options.detectors.pop(key)

                message = "Detector '%s' of type '%s' cannot be converted. It was removed" % \
                    (key, detector.__class__.__name__)
                warnings.warn(message, ConversionWarning)

        if not options.detectors:
            message = "No detectors in options. This options definition was removed."
            warnings.warn(message, ConversionWarning)
            return False

        return True

    def _convert_limits(self, options):
        for limit in options.limits:
            if limit.__class__ not in self.LIMITS:
                options.limits.discard(limit)

                message = "Limit of type '%s' cannot be converted. It was removed" % \
                    (limit.__class__.__name__)
                warnings.warn(message, ConversionWarning)

        if not options.limits:
            message = "No limits in options. This options definition was removed."
            warnings.warn(message, ConversionWarning)
            return False

        return True

    def _convert_models(self, options):
        for model_type, default_model in self.DEFAULT_MODELS.iteritems():
            models = list(options.models.iterclass(model_type))

            # Add default model if model type is missing
            if not models:
                options.models.add(default_model)

                message = "Set default model (%s) for model type '%s'" % \
                    (default_model, model_type)
                warnings.warn(message, ConversionWarning)

            # Check if model is allowable
            else:
                for model in models:
                    if model not in self.MODELS[model_type]:
                        options.models.discard(model) # not required
                        options.models.add(default_model)

                        message = "Model (%s) is not allowable. It is replaced by the default model (%s)." % \
                            (model, default_model)
                        warnings.warn(message, ConversionWarning)

        # Remove extra model types
        for model in options.models:
            if model.type not in self.DEFAULT_MODELS:
                options.models.discard(model)

                message = "Unknown model type (%s) for this converter. Model (%s) is removed." % \
                    (model.type, model)
                warnings.warn(message, ConversionWarning)

        return True

