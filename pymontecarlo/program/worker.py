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

    @abc.abstractmethod
    def run(self, options):
        """
        Creates and runs a simulation from the specified options.

        :arg options: options of simulation

        :return: simulation
        """
        raise NotImplementedError

    @abc.abstractmethod
    def cancel(self):
        """
        Cancels worker.
        """
        raise NotImplementedError

    @abc.abstractproperty
    def progress(self):
        return 0.0

    @abc.abstractproperty
    def status(self):
        return ''

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
            raise WorkerCancelledError

