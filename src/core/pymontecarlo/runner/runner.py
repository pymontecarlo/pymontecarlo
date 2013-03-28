#!/usr/bin/env python
"""
================================================================================
:mod:`queue` -- Queue of workers for running simulations
================================================================================

.. module:: queue
   :synopsis: Queue of workers for running simulations

.. inheritance-diagram:: pymontecarlo.runner.runner

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import copy
import logging
from Queue import Empty
import threading
import tempfile
import shutil
import posixpath
import fnmatch
import datetime
import re
import time

# Third party modules.
import paramiko

# Local modules.
from pymontecarlo.util.queue import Queue
import pymontecarlo.util.xmlutil as xmlutil
from pymontecarlo.output.results import Results

# Globals and constants variables.

class _Runner(object):

    def __init__(self, program):
        """
        Creates a new runner to run several simulations.
        
        Use :meth:`put` to add simulation to the run and then use the method
        :meth:`start` to start the simulation(s). 
        Status of the simulations can be retrieved using the method 
        :meth:`report`. 
        The method :meth:`join` before closing an application to ensure that
        all simulations were run and all workers are stopped.
        
        :arg program: program used to run the simulations
        """
        self._program = program

        self._options_names = []
        self._queue_options = Queue()
        self._queue_results = Queue()

    @property
    def program(self):
        """
        Program of this runner.
        """
        return self._program

    def put(self, options):
        """
        Puts an options in queue.
        
        An :exc:`ValueError` is raised if an options with the same name was
        already added. This error is raised has options with the same name 
        would lead to results been overwritten.
        
        .. note::
        
           A copy of the options is put in queue
           
        :arg options: options to be added to the queue
        """
        name = options.name
        if name in self._options_names:
            raise ValueError, 'An options with the name (%s) was already added' % name

        self._queue_options.put(copy.deepcopy(options))
        self._options_names.append(name)

        logging.debug('Options "%s" put in queue', name)

    def start(self):
        """
        Starts running the simulations.
        """
        raise NotImplementedError

    def stop(self):
        """
        Stops all running simulations.
        """
        raise NotImplementedError

    def is_alive(self):
        """
        Returns whether all options in the queue were simulated.
        """
        return not self._queue_options.are_all_tasks_done()

    def join(self):
        """
        Blocks until all options have been simulated.
        """
        self._queue_options.join()
        self.stop()
        self._options_names[:] = [] # clear

    def get_results(self):
        """
        Returns the results from the simulations.
        This is a blocking method which calls :meth:`join` before returning
        the results.
        
        :rtype: :class:`list`
        """
        self.join()

        results = []
        while True:
            try:
                results.append(self._queue_results.get_nowait())
            except Empty:
                break
        return results

    def report(self):
        """
        Returns a tuple of:
        
          * counter of completed simulations
          * the progress of *one* of the currently running simulations 
              (between 0.0 and 1.0)
          * text indicating the status of *one* of the currently running 
              simulations
        """
        completed = len(self._options_names) - self._queue_options.unfinished_tasks
        return completed, 0, ''

class _Dispatcher(threading.Thread):

    def __init__(self, program, queue_options, queue_results):
        threading.Thread.__init__(self)

        self._program = program
        self._queue_options = queue_options
        self._queue_results = queue_results

    def stop(self):
        """
        Stops running simulation.
        """
        threading.Thread.__init__(self)

    def report(self):
        """
        Returns a tuple of:
        
          * counter of completed simulations
          * the progress of *one* of the currently running simulations 
              (between 0.0 and 1.0)
          * text indicating the status of *one* of the currently running 
              simulations
        """
        return 0.0, ''

class _LocalDispatcher(_Dispatcher):

    def __init__(self, program, queue_options, queue_results,
                 outputdir, workdir=None, overwrite=True):
        _Dispatcher.__init__(self, program, queue_options, queue_results)

        self._worker = program.worker_class()

        if not os.path.isdir(outputdir):
            raise ValueError, 'Output directory (%s) is not a directory' % outputdir
        self._outputdir = outputdir

        if workdir is not None and not os.path.isdir(workdir):
            raise ValueError, 'Work directory (%s) is not a directory' % workdir
        self._workdir = workdir
        self._user_defined_workdir = self._workdir is not None

        self._overwrite = overwrite

    def run(self):
        while True:
            try:
                # Retrieve options
                options = self._queue_options.get()

                # Check if results already exists
                h5filepath = os.path.join(self._outputdir, options.name + ".h5")
                if os.path.exists(h5filepath) and not self._overwrite:
                    logging.info('Skipping %s as results already exists', options.name)
                    self._queue_options.task_done()
                    continue

                # Create working directory
                self._setup_workdir()

                # Run
                logging.debug('Running program specific worker')
                self._worker.reset()
                results = self._worker.run(options, self._outputdir, self._workdir)
                logging.debug('End program specific worker')

                # Cleanup
                self._cleanup()

                # Save results
                results.save(h5filepath)
                logging.debug('Results saved')

                # Put results in queue
                self._queue_results.put(results)

                self._queue_options.task_done()
            except:
                self.stop()
                self._queue_options.raise_exception()

    def _setup_workdir(self):
        if not self._user_defined_workdir:
            self._workdir = tempfile.mkdtemp()
            logging.debug('Temporary work directory: %s', self._workdir)

    def _cleanup(self):
        if not self._user_defined_workdir:
            shutil.rmtree(self._workdir, ignore_errors=True)
            logging.debug('Removed temporary work directory: %s', self._workdir)
            self._workdir = None

    def stop(self):
        self._worker.stop()
        _Dispatcher.stop(self)

    def report(self):
        return self._worker.report()

class LocalRunner(_Runner):

    def __init__(self, program, outputdir, workdir=None, overwrite=True,
                 nbprocesses=1):
        """
        Creates a new runner to run several simulations.
        
        Use :meth:`put` to add simulation to the run and then use the method
        :meth:`start` to start the simulation(s). 
        Status of the simulations can be retrieved using the method 
        :meth:`report`. 
        The method :meth:`join` before closing an application to ensure that
        all simulations were run and all workers are stopped.
        
        :arg program: program used to run the simulations
        
        :arg outputdir: output directory for saving the results from the 
            simulation. The directory must exists.
        
        :arg workdir: work directory for the simulation temporary files.
            If ``None``, a temporary folder is created and removed after each
            simulation is run. If not ``None``, the directory must exists.
        
        :arg overwrite: whether to overwrite already existing simulation file(s)
        
        :arg nbprocesses: number of processes/threads to use (default: 1)
        """
        _Runner.__init__(self, program)

        if nbprocesses < 1:
            raise ValueError, "Number of processes must be greater or equal to 1."
        self._nbprocesses = nbprocesses

        if not os.path.isdir(outputdir):
            raise ValueError, 'Output directory (%s) is not a directory' % outputdir
        self._outputdir = outputdir

        if workdir is not None and not os.path.isdir(workdir):
            raise ValueError, 'Work directory (%s) is not a directory' % workdir
        self._workdir = workdir

        self._overwrite = overwrite

        self._dispatchers = []

    @property
    def outputdir(self):
        """
        Output directory.
        """
        return self._outputdir

    def start(self):
        """
        Starts running the simulations.
        """
        if self._dispatchers:
            raise RuntimeError, 'Already started'

        # Create dispatchers
        self._dispatchers = []
        for _ in range(self._nbprocesses):
            dispatcher = \
                _LocalDispatcher(self.program,
                                 self._queue_options, self._queue_results,
                                 self._outputdir, self._workdir,
                                 self._overwrite)
            self._dispatchers.append(dispatcher)

            dispatcher.daemon = True
            dispatcher.start()
            logging.debug('Started dispatcher: %s', dispatcher.name)

    def stop(self):
        """
        Stops all dispatchers and closes the current runner.
        """
        for dispatcher in self._dispatchers:
            dispatcher.stop()
        self._dispatchers = []

    def report(self):
        """
        Returns a tuple of:
        
          * counter of completed simulations
          * the progress of *one* of the currently running simulations 
              (between 0.0 and 1.0)
          * text indicating the status of *one* of the currently running 
              simulations
        """
        completed, progress, status = _Runner.report(self)

        for dispatcher in self._dispatchers:
            progress, status = dispatcher.report()
            if progress > 0.0 and progress < 1.0: # active worker
                return completed, progress, status

        return completed, progress, status

class _RemoteDispatcher(_Dispatcher):

    def __init__(self, program, queue_options, queue_results,
                 connection_dict, remote_workdir, local_outputdir):
        _Dispatcher.__init__(self, program, queue_options, queue_results)

        self._connection_dict = connection_dict
        self._remote_workdir = remote_workdir
        self._local_outputdir = local_outputdir

        self._jobids = set()

    def start(self):
        self._jobids.clear()

        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._client.connect(**self._connection_dict)

        _Dispatcher.start(self)

    def run(self):
        while True:
            try:
                # Try to get all available options
                options_list = []
                while True:
                    try:
                        options_list.append(self._queue_options.get_nowait())
                    except Empty:
                        break

                # Submit new simulations
                if options_list:
                    remote_filepaths = self._transfer_options(options_list)
                    self._jobids |= set(self._launch_simulations(remote_filepaths))

                # Update completed simulations
                _, _, completed = self._progress_simulations(self._jobids)

                for jobid in completed:
                    self._queue_options.task_done()
                    self._jobids.remove(jobid)

                # Transfer new results
                local_filepaths = self._transfer_results()

                for local_filepath in local_filepaths:
                    self._queue_results.put(Results.load(local_filepath))

                # Delay
                time.sleep(1.0)
            except:
                self.stop()
                self._queue_options.raise_exception()

    def _transfer_options(self, options_list):
        """
        Creates options file (.xml) in work directory on remote host.
        """
        try:
            ftp = self._client.open_sftp()

            # Make work directory
            command = 'mkdir -p "%s"' % self._remote_workdir
            _, _, stderr = self._client.exec_command(command)
            stderr = list(stderr)
            if stderr:
                raise IOError, 'Error while creating work directory: %s' % \
                        ''.join(stderr)

            # Transfer options
            remote_filepaths = []

            for options in options_list:
                remote_filepath = \
                    posixpath.join(self._remote_workdir, options.name + '.xml')
                data = xmlutil.tostring(options.to_xml())

                ftp.open(remote_filepath, 'w').write(data)
                logging.debug("Transfered options to %s", remote_filepath)

                remote_filepaths.append(remote_filepath)
        finally:
            ftp.close()

        return remote_filepaths

    def _transfer_results(self):
        """
        Transfers all results files (.h5) from work directory on remote host
        to output directory on local host.
        Only new files are transfered.
        Returns a :class:`list` of the newly transfered results files.
        """
        local_filepaths = []

        try:
            ftp = self._client.open_sftp()

            for remote_filepath in \
                    fnmatch.filter(ftp.listdir(self._remote_workdir), '*.h5'):
                filename = os.path.basename(remote_filepath)
                local_filepath = os.path.join(self._local_outputdir, filename)
                if os.path.exists(local_filepath):
                    continue

                logging.debug('Transferring %s', remote_filepath)
                ftp.get(remote_filepath, local_filepath)

                local_filepaths.append(local_filepath)
                logging.debug('Transfered results to %s', local_filepath)
        finally:
            ftp.close()

        return local_filepaths

    def _launch_simulations(self, remote_filepaths):
        """
        Launches the simulations.
        Returns a set of job ids corresponding to the submitted simulations.
        
        :arg remote_filepaths: location of options file (.xml) on the 
            remote host
        
        :return: job ids of the submitted simulations
        :rtype: :class:`set`
        """
        raise NotImplementedError

    def _progress_simulations(self, jobids):
        """
        Returns the progress of the simulations with the specified job ids.
        The progress is returned as three :class:`set`:
        
            * pending job ids
            * running job ids
            * completed or exited job ids
        
        :arg jobids: :class:`set` containing the job ids of the 
            submitted simulations
        """
        raise NotImplementedError

    def _stop_simulations(self, jobids):
        """
        Stops the specified simulations.
        
        :arg jobids: :class:`set` containing the job ids of the 
            submitted simulations
        """
        raise NotImplementedError

    def stop(self):
        self._stop_simulations(self._jobids)
        self._jobids.clear()
        self._client.close()
        _Dispatcher.stop(self)

    def report(self):
        pending, running, _ = self._progress_simulations(self._jobids)
        return len(running) / float(len(pending) + len(running))

class _PlatformLSFRemoteDispatcher(_RemoteDispatcher):

    _JOBID_PATTERN = re.compile('<(\d+)>')

    def __init__(self, program, queue_options, queue_results,
                 connection_dict, remote_workdir, local_outputdir,
                 runtime_limit=datetime.timedelta(minutes=15),
                 memory_limit=1024, email=None):
        _RemoteDispatcher.__init__(self, program, queue_options, queue_results,
                                   connection_dict, remote_workdir, local_outputdir)

        if runtime_limit > datetime.timedelta(days=1):
            raise ValueError, "Run time must be less than 24 hours"
        self._runtime_limit = runtime_limit
        self._memory_limit = memory_limit
        self._email = email

    def _create_bsub(self, remote_filepath):
        s = []

        # Header
        s += ['#!/bin/bash']
        s += ['#BSUB -J pymontecarlo']
        s += ['#BSUB -o pymontecarlo_%J.out']
        hours = self._runtime_limit.seconds // 3600
        minutes = (self._runtime_limit.seconds // 3600) % 60
        s += ['#BSUB -W %i:%i' % (hours, minutes)]
        s += ['#BSUB -M %i' % self._memory_limit]
        if self._email:
            s += ['#BSUB -u %s' % self._email]
            s += ['#BSUB -N']
        s += ['module load python/2.7.1']

        # Command
        remote_dirpath = posixpath.dirname(remote_filepath)
        s += ['cd %s' % remote_dirpath]
        s += ['pymontecarlo-cli -v -s -q -n 1 --%s -o "%s" "%s"' % \
                (self._program.alias, remote_dirpath, remote_filepath)]

        return '\n'.join(s)

    def _launch_simulations(self, remote_filepaths):
        jobids = set()

        try:
            ftp = self._client.open_sftp()

            for remote_filepath in remote_filepaths:
                bsub_data = self._create_bsub(remote_filepath)
                bsub_filepath = posixpath.splitext(remote_filepath)[0] + '.lsf'
                ftp.open(bsub_filepath, 'w').write(bsub_data)

                command = 'bsub < %s' % bsub_filepath
                _, stdout, _ = self._client.exec_command(command)

                stdout = list(stdout)
                if not stdout:
                    raise IOError, "Problem in submitting job"

                jobid = int(self._JOBID_PATTERN.findall(stdout[0])[0])
                jobids.add(jobid)
                self._jobids.add(jobid) # Add to allow job kill on exception
        finally:
            ftp.close()

        return jobids

    def _progress_simulations(self, jobids):
        pending = set()
        running = set()
        completed = set()

        for jobid in jobids:
            command = 'bjobs -w %i' % jobid
            _, stdout, stderr = self._client.exec_command(command)

            stdout = list(stdout)
            stderr = list(stderr)

            if not stdout and stderr:
                completed.add(jobid)
            elif stdout:
                status = stdout[1].split()[2]
                if status == 'PEND':
                    pending.add(jobid)
                elif status == 'RUN':
                    running.add(jobid)
                elif status == 'EXIT':
                    completed.add(jobid)

        return pending, running, completed

    def _stop_simulations(self, jobids):
        command = 'bkill ' + ' '.join(map(str, jobids))
        self._client.exec_command(command)

class _RemoteRunner(_Runner):

    def __init__(self, program, connection_dict, remote_workdir, local_outputdir,
                 dispatcher_class, **dispatcher_kwargs):
        _Runner.__init__(self, program)

        self._local_outputdir = local_outputdir

        self._dispatcher = \
            dispatcher_class(program, self._queue_options, self._queue_results,
                             connection_dict, remote_workdir, local_outputdir,
                             **dispatcher_kwargs)
        self._dispatcher.daemon = True

    @property
    def outputdir(self):
        return self._local_outputdir

    def start(self):
        self._dispatcher.start()

    def stop(self):
        self._dispatcher.stop()

class PlatformLSFRemoteRunner(_RemoteRunner):

    def __init__(self, program, connection_dict, remote_workdir, local_outputdir,
                 runtime_limit=datetime.timedelta(minutes=15),
                 memory_limit=1024, email=None):
        _RemoteRunner.__init__(self, program, connection_dict,
                               remote_workdir, local_outputdir,
                               _PlatformLSFRemoteDispatcher)
