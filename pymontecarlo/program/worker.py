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
from pymontecarlo.exceptions import WorkerError

# Globals and constants variables.

class Worker:
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
    def run(self, token, simulation, outputdir):
        """
        Creates and runs a simulation from the specified options.

        :arg simulation: simulation containing options to simulate
        :arg outputdir: directory where to save simulation results.
        """
        raise NotImplementedError

class SubprocessWorkerMixin:

    def _create_process(self, *args, **kwargs):
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        else:
            startupinfo = None
        logging.debug('Args: %s' % subprocess.list2cmdline(args[0]))
        return subprocess.Popen(*args, startupinfo=startupinfo, **kwargs)

    def _wait_process(self, process, token, timeout=1):
        while process.wait(timeout) is None:
            if token.cancelled():
                process.kill()
                break

        returncode = process.poll()
        logging.debug('returncode: %s' % returncode)
        if returncode != 0:
            raise WorkerError

        return returncode


