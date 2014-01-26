#!/usr/bin/env python
"""
================================================================================
:mod:`worker` -- PENEPMA worker
================================================================================

.. module:: worker
   :synopsis: PENEPMA worker

.. inheritance-diagram:: pymontecarlo.program.penepma.runner.worker

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import subprocess
import logging

# Third party modules.

# Local modules.
from pymontecarlo.settings import get_settings
from pymontecarlo.options.limit import TimeLimit, ShowersLimit, UncertaintyLimit
from pymontecarlo.program._penelope.worker import Worker as _Worker

# Globals and constants variables.

class Worker(_Worker):

    def __init__(self, program):
        """
        Runner to run PENEPMA simulation(s).
        """
        _Worker.__init__(self, program)

        self._executable = get_settings().penepma.exe
        if not os.path.isfile(self._executable):
            raise IOError('PENEPMA executable (%s) cannot be found' % self._executable)
        logging.debug('PENEPMA executable: %s', self._executable)

    def run(self, options, outputdir, workdir, *args, **kwargs):
        infilepath = self.create(options, workdir, createdir=False)

        # Extract limit
        limits = list(options.limits.iterclass(ShowersLimit))
        showers_limit = limits[0].showers if limits else 1e38

        limits = list(options.limits.iterclass(TimeLimit))
        time_limit = limits[0].time_s if limits else 1e38

        limits = list(options.limits.iterclass(UncertaintyLimit))
        uncertainty_limit = 1.0 - limits[0].uncertainty if limits else float('inf')

        # Launch
        args = [self._executable]
        stdin = open(infilepath, 'r')
        logging.debug('Launching %s', ' '.join(args))

        self._status = 'Running PENEPMA'
        self._progress = 0.001 # Ensure that the simulation has started

        with subprocess.Popen(args, stdin=stdin, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, cwd=workdir) as self._process:
            for line in iter(self._process.stdout.readline, b""):
                infos = line.decode('ascii').split(',')
                if len(infos) == 1:
                    self._status = infos[0].strip()
                    if self._status.startswith('STOP'):
                        raise RuntimeError("The following error occurred during the simulation: %s" % self._status)
                elif len(infos) == 4:
                    progress_showers = float(infos[0]) / showers_limit
                    progress_time = float(infos[1]) / time_limit
                    progress_uncertainty = (1.0 - float(infos[2])) / uncertainty_limit
                    self._progress = max(0.001, progress_showers, progress_time,
                                         progress_uncertainty)
                    self._status = 'Running'

            self._process.wait()
            retcode = self._process.returncode

        self._process = None
        stdin.close()

        if retcode != 0:
            raise RuntimeError("An error occurred during the simulation")

        return self._extract_results(options, outputdir, workdir)

