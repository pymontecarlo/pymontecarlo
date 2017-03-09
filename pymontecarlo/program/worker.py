#!/usr/bin/env python
"""
Base worker
"""

# Standard library modules.
import os
import sys
import subprocess
import logging
import abc
import tempfile
import shutil

# Third party modules.

# Local modules.
from pymontecarlo.exceptions import WorkerError, WorkerCancelledError

# Globals and constants variables.

class Worker(metaclass=abc.ABCMeta):
    """
    Base class for all workers.
    A worker is used to run one simulation with a given program and
    return their results.
    It can also be used to create the simulation files required to run
    simulation(s) (without running them).

    A worker should not be directly used to start a simulation.
    One should rather use a runner.
    """

    def __init__(self):
        self._progress = 0.0
        self._status = ''

#    def create(self, options, outputdir, *args, **kwargs):
#        """
#        Creates the simulation file(s) from the options and saves it inside the
#        output directory.
#        This method should be implemented by derived class as it is specific
#        to the different Monte Carlo programs.
#
#        :arg options: options of a simulation
#        :arg outputdir: directory where to save the simulation file(s)
#        """
#        filepath = os.path.join(outputdir, options.name + '.xml')
#        options.write(filepath)
#
#        return self._exporter.export(options, outputdir)

    def _setup_outputdir(self, simulation, outputdir=None):
        """
        Creates a temporary directory if *outputdir* is ``None``, otherwise
        create a directory with the simulation *identifier* in the output directory.
        """
        if outputdir is None:
            outputdir = tempfile.mkdtemp()
            return outputdir, True

        else:
            outputdir = os.path.join(outputdir, simulation.identifier)
            os.makedirs(outputdir, exist_ok=True)
            return outputdir, False

    def _cleanup_outputdir(self, outputdir, temporary):
        if temporary:
            shutil.rmtree(outputdir, ignore_errors=True)

    def _update_state(self, progress, status):
        self._progress = progress
        self._status = status

    @abc.abstractmethod
    def run(self, simulation, outputdir):
        """
        Creates and runs a simulation from the specified options.

        :arg simulation: simulation containing options to simulate
        :arg outputdir: directory where to save simulation results.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def cancel(self):
        """
        Cancels worker.
        """
        raise NotImplementedError

    @property
    def progress(self):
        return self._progress

    @property
    def status(self):
        return self._status

class SubprocessWorker(Worker):

    def __init__(self):
        super().__init__()
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
        if returncode != 0:
            raise WorkerError

    def cancel(self):
        if self._process is not None:
            self._process.kill()
            self._update_state(0.0, 'Cancelled')
            raise WorkerCancelledError

