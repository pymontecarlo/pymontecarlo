#!/usr/bin/env python
"""
================================================================================
:mod:`worker` -- Base worker
================================================================================

.. module:: worker
   :synopsis: Base worker

.. inheritance-diagram:: pymontecarlo.runner.worker

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import sys
import subprocess
import logging

# Third party modules.

# Local modules.

# Globals and constants variables.

class Worker(object):

    def __init__(self, program):
        """
        Base class for all workers.
        A worker is used to run simulations in a queue with a given program and
        return their results.
        It can also be used to create the simulation files required to run
        simulation(s) (without running them).

        A worker should not be directly used to start a simulation.
        One should rather use a runner.
        """
        self._program = program
        self._exporter = program.exporter_class()
        self._importer = program.importer_class()

        self._progress = 0.0
        self._status = ''

    def reset(self):
        """
        Resets the worker. This method is called before starting a run.
        """
        self._progress = 0.0
        self._status = ''

    def create(self, options, outputdir, *args, **kwargs):
        """
        Creates the simulation file(s) from the options and saves it inside the
        output directory.
        This method should be implemented by derived class as it is specific
        to the different Monte Carlo programs.

        :arg options: options of a simulation
        :arg outputdir: directory where to save the simulation file(s)
        """
        filepath = os.path.join(outputdir, options.name + '.xml')
        options.write(filepath)

        return self._exporter.export(options, outputdir)

    def run(self, options, outputdir, workdir, *args, **kwargs):
        """
        Creates and runs a simulation from the specified options.
        This method should be implemented by derived class.

        :arg options: options of simulation
        :arg outputdir: output directory where complementary results should be
            saved
        :arg workdir: work directory where temporary files should be saved

        :return: results of simulation
        :rtype: :class:`ResultsContainer`
        """
        raise NotImplementedError

    def cancel(self):
        """
        Cacncels worker.
        """
        self._status = 'Cancelled'

    def report(self):
        """
        Returns a tuple of:

          * the progress of the current running simulation (between 0.0 and 1.0)
          * text indicating the status of the current running simulation
        """
        return self._progress, self._status

    @property
    def program(self):
        return self._program

    @property
    def progress(self):
        return self._progress

    @property
    def status(self):
        return self._status

class SubprocessWorker(Worker):

    def __init__(self, program):
        Worker.__init__(self, program)
        self._process = None

    def _create_process(self, *args, **kwargs):
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        else:
            startupinfo = None
        logging.debug('Args: %s' % subprocess.list2cmdline(args[0]))
        self._process = subprocess.Popen(*args, startupinfo=startupinfo, **kwargs)
        return self._process

    def _join_process(self):
        self._process.wait()
        returncode = self._process.returncode
        self._process = None
        logging.debug('returncode: %s' % returncode)
        return returncode

    def reset(self):
        Worker.reset(self)
        self._process = None

    def cancel(self):
        if self._process is not None:
            self._process.kill()
        Worker.cancel(self)

