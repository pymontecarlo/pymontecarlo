#!/usr/bin/env python
"""
================================================================================
:mod:`exporter` -- Base class for exporters
================================================================================

.. module:: exporter
   :synopsis: Base class for exporters

.. inheritance-diagram:: pymontecarlo.io.exporter

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.

# Globals and constants variables.

class ExporterWarning(Warning):
    pass

class ExporterException(Exception):
    pass

class Exporter(object):

    def __init__(self):
        self._beam_exporters = {}
        self._geometry_exporters = {}
        self._detector_exporters = {}
        self._limit_exporters = {}
        self._model_exporters = {}

    def _export(self, options, *args):
        self._export_beam(options, *args)
        self._export_geometry(options, *args)
        self._export_detectors(options, *args)
        self._export_limits(options, *args)
        self._export_models(options, *args)

    def _export_beam(self, options, *args):
        clasz = options.beam.__class__
        method = self._beam_exporters.get(clasz)

        if method:
            method(options, options.beam, *args)
        else:
            raise ExporterException, "Could not export beam '%s'" % clasz.__name__

    def _export_geometry(self, options, *args):
        clasz = options.geometry.__class__
        method = self._geometry_exporters.get(clasz)

        if method:
            method(options, options.geometry, *args)
        else:
            raise ExporterException, "Could not export geometry '%s'" % clasz.__name__

    def _export_detectors(self, options, *args):
        for name, detector in options.detectors.iteritems():
            clasz = detector.__class__
            method = self._detector_exporters.get(clasz)

            if method:
                method(options, name, detector, *args)
            else:
                raise ExporterException, \
                    "Could not export detector '%s' (%s)" % (name, clasz.__name__)

    def _export_limits(self, options, *args):
        for limit in options.limits:
            clasz = limit.__class__
            method = self._limit_exporters.get(clasz)

            if method:
                method(options, limit, *args)
            else:
                raise ExporterException, \
                    "Could not export limit '%s'" % clasz.__name__

    def _export_models(self, options, *args):
        for model in options.models:
            type = model.type
            method = self._model_exporters.get(type)

            if method:
                method(options, model, *args)
            else:
                raise ExporterException, \
                    "Could not export model of type '%s'" % type.name
