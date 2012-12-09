#!/usr/bin/env python
"""
================================================================================
:mod:`worker` -- Casino 2 worker
================================================================================

.. module:: worker
   :synopsis: Casino 2 worker

.. inheritance-diagram:: pymontecarlo.program.casino2.runner.worker

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import struct

# Third party modules.

# Local modules.
from pymontecarlo import get_settings

from pymontecarlo.runner.worker import Worker as _Worker

# Globals and constants variables.

def _create_mcb(monaco_basedir, jobdir):
    """
    Create Monaco batch file. 
    The batch file is located in *monaco_basedir*\MCUTIL\MCBAT32.MCB.
    
    :arg monaco_basedir: base directory of Monaco program
    :arg jobdir: job directory where the SIM and MAT files are located for a
        given job
    """
    filepath = os.path.join(monaco_basedir, 'MCUTIL', 'MCBAT32.MCB')
    with open(filepath, 'wb') as fp:
        # BStatus
        # DELPHI: BlockWrite(Bf, VersionSign, 1,f);
        fp.write(struct.pack('b', 255))

        # BVersion
        # DELPHI: BlockWrite(Bf, BVersion, SizeOf(Integer),f);
        fp.write(struct.pack('i', 1))

        # Bstatus
        # DELPHI: BlockWrite(Bf,BStatus,1,f);
        fp.write(struct.pack('b', 1))

        # Job 1 Directory
        # DELPHI: l := 1+Length(Job.Dir); Inc(s,l);BlockWrite(Bf,Job.Dir,l,w); Inc(Sum,w);
        jobdir = os.path.abspath(jobdir)
        fp.write(struct.pack('b', len(jobdir)))
        fp.write(jobdir)

        # Job 1 Name
        # DELPHI: l := 1+Length(Job.Smp); Inc(s,l);BlockWrite(Bf,Job.Smp,l,w); Inc(Sum,w);
        name = os.path.basename(jobdir)
        fp.write(struct.pack('b', len(name)))
        fp.write(name)

        # Job 1 Status
        # DELPHI: l := 1; Inc(s,l);BlockWrite(Bf,Job.Status,l,w); Inc(Sum,w);
        fp.write(struct.pack('b', 3))

        # Job 1 Standard
        # DELPHI: l := 1; Inc(s,l);BlockWrite(Bf,Job.Std,l,w); Inc(Sum,w);
        fp.write(struct.pack('b', 1))

        # Job 1 Version
        # DELPHI: l := SizeOf(Integer); Inc(s,l);BlockWrite(Bf,Job.Version,l,w); Inc(Sum,w);
        fp.write(struct.pack('i', 1))

        # Job 1 DateTime
        # DELPHI: l := SizeOf(TDateTime); Inc(s,l);BlockWrite(Bf,Job.DateTime,l,w);Inc(Sum,w);
        fp.write('\x54\x9e\x3f\xd0\x53\x1c\xe4\x40')

        # Job 1 User
        # DELPHI: l := 1+Length(Job.UserStr);Inc(s,l);BlockWrite(Bf,Job.UserStr,l,w); Inc(Sum,w);
        fp.write(struct.pack('b', 3))
        fp.write('bot')

        # Job 1 Info
        # DELPHI: l := 1+Length(Job.InfoStr);Inc(s,l);BlockWrite(Bf,Job.InfoStr,l,w); Inc(Sum,w);
        fp.write('\x00')

class Worker(_Worker):
    def __init__(self, queue_options, outputdir, workdir=None, overwrite=True):
        """
        Runner to run Monaco simulation(s).
        """
        _Worker.__init__(self, queue_options, outputdir, workdir, overwrite)

        self._monaco_basedir = get_settings().monaco.basedir
