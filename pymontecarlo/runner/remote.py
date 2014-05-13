#!/usr/bin/env python
"""
================================================================================
:mod:`remote` -- Interface for remote runners
================================================================================

.. module:: remote
   :synopsis: Interface for remote runners

.. inheritance-diagram:: pymontecarlo.runner.remote

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import time
import fnmatch
import logging
import posixpath
from queue import Empty
import threading
from io import BytesIO

# Third party modules.
import paramiko

# Local modules.
from pymontecarlo.runner.base import _RunnerDispatcher, _Runner

from pymontecarlo.fileformat.results.results import load as load_results
from pymontecarlo.fileformat.options.options import save as save_options

# Globals and constants variables.

class _RemoteRunnerDispatcher(_RunnerDispatcher):

    def __init__(self, program, queue_options, queue_results,
                 connection_dict, remote_workdir, local_outputdir):
        _RunnerDispatcher.__init__(self, program, queue_options, queue_results)

        self._remote_workdir = remote_workdir
        self._local_outputdir = local_outputdir

        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._client.connect(**connection_dict)

        self._jobids = set()

        self._close_event = threading.Event()
        self._closed_event = threading.Event()

    def start(self):
        self._jobids.clear()
        _RunnerDispatcher.start(self)

    def run(self):
        while not self._close_event.is_set():
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
                    self._queue_results.put(load_results(local_filepath))

                # Delay
                time.sleep(1.0)
            except:
                self._queue_options.task_done()
                self._queue_options.raise_exception()
                self.stop()

        self._closed_event.set()

    def _transfer_options(self, options_list):
        """
        Creates options file (.xml) in work directory on remote host.
        """
        try:
            ftp = self._client.open_sftp()

            # Make work directory
            command = 'mkdir -p "%s"' % self._remote_workdir
            logging.debug('"%s" sent', command)
            _, _, stderr = self._client.exec_command(command)
            stderr = list(stderr)
            if stderr:
                raise IOError('Error while creating work directory: %s' % \
                              ''.join(stderr))

            # Transfer options
            remote_filepaths = []

            for options in options_list:
                remote_filepath = \
                    posixpath.join(self._remote_workdir, options.name + '.xml')
                buf = BytesIO()
                save_options(options, buf)
                data = buf.getvalue()

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

    def close(self):
        self.stop()
        self._close_event.set()
        self._closed_event.wait()
        self._client.close()

    def report(self):
        pending, running, _ = self._progress_simulations(self._jobids)
        return len(running) / float(len(pending) + len(running))

class _RemoteRunner(_Runner):

    def __init__(self, program, connection_dict, remote_workdir, local_outputdir,
                 dispatcher_class, **dispatcher_kwargs):
        _Runner.__init__(self, program)

        self._local_outputdir = local_outputdir

        self._dispatcher = \
            dispatcher_class(program, self._queue_options, self._queue_results,
                             connection_dict, remote_workdir, local_outputdir,
                             **dispatcher_kwargs)

    @property
    def outputdir(self):
        return self._local_outputdir

    def start(self):
        if self._dispatcher is None:
            raise RuntimeError('Runner is closed')

        if not self._dispatcher.is_alive():
            self._dispatcher.start()

        logging.debug("Runner started")

    def stop(self):
        self._dispatcher.stop()
        logging.debug("Runner stopped")

    def close(self):
        self._dispatcher.close()
        self._dispatcher = None
        logging.debug("Runner closed")
