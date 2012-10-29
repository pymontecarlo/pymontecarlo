#!/usr/bin/env python
"""
================================================================================
:mod:`simulation` -- Simulation
================================================================================

.. module:: simulation
   :synopsis: Simulation

.. inheritance-diagram:: pymontecarlo.io.simulation

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import copy
from zipfile import ZipFile
from StringIO import StringIO

# Third party modules.

# Local modules.
from pymontecarlo.input.options import Options
from pymontecarlo.output.results import Results

import pymontecarlo.util.progress as progress

# Globals and constants variables.
VERSION = '1'
OPTIONS_FILENAME = 'options.xml'

class Simulation(object):

    def __init__(self, options=None, results=None):
        """
        Creates a new simulation.
        """
        # Initialize options
        if options is None:
            options = Options()
        else:
            options = copy.deepcopy(options)
        self._options = options

        # Initialize results
        if results is None:
            results = Results()
        else:
            results = copy.deepcopy(results)
        self._results = results

        # Check results
        for key in self._results.iterkeys():
            if key not in self._options.detectors:
                raise KeyError, 'No detector was found for result %s' % key

    def __repr__(self):
        return '<%s(%s)>' % (self.__class__.__name__, self.options.name)

    @classmethod
    def load(cls, source):
        """
        Loads options/results from a PMC.
        
        :arg source: filepath or file-object
        
        :return: simulation
        """
        task = progress.start_task("Loading simulation")

        zipfile = ZipFile(source, 'r')

        # Check version
        if zipfile.comment != 'version=%s' % VERSION:
            raise IOError, "Incorrect version of simulation. Only version %s is accepted" % \
                    VERSION

        # Load options
        task.status = 'Reading %s' % OPTIONS_FILENAME

        try:
            zipinfo = zipfile.getinfo(OPTIONS_FILENAME)
        except KeyError:
            raise IOError, "Zip file (%s) does not contain a %s" % \
                    (getattr(source, 'name', 'unknown'), OPTIONS_FILENAME)

        options = Options.load(zipfile.open(zipinfo, 'r'))

        zipfile.close()

        # Load results
        task.status = 'Reading results'
        task.progress = 0.5
        results = Results.load(source)

        progress.stop_task(task)

        return cls(options, results)

    def save(self, source):
        """
        Saves results in a results ZIP.
        
        :arg source: filepath or file-object
        """
        task = progress.start_task("Saving simulation")

        # Save results
        task.status = 'Saving results'
        self.results.save(source)

        # Save options
        task.progress = 0.5
        task.status = 'Saving %s' % OPTIONS_FILENAME

        zipfile = ZipFile(source, 'r')
        fp = StringIO()
        self.options.save(fp)
        zipfile.writestr(OPTIONS_FILENAME, fp.getvalue())

        # Set version
        zipfile.comment = 'version=%s' % VERSION

        zipfile.close()

        progress.stop_task(task)

    @property
    def options(self):
        if self.results:
            return copy.deepcopy(self._options) # Immutable
        return self._options # Mutable

    @property
    def results(self):
        return self._results


