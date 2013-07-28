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
from pymontecarlo.input.expander import Expander

# Globals and constants variables.

class ConversionWarning(Warning):
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

    def __init__(self):
        self._expander = Expander()

    def _warn(self, *messages):
        message = ' '.join(messages)
        warnings.warn(message, ConversionWarning)

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
            self._warn("No options could be converted")

        return list_options

    def _expand(self, options):
        return self._expander.expand(options)

    def _convert_beam(self, options):
        clasz = options.beam.__class__
        if clasz not in self.BEAMS:
            self._warn("Cannot convert beam (%s)." % clasz.__name__,
                       "This options definition was removed.")
            return False

        return True

    def _convert_geometry(self, options):
        # Check class
        clasz = options.geometry.__class__
        if clasz not in self.GEOMETRIES:
            self._warn("Cannot convert geometry (%s)." % clasz.__name__,
                       "This options definition was removed.")
            return False

        # Calculate materials
        for material in options.geometry.get_materials():
            material.calculate()

        return True

    def _convert_detectors(self, options):
        for key in options.detectors.keys():
            detector = options.detectors[key]
            clasz = detector.__class__
            if clasz not in self.DETECTORS:
                options.detectors.pop(key)

                self._warn("Detector '%s' of type '%s' cannot be converted." % \
                           (key, clasz.__name__),
                           "It was removed")

        if not options.detectors:
            self._warn("No detectors in options.",
                       "This options definition was removed.")
            return False

        return True

    def _convert_limits(self, options):
        for limit in options.limits:
            clasz = limit.__class__
            if clasz not in self.LIMITS:
                options.limits.discard(limit)

                self._warn("Limit of type '%s' cannot be converted." % clasz.__name__,
                           "It was removed")

        if not options.limits:
            self._warn("No limits in options.",
                       "This options definition was removed.")
            return False

        return True

    def _convert_models(self, options):
        for model_type, default_model in self.DEFAULT_MODELS.iteritems():
            models = list(options.models.iterclass(model_type))

            # Add default model if model type is missing
            if not models:
                options.models.add(default_model)

                self._warn("Set default model (%s) for model type '%s'" % \
                           (default_model, model_type))

            # Check if model is allowable
            else:
                for model in models:
                    if model not in self.MODELS[model_type]:
                        options.models.discard(model) # not required
                        options.models.add(default_model)

                        self._warn("Model (%s) is not allowable." % model,
                                   "It is replaced by the default model (%s)." % default_model)

        # Remove extra model types
        for model in options.models:
            if model.type not in self.DEFAULT_MODELS:
                options.models.discard(model)

                self._warn("Unknown model type (%s) for this converter." % model.type,
                           "Model (%s) is removed." % model)

        return True

