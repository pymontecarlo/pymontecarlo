#!/usr/bin/env python
"""
================================================================================
:mod:`results` -- HDF5 handler for results
================================================================================

.. module:: results
   :synopsis: HDF5 handler for results

.. inheritance-diagram:: pymontecarlo.fileformat.results.results

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from io import BytesIO
import xml.etree.ElementTree as etree
import logging

# Third party modules.
import h5py
import numpy as np

# Local modules.
from pymontecarlo.fileformat.handler import \
    find_convert_handler, find_parse_handler
from pymontecarlo.fileformat.options.options import OptionsReader, OptionsWriter

from pymontecarlo.results.results import Results

from pymontecarlo.util.monitorable import _MonitorableThread, _Monitorable

# Globals and constants variables.
VERSION = b'7'

def append(results, filepath):
    with h5py.File(filepath, 'r+') as hdf5file:
        # Check UUID of base options
        source = BytesIO(hdf5file.attrs['options'])
        reader = OptionsReader()
        reader.read(source)
        options = reader.get()

        if options.uuid != results.options.uuid:
            raise ValueError('UUID of base options do not match: %s != %s' % \
                             (options.uuid, results.options.uuid))

        # Save results
        identifiers = np.array(hdf5file.attrs['identifiers'], 'U').tolist()
        for container in results:
            identifier = container.options.uuid
            identifiers.append(identifier)

            group = hdf5file.create_group('result-' + identifier)

            # Save each result
            for key, result in container.items():
                subgroup = group.create_group(key)
                handler = find_convert_handler('pymontecarlo.fileformat.results.result',
                                               result, subgroup)
                handler.convert(result, subgroup)

            # Save options
            writer = OptionsWriter()
            writer.convert(container.options)
            element = writer.get()
            group.attrs['options'] = etree.tostring(element)

        # Update identifiers
        del hdf5file.attrs['identifiers']
        hdf5file.attrs.create('identifiers', identifiers,
                              dtype=h5py.special_dtype(vlen=str))

class _ResultsReaderThread(_MonitorableThread):

    def __init__(self, group):
        _MonitorableThread.__init__(self, args=(group,))

    def _run(self, group):
        try:
            self._update_status(0.1, "Check version")
            version = self._read_version(group)
            if version != VERSION:
                raise ValueError('Incompatible version: %s != %s' % \
                                 (version, VERSION))

            # Read results
            group_size = len(group)

            list_results = {}
            for i, item in enumerate(group.items()):
                self._update_status(i / group_size * 0.9, 'Reading results %i' % i)
                identifier, subgroup = item
                identifier = identifier[7:] # Remove "result-"

                # Options
                self._update_status(i / group_size * 0.9, 'Reading options')
                options = self._read_options(subgroup)
                assert identifier == options.uuid

                # Load each result
                subgroup_size = len(subgroup)

                results = {}
                for j, item in enumerate(subgroup.items()):
                    key, subsubgroup = item

                    self._update_status(i / group_size * 0.9 + j / subgroup_size * 0.1,
                                        'Loading %s' % key)

                    logging.debug('Parsing %s (%s) result of %s',
                                  key, subsubgroup.attrs['_class'], identifier)
                    results[key] = self._read_result(subsubgroup)

                # Results
                list_results[identifier] = (options, results)

            identifiers = np.array(group.attrs['identifiers'], 'U')
            if len(identifiers) != len(list_results):
                raise ValueError('Number of identifiers do not match number of results')

            list_results = [list_results[identifier] for identifier in identifiers]

            # Read options
            self._update_status(0.9, 'Reading base options')
            options = self._read_options(group)

            return Results(options, list_results)
        finally:
            if hasattr(group, 'close'):
                group.close()

    def _read_version(self, group):
        return group.attrs['version']

    def _read_options(self, group):
        source = BytesIO(group.attrs['options'])
        element = etree.parse(source).getroot()

        reader = OptionsReader()
        reader.parse(element)
        return reader.get()

    def _read_result(self, group):
        handler = find_parse_handler('pymontecarlo.fileformat.results.result', group)
        return handler.parse(group)

class ResultsReader(_Monitorable):

    def _create_thread(self, group, *args, **kwargs):
        return _ResultsReaderThread(group)

    def can_read(self, filepath):
        with h5py.File(filepath, 'r') as group:
            return self.can_parse(group)

    def can_parse(self, group):
        return group.attrs['_class'] == np.string_(Results.__name__) #@UndefinedVariable

    def read(self, filepath):
        self.parse(h5py.File(filepath, 'r'))

    def parse(self, group):
        self._start(group)

class _ResultsWriterThread(_MonitorableThread):

    def __init__(self, results, group, close=False):
        _MonitorableThread.__init__(self, args=(results, group, close))

    def _run(self, results, group, close):
        try:
            self._update_status(0.03, 'Write class')
            self._write_class(results, group)

            self._update_status(0.06, 'Write version')
            self._write_version(results, group)

            # Save results
            results_size = len(results)

            identifiers = []
            for i, container in enumerate(results):
                self._update_status(i / results_size * 0.8 + 0.1,
                                    'Saving results %i' % i)

                identifier = container.options.uuid
                identifiers.append(identifier)

                subgroup = group.create_group('result-' + identifier)

                # Save each result
                container_size = len(container)

                for j, item in enumerate(container.items()):
                    key, result = item

                    self._update_status(i / results_size * 0.8 + 0.1 + j / container_size * 0.1,
                                        'Saving result %s' % key)

                    subsubgroup = subgroup.create_group(key)
                    self._write_result(result, subsubgroup)

                # Save options
                self._write_options(container.options, subgroup)

            group.attrs.create('identifiers', identifiers,
                               dtype=h5py.special_dtype(vlen=str))

            # Save options
            self._update_status(0.9, 'Saving options')
            self._write_options(results.options, group)

            return group
        finally:
            if hasattr(group, 'close') and close:
                group.close()

    def _write_class(self, results, group):
        group.attrs['_class'] = np.string_(results.__class__.__name__)

    def _write_version(self, results, group):
        group.attrs['version'] = VERSION

    def _write_options(self, options, group):
        writer = OptionsWriter()
        writer.convert(options)
        element = writer.get()
        group.attrs['options'] = etree.tostring(element)

    def _write_result(self, result, group):
        handler = find_convert_handler('pymontecarlo.fileformat.results.result', result)
        handler.convert(result, group)

class ResultsWriter(_Monitorable):

    def _create_thread(self, results, group, close=False, *args, **kwargs):
        return _ResultsWriterThread(results, group, close)

    def can_write(self, results):
        return self.can_convert(results)

    def can_convert(self, results):
        return type(results) is Results

    def write(self, results, filepath):
        group = h5py.File(filepath, 'w')
        self._start(results, group, True)

    def convert(self, results, group):
        self._start(results, group, False)
