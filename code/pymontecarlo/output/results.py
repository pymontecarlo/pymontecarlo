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

# Standard library modules.
import copy
from collections import Mapping
from StringIO import StringIO

# Third party modules.
import h5py

# Local modules.
from pymontecarlo.input.options import Options
from pymontecarlo.output.manager import ResultManager
import pymontecarlo.output.result #@UnusedImport

import pymontecarlo.util.progress as progress

# Globals and constants variables.

VERSION = '5'

class Results(Mapping):

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
    def load(cls, source):
        """
        Loads results from a results (HDF5).
        
        :arg source: filepath or file-object
        
        :return: results container
        """
        task = progress.start_task("Loading results")

        hdf5file = h5py.File(source, 'r')

        # Check version
        if hdf5file.attrs['version'] != VERSION:
            raise IOError, "Incorrect version of results. Only version %s is accepted" % \
                    VERSION

        # Read options
        task.status = 'Reading options'
        fp = StringIO(hdf5file.attrs['options'])
        options = Options.load(fp)

        # Load each result
        results = {}
        for i, key in enumerate(hdf5file):
            task.progress = float(i) / len(hdf5file)
            task.status = 'Loading %s' % key

            hdf5group = hdf5file[key]
            klass = ResultManager.get_class(hdf5group.attrs['_class'])
            results[key] = klass.__loadhdf5__(hdf5file, key)

        hdf5file.close()

        progress.stop_task(task)

        return cls(options, results)

    def save(self, source):
        """
        Saves results in a results HDF5.
        
        :arg source: filepath or file-object
        """
        task = progress.start_task('Saving results')

        hdf5file = h5py.File(source, 'w')
        hdf5file.attrs['version'] = VERSION

        # Save each result
        for i, key in enumerate(self.iterkeys()):
            task.progress = float(i) / len(self)
            task.status = 'Saving result(s) for %s' % key

            result = self[key]

            hdf5group = hdf5file.create_group(key)
            tag = ResultManager.get_tag(result.__class__)
            hdf5group.attrs['_class'] = tag

            result.__savehdf5__(hdf5file, key)

        # Save options
        task.status = 'Saving options'
        fp = StringIO()
        self._options.save(fp, pretty_print=False)
        hdf5file.attrs['options'] = fp.getvalue()

        hdf5file.close()

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


