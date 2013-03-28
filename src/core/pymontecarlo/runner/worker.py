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

# Third party modules.

# Local modules.

# Globals and constants variables.

class Worker(object):

    def __init__(self):
        """
        Base class for all workers. 
        A worker is used to run simulations in a queue with a given program and 
        return their results.
        It can also be used to create the simulation files required to run
        simulation(s) (without running them).
        
        A worker should not be directly used to start a simulation. 
        One should rather use a runner.
        """
        self._progress = 0.0
        self._status = ''

    def reset(self):
        """
        Resets the worker. This method is called before starting a run.
        """
        self._progress = 0.0
        self._status = ''

    def create(self, options, outputdir):
        """
        Creates the simulation file(s) from the options and saves it inside the
        output directory.
        This method should be implemented by derived class as it is specific
        to the different Monte Carlo programs.

        :arg options: options of a simulation
        :arg outputdir: directory where to save the simulation file(s)
        """
        raise NotImplementedError

#        """
#        Creates all simulation files without starting the simulation(s).
#        All simulations in the options queue will be created.
#        The simulation files created will depend on the Monte Carlo program used.
#        The simulation files could also be a folder.
#        The simulation files are saved in the *output directory*.
#        """
#        while True:
#            try:
#                options = self._queue_options.get()
#                self._create(options, self._outputdir)
#                self._queue_options.task_done()
#            except Exception:
#                self.stop()
#                self._queue_options.raise_exception()
#
#    def _create(self, options, dirpath):
#        """
#        Creates the simulation file(s) from the options and saves it inside the
#        specified directory.
#        This method should be implemented by derived class as it is specific
#        to the different Monte Carlo programs.
#
#        :arg options: options of a simulation
#        :arg dirpath: directory where to save the simulation file(s)
#        """
#        raise NotImplementedError

    def run(self, options, outputdir, workdir):
        """
        Creates and runs a simulation from the specified options.
        This method should be implemented by derived class.
        
        :arg options: options of simulation
        :arg outputdir: output directory where complementary results should be
            saved
        :arg workdir: work directory where temporary files should be saved
        
        :return: results of simulation
        :rtype: :class:`Results`
        """
        raise NotImplementedError

    def stop(self):
        """
        Stops worker.
        """
        self._status = 'Stopped'

    def report(self):
        """
        Returns a tuple of:
        
          * the progress of the current running simulation (between 0.0 and 1.0)
          * text indicating the status of the current running simulation
        """
        return self._progress, self._status

class SubprocessWorker(Worker):

    def reset(self):
        Worker.reset(self)
        self._process = None

    def stop(self):
        if self._process is not None:
            self._process.kill()
        Worker.stop(self)

