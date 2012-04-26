#!/usr/bin/env python
"""
================================================================================
:mod:`worker` -- Base worker
================================================================================

.. module:: worker
   :synopsis: Base worker

.. inheritance-diagram:: pymontecarlo.runner.base.worker

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import threading
import tempfile
import shutil
import logging
import platform

# Third party modules.

# Local modules.

# Globals and constants variables.
PLATFORM_WINDOWS = 'Windows'
PLATFORM_MACOS = 'MacOS'
PLATFORM_LINUX = 'Linux'

def get_platform():
    return platform.system()

class InvalidPlatform(Exception):
    pass

class Worker(threading.Thread):
    def __init__(self, queue_options, outputdir, workdir=None, overwrite=True):
        """
        Base class for all workers. 
        A worker is used to run simulations in a queue with a given program and 
        saved their results in the output directory.
        It can also be used to create the simulation files required to run
        simulation(s) (without running them).
        
        A worker should not be directly used to start a simulation. 
        One should rather use a runner.
        
        :arg queue_options: queue of options to run using this worker
        
        :arg outputdir: output directory for saving the results from the 
            simulation. The directory must exists.
            
        :arg workdir: work directory for temporary files created during the 
            simulation(s). If ``None``, a temporary folder is created and 
            removed after all simulations are run. If not ``None``, the 
            directory must exists.
        
        :arg overwrite: whether to overwrite results if they exist
            (default: ``True``)
        """
        threading.Thread.__init__(self)

        self._queue_options = queue_options

        if not os.path.isdir(outputdir):
            raise ValueError, 'Output directory (%s) is not a directory' % outputdir
        self._outputdir = outputdir

        if workdir is not None and not os.path.isdir(workdir):
            raise ValueError, 'Work directory (%s) is not a directory' % workdir
        self._workdir = workdir

        self._overwrite = overwrite

        self._reset()

    def _reset(self):
        """
        Resets the worker. This method is called before starting a run.
        """
        self._progress = 0.0
        self._status = ''

    def create(self):
        """
        Creates all simulation files without starting the simulation(s).
        All simulations in the options queue will be created.
        The simulation files created will depend on the Monte Carlo program used.
        The simulation files could also be a folder.
        The simulation files are saved in the *output directory*.
        """
        while True:
            try:
                options = self._queue_options.get()
                self._create(options, self._outputdir)
                self._queue_options.task_done()
            except Exception as exc:
                self.stop()
                self._queue_options.raise_exc(exc)

    def _create(self, options, dirpath):
        """
        Creates the simulation file(s) from the options and saves it inside the 
        specified directory.
        This method should be implemented by derived class as it is specific
        to the different Monte Carlo programs.
        
        :arg options: options of a simulation
        :arg dirpath: directory where to save the simulation file(s)
        """
        raise NotImplementedError

    def run(self):
        """
        Creates and runs all simulations in the options queue.
        The results from the simulations are then saved in the *output directory*.
        """
        while True:
            try:
                self._reset()

                self._progress = 0.0
                self._status = 'Starting'

                # Retrieve options
                options = self._queue_options.get()

                # Check if results already exists
                zipfilepath = os.path.join(self._outputdir, options.name + ".zip")
                if os.path.exists(zipfilepath) and not self._overwrite:
                    logging.info('Skipping %s as results already exists', options.name)
                    self._queue_options.task_done()
                    continue

                # Create working directory
                if self._workdir is None:
                    self._workdir = tempfile.mkdtemp()
                    _user_defined_workdir = False
                    logging.debug('Temporary work directory: %s', self._workdir)
                else:
                    _user_defined_workdir = True

                # Run
                self._run(options)

                # Save results
                self._save_results(options, zipfilepath)
                logging.debug('Results saved at %s', zipfilepath)

                # Cleanup working directory if needed
                if not _user_defined_workdir:
                    shutil.rmtree(self._workdir, ignore_errors=True)
                    logging.debug('Removed temporary work directory: %s', self._workdir)
                    self._workdir = None

                self._progress = 1.0
                self._status = 'Completed'

                self._queue_options.task_done()
            except Exception as exc:
                self.stop()

                if not _user_defined_workdir:
                    shutil.rmtree(self._workdir, ignore_errors=True)

                self._queue_options.raise_exc(exc)

    def _run(self, options):
        """
        Creates and runs a simulation from the specified options.
        This method should be implemented by derived class.
        """
        raise NotImplementedError

    def _save_results(self, options, zipfilepath):
        """
        Generates the results from the simulation outputs after the simulation 
        was run and then save them at the specified location.
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

    def _get_filepath(self, options, dirpath, ext='xml'):
        """
        **Utility function**
        
        Returns a filepath inside the specified directory.
        The filename is the name of the options with the specified extension.
        
        :arg options: options of a simulation
        :arg dirpath: directory of the file
        :arg ext: extension of the file
        """
        return os.path.join(dirpath, options.name + "." + ext)

    def _get_dirpath(self, options):
        """
        **Utility function**
        
        Returns the following path: *work directory*/*name of options*.
        The directory is created if it doesn't exist.
        
        :arg options: options of a simulation
        """
        dirpath = os.path.join(self._workdir, options.name)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        return dirpath

class SubprocessWorker(Worker):
    def _reset(self):
        Worker._reset(self)
        self._process = None

    def stop(self):
        if self._process is not None:
            self._process.kill()
        Worker.stop(self)

