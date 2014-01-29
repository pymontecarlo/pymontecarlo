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
from pymontecarlo.fileformat.hdf5handler import _HDF5Handler
from pymontecarlo.fileformat.handler import \
    find_convert_handler, find_parse_handler

from pymontecarlo.results.results import Results

import pymontecarlo.util.progress as progress

# Globals and constants variables.

def load(filepath):
    with h5py.File(filepath, 'r') as hdf5file:
        handler = find_parse_handler('pymontecarlo.fileformat.results.results',
                                     hdf5file)
        return handler.parse(hdf5file)

def save(results, filepath):
    with h5py.File(filepath, 'w') as hdf5file:
        handler = find_convert_handler('pymontecarlo.fileformat.results.results',
                                       results, hdf5file)
        return handler.convert(results, hdf5file)

class ResultsHDF5Handler(_HDF5Handler):

    CLASS = Results
    VERSION = b'7'

    def parse(self, group):
        task = progress.start_task('Loading results')

        try:
            # Check version
            version = group.attrs['version']
            if version != self.VERSION:
                raise ValueError('Incompatible version: %s != %s' % \
                                 (version, self.VERSION))

            # Read results
            group_size = len(group)

            list_results = {}
            for i, item in enumerate(group.items()):
                task.status = 'Reading results %i' % i
                task.progress = i / group_size
                identifier, subgroup = item
                identifier = identifier[7:] # Remove "result-"

                # Options
                task.status = 'Reading options'
                source = BytesIO(subgroup.attrs['options'])
                element = etree.parse(source).getroot()
                options = self._parse_handlers('pymontecarlo.fileformat.options.options', element)

                assert identifier == options.uuid

                # Load each result
                subgroup_size = len(subgroup)

                results = {}
                for j, item in enumerate(subgroup.items()):
                    key, subsubgroup = item

                    task.status = 'Loading %s' % key
                    task.progress = i / group_size + j / subgroup_size * 0.1

                    logging.debug('Parsing %s (%s) result of %s',
                                  key, subsubgroup.attrs['_class'], identifier)
                    result = self._parse_handlers('pymontecarlo.fileformat.results.result',
                                                  subsubgroup)
                    results[key] = result

                # Results
                list_results[identifier] = (options, results)

            identifiers = np.array(group.attrs['identifiers'], 'U')
            if len(identifiers) != len(list_results):
                raise ValueError('Number of identifiers do not match number of results')

            list_results = [list_results[identifier] for identifier in identifiers]

            # Read options
            task.status = 'Reading base options'
            source = BytesIO(group.attrs['options'])
            element = etree.parse(source).getroot()
            options = self._parse_handlers('pymontecarlo.fileformat.options.options', element)

            return Results(options, list_results)
        finally:
            progress.stop_task(task)

    def convert(self, obj, group):
        group = _HDF5Handler.convert(self, obj, group)

        task = progress.start_task('Saving results')

        try:
            # Save version
            group.attrs['version'] = self.VERSION

            # Save results
            obj_size = len(obj)

            identifiers = []
            for i, results in enumerate(obj):
                task.status = 'Saving results %i' % i
                task.progress = i / obj_size

                identifier = results.options.uuid
                identifiers.append(identifier)

                subgroup = group.create_group('result-' + identifier)

                # Save each result
                results_size = len(results)

                for j, item in enumerate(results.items()):
                    key, result = item

                    task.status = 'Saving result %s' % key
                    task.progress = i / obj_size + j / results_size * 0.1

                    subsubgroup = subgroup.create_group(key)
                    self._convert_handlers('pymontecarlo.fileformat.results.result',
                                           result, subsubgroup)

                # Save options
                task.status = 'Saving options'
                element = self._convert_handlers('pymontecarlo.fileformat.options.options',
                                                 results.options)
                subgroup.attrs['options'] = etree.tostring(element)

            group.attrs.create('identifiers', identifiers,
                               dtype=h5py.special_dtype(vlen=str))

            # Save options
            task.status = 'Saving options'
            element = self._convert_handlers('pymontecarlo.fileformat.options.options',
                                             obj.options)
            group.attrs['options'] = etree.tostring(element)
        finally:
            progress.stop_task(task)

        return group

