#!/usr/bin/env python
"""
Base worker
"""

# Standard library modules.
import sys
import subprocess
import logging
import abc

# Third party modules.

# Local modules.
from pymontecarlo.exceptions import WorkerError, WorkerCancelledError
from pymontecarlo.util.cbook import MonitorableMixin

# Globals and constants variables.

class Worker(MonitorableMixin, metaclass=abc.ABCMeta):
    """
    Base class for all workers.
    A worker is used to run one simulation with a given program and
    return their results.
    It can also be used to create the simulation files required to run
    simulation(s) (without running them).

    A worker should not be directly used to start a simulation.
    One should rather use a runner.
    """

    @abc.abstractmethod
    def run(self, simulation, outputdir):
        """
        Creates and runs a simulation from the specified options.

        :arg simulation: simulation containing options to simulate
        :arg outputdir: directory where to save simulation results.
        """
        raise NotImplementedError

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

    def running(self):
        self._process.poll()
        return self._process.returncode is None

    def cancel(self):
        if self._process is not None:
            self._process.kill()
            self._update_state(0.0, 'Cancelled')
            raise WorkerCancelledError

