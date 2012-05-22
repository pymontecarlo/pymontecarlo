#!/usr/bin/env python
"""
================================================================================
:mod:`importer` -- Base class for all importers
================================================================================

.. module:: importer
   :synopsis: Base class for all importers

.. inheritance-diagram:: pymontecarlo.io.importer

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
from pymontecarlo.output.results import Results

# Globals and constants variables.

class ImporterWarning(Warning):
    pass

class ImporterException(Exception):
    pass

class Importer(object):

    def __init__(self):
        self._detector_importers = {}

    def _import_results(self, options, *args):
        results = {}

        for key, detector in options.detectors.iteritems():
            clasz = detector.__class__
            method = self._detector_importers.get(clasz)

            if method:
                result = method(options, key, detector, *args)
                results[key] = result
            else:
                message = "Could not import results from '%s' detector (%s)" % \
                    (key, clasz.__name__)
                warnings.warn(message, ImporterWarning)

        return Results(results)

