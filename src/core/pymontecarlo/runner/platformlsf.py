#!/usr/bin/env python
"""
================================================================================
:mod:`platformlsf` -- Runner for high performance cluster Platform LSF
================================================================================

.. module:: platformlsf
   :synopsis: Runner for high performance cluster Platform LSF

.. inheritance-diagram:: pymontecarlo.runner.platformlsf

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import re
import posixpath
from datetime import timedelta
import logging

# Third party modules.

# Local modules.
from pymontecarlo.runner.remote import _RemoteRunner, _RemoteRunnerDispatcher

# Globals and constants variables.

class _PlatformLSFRemoteDispatcher(_RemoteRunnerDispatcher):

    _JOBID_PATTERN = re.compile('<(\d+)>')

    def __init__(self, program, queue_options, queue_results,
                 connection_dict, remote_workdir, local_outputdir,
                 runtime_limit=timedelta(minutes=15),
                 memory_limit=1024, email=None):
        _RemoteRunnerDispatcher.__init__(self, program, queue_options, queue_results,
                                   connection_dict, remote_workdir, local_outputdir)

        if runtime_limit > timedelta(days=1):
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
                logging.debug('"%s" sent', command)

                stdout = list(stdout)
                if not stdout:
                    raise IOError, "Problem in submitting job"

                jobid = int(self._JOBID_PATTERN.findall(stdout[0])[0])
                logging.debug("jobid: %i", jobid)
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

class PlatformLSFRemoteRunner(_RemoteRunner):

    def __init__(self, program, connection_dict, remote_workdir, local_outputdir,
                 runtime_limit=timedelta(minutes=15),
                 memory_limit=1024, email=None):
        _RemoteRunner.__init__(self, program, connection_dict,
                               remote_workdir, local_outputdir,
                               _PlatformLSFRemoteDispatcher)

