#!/usr/bin/env python
"""
================================================================================
:mod:`options` -- XML handler for options
================================================================================

.. module:: options
   :synopsis: XML handler for options

.. inheritance-diagram:: pymontecarlo.fileformat.options.options

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
import numpy as np

# Local modules.
from pymontecarlo.fileformat.handler import \
    find_convert_handler, find_parse_handler

from pymontecarlo.options.options import Options

import pymontecarlo.util.xmlutil as xmlutil
from pymontecarlo.util.monitorable import _MonitorableThread, _Monitorable

# Globals and constants variables.
VERSION = '6'

class _OptionsReaderThread(_MonitorableThread):

    def __init__(self, element):
        _MonitorableThread.__init__(self, args=(element,))

    def _run(self, element):
        self._update_status(0.1, "Check version")
        version = self._read_version(element)
        if version != VERSION:
            raise ValueError('Incompatible version: %s != %s' % \
                             (version, VERSION))

        self._update_status(0.13, "Reading name")
        name = self._read_name(element)
        options = Options(name)

        self._update_status(0.16, "Reading UUID")
        options._uuid = self._read_uuid(element)

        self._update_status(0.2, "Reading programs")
        options.programs.update(self._read_programs(element))

        self._update_status(0.3, "Reading beams")
        options.beam = self._read_beams(element)

        self._update_status(0.4, "Reading geometries")
        options.geometry = self._read_geometries(element)

        self._update_status(0.6, "Reading detectors")
        options.detectors.update(self._read_detectors(element))

        self._update_status(0.8, "Reading limits")
        options.limits.update(self._read_limits(element))

        self._update_status(0.9, "Reading models")
        options.models.update(self._read_models(element))

        return options

    def _read_version(self, element):
        return element.attrib['version']

    def _read_name(self, element):
        return element.attrib['name']

    def _read_uuid(self, element):
        return element.attrib['uuid']

    def _read_programs(self, element):
        subelement = element.find('programs')
        if subelement is None:
            return set()

        programs = set()
        for subsubelement in subelement:
            programs.add(subsubelement.text)

        return programs

    def _read_beams(self, element):
        subelement = element.find('beam')
        if subelement is None:
            return []

        beams = []
        for subsubelement in subelement:
            handler = find_parse_handler('pymontecarlo.fileformat.options.beam', subsubelement)
            beams.append(handler.parse(subsubelement))

        return beams

    def _read_geometries(self, element):
        subelement = element.find('geometry')
        if subelement is None:
            return []

        geometries = []
        for subsubelement in subelement:
            handler = find_parse_handler('pymontecarlo.fileformat.options.geometry', subsubelement)
            geometries.append(handler.parse(subsubelement))

        return geometries

    def _read_detectors(self, element):
        subelement = element.find('detectors')
        if subelement is None:
            return {}

        detectors = {}
        for subsubelement in subelement:
            key = subsubelement.attrib['_key']
            handler = find_parse_handler('pymontecarlo.fileformat.options.detector', subsubelement)
            detector = handler.parse(subsubelement)
            detectors.setdefault(key, []).append(detector)

        return detectors

    def _read_limits(self, element):
        subelement = element.find('limits')
        if subelement is None:
            return set()

        limits = set()
        for subsubelement in subelement:
            handler = find_parse_handler('pymontecarlo.fileformat.options.limit', subsubelement)
            limits.add(handler.parse(subsubelement))

        return limits

    def _read_models(self, element):
        subelement = element.find('models')
        if subelement is None:
            return set()

        models = set()
        for subsubelement in subelement:
            handler = find_parse_handler('pymontecarlo.fileformat.options.model', subsubelement)
            models.add(handler.parse(subsubelement))

        return models

class OptionsReader(_Monitorable):

    def _create_thread(self, element, *args, **kwargs):
        return _OptionsReaderThread(element)

    def can_read(self, filepath):
        element = xmlutil.parse(filepath)
        return self.can_parse(element)

    def can_parse(self, element):
        return element.tag == '{http://pymontecarlo.sf.net}options'

    def read(self, source):
        self.parse(xmlutil.parse(source))

    def parse(self, element):
        self._start(element)

class _OptionsWriterThread(_MonitorableThread):

    def __init__(self, options, source=None):
        _MonitorableThread.__init__(self, args=(options, source))

    def _run(self, options, source):
        element = etree.Element('{http://pymontecarlo.sf.net}options')

        self._update_status(0.1, "Writing version")
        self._write_version(options, element)

        self._update_status(0.13, "Writing name")
        self._write_name(options, element)

        self._update_status(0.16, "Writing UUID")
        self._write_uuid(options, element)

        self._update_status(0.2, "Writing programs")
        self._write_programs(options, element)

        self._update_status(0.3, "Writing beams")
        self._write_beams(options, element)

        self._update_status(0.4, "Writing geometries")
        self._write_geometries(options, element)

        self._update_status(0.6, "Writing detectors")
        self._write_detectors(options, element)

        self._update_status(0.8, "Writing limits")
        self._write_limits(options, element)

        self._update_status(0.9, "Writing models")
        self._write_models(options, element)

        if source is None:
            return element

        self_opened = False
        if not hasattr(source, "write"):
            source = open(source, "wb")
            self_opened = True
        source.write(xmlutil.tostring(element))
        if self_opened: source.close()
        return source

    def _write_version(self, options, element):
        element.set('version', VERSION)

    def _write_name(self, options, element):
        element.set('name', options.name)

    def _write_uuid(self, options, element):
        element.set('uuid', options._uuid or 'xsi:nil')

    def _write_programs(self, options, element):
        subelement = etree.SubElement(element, 'programs')
        for alias in options.programs.aliases():
            subsubelement = etree.SubElement(subelement, 'program')
            subsubelement.text = alias

    def _write_beams(self, options, element):
        subelement = etree.SubElement(element, 'beam')
        for beam in np.array(options.beam, ndmin=1):
            handler = find_convert_handler('pymontecarlo.fileformat.options.beam', beam)
            subelement.append(handler.convert(beam))

    def _write_geometries(self, options, element):
        subelement = etree.SubElement(element, 'geometry')
        for geometry in np.array(options.geometry, ndmin=1):
            handler = find_convert_handler('pymontecarlo.fileformat.options.geometry', geometry)
            subelement.append(handler.convert(geometry))

    def _write_detectors(self, options, element):
        subelement = etree.SubElement(element, 'detectors')
        for key, detectors in options.detectors.items():
            for detector in np.array(detectors, ndmin=1):
                handler = find_convert_handler('pymontecarlo.fileformat.options.detector', detector)
                subsubelement = handler.convert(detector)
                subsubelement.set('_key', key)
                subelement.append(subsubelement)

    def _write_limits(self, options, element):
        subelement = etree.SubElement(element, 'limits')
        for limit in options.limits:
            handler = find_convert_handler('pymontecarlo.fileformat.options.limit', limit)
            subelement.append(handler.convert(limit))

    def _write_models(self, options, element):
        subelement = etree.SubElement(element, 'models')
        for model in options.models:
            handler = find_convert_handler('pymontecarlo.fileformat.options.model', model)
            subelement.append(handler.convert(model))

class OptionsWriter(_Monitorable):

    def _create_thread(self, options, source=None, *args, **kwargs):
        return _OptionsWriterThread(options, source)

    def can_write(self, options, source):
        return self.can_convert(options)

    def can_convert(self, options):
        return type(options) is Options

    def write(self, options, source):
        self._start(options, source)

    def convert(self, options):
        self._start(options)
