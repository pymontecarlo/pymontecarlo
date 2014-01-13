#!/usr/bin/env python
"""
================================================================================
:mod:`exporter` -- Base class for exporters
================================================================================

.. module:: exporter
   :synopsis: Base class for exporters

.. inheritance-diagram:: pymontecarlo.input.exporter

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
from abc import ABCMeta, abstractmethod
from xml.etree import ElementTree
import xml.dom.minidom as minidom

# Third party modules.

# Local modules.
from pymontecarlo.options.expander import Expander
from pymontecarlo.options.xmlmapper import mapper

# Globals and constants variables.

class ExporterWarning(Warning):
    pass

class ExporterException(Exception):
    pass

class Exporter(object):
    """
    Base class for all exporters.
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        self._expander = Expander()

        self._beam_exporters = {}
        self._geometry_exporters = {}
        self._detector_exporters = {}
        self._limit_exporters = {}
        self._model_exporters = {}

    def export(self, options, dirpath, *args, **kwargs):
        """
        Exports options to a file inside the specified output directory.
        Returns the filepath of the exported options.

        :arg options: options to export
            The options must only contained a single value for each parameter.
        :arg dirpath: full path to output directory
        """
        if self._expander.is_expandable(options):
            raise ValueError, "Only options with singular value can be exported"

        return self._export(options, dirpath, *args, **kwargs)

    @abstractmethod
    def _export(self, options, dirpath, *args, **kwargs):
        """
        Performs the actual export.
        """
        raise NotImplementedError

    def _run_exporters(self, options, *args, **kwargs):
        """
        Internal command to call the register export functions.
        """
        self._export_beam(options, *args, **kwargs)
        self._export_geometry(options, *args, **kwargs)
        self._export_detectors(options, *args, **kwargs)
        self._export_limits(options, *args, **kwargs)
        self._export_models(options, *args, **kwargs)

    def _export_beam(self, options, *args, **kwargs):
        """
        Exports the beam.
        If a exporter function is defined, it calls this function with the
        following arguments:

            * options object
            * beam object
            * optional arguments and keyword-arguments
        """
        clasz = options.beam.__class__
        method = self._beam_exporters.get(clasz)

        if not method:
            raise ExporterException, "Could not export beam '%s'" % clasz.__name__

        method(options, options.beam, *args, **kwargs)

    def _export_geometry(self, options, *args, **kwargs):
        """
        Exports the geometry.
        If a exporter function is defined, it calls this function with the
        following arguments:

            * options object
            * geometry object
            * optional arguments and keyword-arguments
        """
        clasz = options.geometry.__class__
        method = self._geometry_exporters.get(clasz)

        if method:
            method(options, options.geometry, *args, **kwargs)
        else:
            raise ExporterException, "Could not export geometry '%s'" % clasz.__name__

    def _export_detectors(self, options, *args, **kwargs):
        """
        Exports the detectors.
        If a exporter function is defined, it calls this function with the
        following arguments for each detector:

            * options object
            * name/key of detector
            * detector object
            * optional arguments and keyword-arguments
        """
        for name, detector in options.detectors.iteritems():
            clasz = detector.__class__
            method = self._detector_exporters.get(clasz)

            if not method:
                raise ExporterException, \
                    "Could not export detector '%s' (%s)" % (name, clasz.__name__)

            method(options, name, detector, *args, **kwargs)

    def _export_limits(self, options, *args, **kwargs):
        """
        Exports the limit.
        If a exporter function is defined, it calls this function with the
        following arguments for each limit:

            * options object
            * limit object
            * optional arguments and keyword-arguments
        """
        for limit in options.limits:
            clasz = limit.__class__
            method = self._limit_exporters.get(clasz)

            if not method:
                raise ExporterException, \
                    "Could not export limit '%s'" % clasz.__name__

            method(options, limit, *args, **kwargs)

    def _export_models(self, options, *args, **kwargs):
        """
        Exports the models.
        If a exporter function is defined, it calls this function with the
        following arguments for each model:

            * options object
            * model object
            * optional arguments and keyword-arguments
        """
        for model in options.models:
            type_ = model.type
            method = self._model_exporters.get(type_)

            if not method:
                raise ExporterException, \
                    "Could not export model of type '%s'" % type_.name

            method(options, model, *args, **kwargs)

class XMLExporter(Exporter):
    """
    Exports the options to a XML file.
    """

    def _export(self, options, dirpath, *args, **kwargs):
        element = mapper.to_xml(options)

        encoding = kwargs.get('encoding', 'UTF-8')
        pretty_print = kwargs.get('pretty_print', True)

        output = ElementTree.tostring(element, encoding=encoding)
        if pretty_print:
            output = minidom.parseString(output).toprettyxml(encoding=encoding)

        filepath = os.path.join(dirpath, options.name + '.xml')
        with open(filepath, 'w') as fp:
            fp.write(output)

        return filepath


