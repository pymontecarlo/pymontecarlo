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
import copy
import uuid
from collections import Mapping, Sequence
from StringIO import StringIO

# Third party modules.
import h5py

# Local modules.
from pymontecarlo.input.options import Options
from pymontecarlo.output.manager import ResultManager
import pymontecarlo.output.result #@UnusedImport

import pymontecarlo.util.progress as progress

# Globals and constants variables.

class Results(Mapping):
    VERSION = '6'

    def __init__(self, options, results={}):
        """
        Creates a new container for the results.
        Once created, the results container cannot be modified (i.e. read-only).
        
        :arg options: options used to generate these results
        :type options: :class:`Options`
        
        :arg results: results to be part of this container.
            The results are specified by a key (key of the detector) and a
            :class:`Result <pymontecarlo.result.base.result.Result>` class.
        :type results: :class:`dict`
        """
        self._options = copy.deepcopy(options)

        self._results = {}
        for key, result in results.iteritems():
            if key not in options.detectors:
                raise KeyError, 'No detector found for result %s' % key
            self._results[key] = result

    def __repr__(self):
        return '<Results(%s)>' % ', '.join(self._results.keys())

    @classmethod
    def load(cls, filepath):
        """
        Loads results from a HDF5 file.
        
        :arg filepath: location of HDF5 file
        
        :return: results
        """
        hdf5file = h5py.File(filepath, 'r')

        try:
            return cls._load(hdf5file)
        finally:
            hdf5file.close()

    @classmethod
    def _load(cls, hdf5parent):
        """
        Internal method to load results from an HDF5 group.
        """
        task = progress.start_task("Loading results")

        try:
            # Check version
            if hdf5parent.attrs['version'] != cls.VERSION:
                raise IOError, "Incorrect version of results. Only version %s is accepted" % \
                        cls.VERSION

            # Read options
            task.status = 'Reading options'
            fp = StringIO(hdf5parent.attrs['options'])
            options = Options.load(fp)

            # Load each result
            results = {}
            for i, key in enumerate(hdf5parent):
                task.progress = float(i) / len(hdf5parent)
                task.status = 'Loading %s' % key

                hdf5group = hdf5parent[key]
                klass = ResultManager.get_class(hdf5group.attrs['_class'])
                results[key] = klass.__loadhdf5__(hdf5parent, key)

            return cls(options, results)
        finally:
            progress.stop_task(task)

    def save(self, filepath):
        """
        Saves results in a results HDF5.
        
        :arg filepath: location where to save
        """
        hdf5file = h5py.File(filepath, 'w')

        try:
            self._save(hdf5file)
        finally:
            hdf5file.close()

    def _save(self, hdf5parent):
        """
        Internal method to save a results inside the specified HDF5 group.
        """
        task = progress.start_task('Saving results')

        try:
            hdf5parent.attrs['version'] = self.VERSION

            # Save each result
            for i, key in enumerate(self.iterkeys()):
                task.progress = float(i) / len(self)
                task.status = 'Saving result(s) for %s' % key

                result = self[key]

                hdf5group = hdf5parent.create_group(key)
                tag = ResultManager.get_tag(result.__class__)
                hdf5group.attrs['_class'] = tag

                result.__savehdf5__(hdf5parent, key)

            # Save options
            task.status = 'Saving options'
            fp = StringIO()
            self._options.save(fp, pretty_print=False)
            hdf5parent.attrs['options'] = fp.getvalue()
        finally:
            progress.stop_task(task)

    def __len__(self):
        return len(self._results)

    def __getitem__(self, key):
        return self._results[key]

    def __iter__(self):
        return iter(self._results)

    @property
    def options(self):
        """
        Returns a copy of the options.
        """
        return copy.deepcopy(self._options)

class _ResultsSequenceParameters(Sequence):

    def __init__(self, list_params):
        self._list_params = list_params

    def __len__(self):
        return len(self._list_params)

    def __getitem__(self, index):
        return self._list_params[index].copy()

class ResultsSequence(Sequence):
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

    VERSION = '1'

    def __init__(self, list_results, list_params=None):
        self._list_results = list(list_results) # copy

        if list_params is not None :
            if len(list_results) != len(list_params):
                raise ValueError, "Number of parameters should match the number of results"
        else:
            list_params = [{}] * len(list_results)
        self._params = _ResultsSequenceParameters(list_params)

    @classmethod
    def load(cls, filepath):
        """
        Loads results sequence from a HDF5 file.
        
        :arg filepath: location of HDF5 file
        
        :return: results sequence
        """
        task = progress.start_task('Loading results sequence')

        hdf5file = h5py.File(filepath, 'r')

        try:
            # Check version
            if hdf5file.attrs['version'] != cls.VERSION:
                raise IOError, "Incorrect version of results sequence. Only version %s is accepted" % \
                        cls.VERSION

            # Identifiers
            identifiers = hdf5file.attrs['identifiers']

            # Read results and parameters
            list_results = {}
            list_params = {}

            for identifier, hdf5group in hdf5file.iteritems():
                # Results
                results = Results._load(hdf5group)
                list_results[identifier] = results

                # Parameters
                params = {}
                for key, value in hdf5group.attrs.iteritems():
                    if not key.startswith(identifier):
                        continue
                    params[key.split('-')[1]] = value

                list_params[identifier] = params

            # Build sequence
            if len(identifiers) != len(list_results):
                raise IOError, 'Number of identifiers do not match number of results'

            list_results = [list_results[identifier] for identifier in identifiers]
            list_params = [list_params[identifier] for identifier in identifiers]
            return cls(list_results, list_params)
        finally:
            hdf5file.close()
            progress.stop_task(task)

    def save(self, filepath):
        """
        Saves results sequence in a results HDF5.
        
        :arg filepath: location where to save
        """
        task = progress.start_task('Saving results sequence')

        hdf5file = h5py.File(filepath, 'w')

        try:
            hdf5file.attrs['version'] = self.VERSION

            identifiers = []
            for results, params in zip(self, self._params):
                identifier = uuid.uuid4().hex
                identifiers.append(identifier)

                hdf5group = hdf5file.create_group(identifier)

                for param, value in params.iteritems():
                    hdf5group.attrs['%s-%s' % (identifier, param)] = value

                results._save(hdf5group)

            hdf5file.attrs['identifiers'] = identifiers
        finally:
            hdf5file.close()
            progress.stop_task(task)

    def __repr__(self):
        return '<%s(%i results)>' % (self.__class__.__name__, len(self))

    def __len__(self):
        return len(self._list_results)

    def __getitem__(self, index):
        return self._list_results[index]

    @property
    def parameters(self):
        return self._params

    params = parameters
