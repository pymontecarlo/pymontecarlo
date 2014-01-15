#!/usr/bin/env python
"""
================================================================================
:mod:`importer` -- Base class for all importers
================================================================================

.. module:: importer
   :synopsis: Base class for all importers

.. inheritance-diagram:: pymontecarlo.output.importer

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import warnings
from abc import ABCMeta, abstractmethod

# Third party modules.

# Local modules.
from pymontecarlo.results.results import Results

# Globals and constants variables.

class ImporterWarning(Warning):
    pass

class ImporterException(Exception):
    pass

class Importer(object):

    __metaclass__ = ABCMeta

    def __init__(self):
        self._importers = {}

    def import_(self, options, dirpath, *args, **kwargs):
        """
        Imports the results.

        :arg options: options to export
            The options must only contained a single value for each parameter.
        :arg outputdir: full path to output directory
        """
        if not os.path.isdir(dirpath):
            raise ValueError("Specified path (%s) is not a directory" % dirpath)
        return self._import(options, dirpath, *args, **kwargs)

    @abstractmethod
    def _import(self, options, dirpath, *args, **kwargs):
        """
        Performs the actual import.
        """
        raise NotImplementedError

    def _run_importers(self, options, *args, **kwargs):
        """
        Internal command to call the correct import function for each
        detector in the options.
        The following arguments are passed to the import function:

            * options object
            * name/key of detector/result
            * detector object
            * optional arguments and keyword-arguments

        The import function must return the result for this detector.
        """
        results = {}

        for key, detector in options.detectors.iteritems():
            clasz = detector.__class__
            method = self._importers.get(clasz)

            if not method:
                message = "Could not import results from '%s' detector (%s)" % \
                    (key, clasz.__name__)
                warnings.warn(message, ImporterWarning)

            result = method(options, key, detector, *args, **kwargs)
            results[key] = result

        return Results(options, [(options, results)])

class HDF5Importer(Importer):

    def _import(self, options, dirpath, *args, **kwargs):
        filepath = os.path.join(dirpath, options.name + '.h5')
        return Results.load(filepath)
