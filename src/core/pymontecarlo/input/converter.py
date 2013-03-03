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
        Converts the beam, geometry, detectors and limits to be compatible
        with the Monte Carlo program.
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
        self._convert_models(options)

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

    def _convert_models(self, options):
        for model_type, default_model in self.DEFAULT_MODELS.iteritems():
            model = options.models.find(model_type)

            # Add default model if model type is missing
            if model is None:
                options.models.add(default_model)

                message = "Set default model (%s) for model type '%s'" % \
                    (default_model, model_type)
                warnings.warn(message, ConversionWarning)

            # Check if model is allowable
            else:
                if model not in self.MODELS[model_type]:
                    options.models.discard(model) # not required
                    options.models.add(default_model)

                    message = "Model (%s) is not allowable. It is replaced by the default model (%s)." % \
                        (model, default_model)
                    warnings.warn(message, ConversionWarning)

        # Remove extra model types
        for model_type, model in options.models.items():
            if model_type not in self.DEFAULT_MODELS:
                options.models.discard(model)

                message = "Unknown model type (%s) for this converter. Model (%s) is removed." % \
                    (model_type, model)
                warnings.warn(message, ConversionWarning)

class PassConverter(Converter):
    """
    Converter that allows any beam, geometry, detector, limit and models.
    """

    def _convert_beam(self, options):
        pass

    def _convert_geometry(self, options):
        pass

    def _convert_detectors(self, options):
        pass

    def _convert_limits(self, options):
        pass

    def _convert_models(self, options):
        pass
