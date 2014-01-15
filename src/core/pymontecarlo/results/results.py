#!/usr/bin/env python
"""
================================================================================
:mod:`results` -- Container of all results
================================================================================

.. module:: results
   :synopsis: Container of all results

.. inheritance-diagram:: pymontecarlo.output.results

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

__all__ = ['Results']

# Standard library modules.
import uuid
from collections import Mapping, Sequence
from io import BytesIO

# Third party modules.
import h5py

# Local modules.
from pymontecarlo.options.options import Options
from pymontecarlo.options.parameter import freeze
from pymontecarlo.results.manager import ResultManager
import pymontecarlo.results.result # @UnusedImport

import pymontecarlo.util.progress as progress

# Globals and constants variables.

class _ResultsContainer(Mapping):

    def __init__(self, options, results={}):
        """
        Internal container for the results.

        :arg options: options used to generate these results
        :type options: :class:`Options`

        :arg results: results to be part of this container.
            The results are specified by a key (key of the detector) and a
            :class:`Result <pymontecarlo.result.base.result.Result>` class.
        :type results: :class:`dict`
        """
        self._options = options
        freeze(self._options)

        self._results = {}
        for key, result in results.items():
            if key not in options.detectors:
                raise KeyError('No detector found for result %s' % key)
            self._results[key] = result

    def __repr__(self):
        return '<%s(%s)>' % (self.__class__.__name__,
                             ', '.join(self._results.keys()))

    def __len__(self):
        return len(self._results)

    def __getitem__(self, key):
        return self._results[key]

    def __iter__(self):
        return iter(self._results)

    @property
    def options(self):
        return self._options

class Results(Sequence):
    """
    :class:`.ResultsSequence` is a container of several :class:`.Results`.
    It preserves the order of the results.

    The class works like an immutable :class:`list` object.

    The class also contains parameter values associated to each results.
    The parameters are saved in a dictionary for each results.
    Note that results can have different parameters.
    Parameters are immutable; they cannot be modified.
    Parameters can be retrieved using the property :attr:`parameters`::

        >>> results_seq.parameters[0]['param1']
        >>> 2.0
    """

    VERSION = '7'

    def __init__(self, options, list_results):
        self._options = options
        freeze(self._options)

        self._list_results = []
        for options, results in list_results:
            container = _ResultsContainer(options, results)
            self._list_results.append(container)

    def __repr__(self):
        return '<%s(%i results)>' % (self.__class__.__name__, len(self))

    def __len__(self):
        return len(self._list_results)

    def __getitem__(self, index):
        return self._list_results[index]

    @property
    def options(self):
        return self._options

    @classmethod
    def load(cls, filepath):
        """
        Loads results from a HDF5 file.

        :arg filepath: location of HDF5 file

        :return: results
        """
        task = progress.start_task('Loading results')

        hdf5file = h5py.File(filepath, 'r')

        try:
            # Check version
            if hdf5file.attrs['version'] != cls.VERSION:
                raise IOError("Incorrect version of results sequence. Only version %s is accepted" % \
                              cls.VERSION)

            # Read results
            len_hdf5file = float(len(hdf5file))

            list_results = {}
            for i, item in enumerate(hdf5file.items()):
                task.status = 'Reading results %i' % i
                task.progress = i / len_hdf5file
                identifier, hdf5group = item

                # Options
                task.status = 'Reading options'
                fp = BytesIO(hdf5group.attrs['options'])
                options = Options.load(fp)

                # Load each result
                len_hdf5group = float(len(hdf5group))

                results = {}
                for j, item in enumerate(hdf5group.items()):
                    key, hdf5group2 = item

                    task.status = 'Loading %s' % key
                    task.progress = i / len_hdf5file + j / len_hdf5group * 0.1

                    klass = ResultManager.get_class(hdf5group2.attrs['_class'])
                    results[key] = klass.__loadhdf5__(hdf5group, key)

                # Results
                list_results[identifier.encode('ascii')] = (options, results)

            identifiers = hdf5file.attrs['identifiers']
            if len(identifiers) != len(list_results):
                raise IOError('Number of identifiers do not match number of results')

            list_results = [list_results[identifier] for identifier in identifiers]

            # Read options
            task.status = 'Reading base options'
            fp = BytesIO(hdf5file.attrs['options'])
            options = Options.load(fp)

            return cls(options, list_results)
        finally:
            hdf5file.close()
            progress.stop_task(task)

    def save(self, filepath):
        """
        Saves results as HDF5.

        :arg filepath: location where to save
        """
        task = progress.start_task('Saving results')

        hdf5file = h5py.File(filepath, 'w')

        try:
            # Save version
            hdf5file.attrs['version'] = self.VERSION

            # Save results
            len_self = float(len(self))

            identifiers = []
            for i, results in enumerate(self):
                task.status = 'Saving results %i' % i
                task.progress = i / len_self

                identifier = uuid.uuid4().hex.encode('ascii')
                identifiers.append(identifier)

                hdf5group = hdf5file.create_group(identifier)

                # Save each result
                len_results = float(len(results))

                for j, item in enumerate(results.items()):
                    key, result = item

                    task.status = 'Saving result %s' % key
                    task.progress = i / len_self + j / len_results * 0.1

                    hdf5group2 = hdf5group.create_group(key)
                    tag = ResultManager.get_tag(result.__class__)
                    hdf5group2.attrs['_class'] = tag
                    result.__savehdf5__(hdf5group, key)

                # Save options
                task.status = 'Saving options'
                fp = BytesIO()
                results.options.save(fp, pretty_print=False)
                hdf5group.attrs['options'] = fp.getvalue()

            hdf5file.attrs['identifiers'] = identifiers

            # Save options
            task.status = 'Saving options'
            fp = BytesIO()
            self.options.save(fp, pretty_print=False)
            hdf5file.attrs['options'] = fp.getvalue()
        finally:
            hdf5file.close()
            progress.stop_task(task)
