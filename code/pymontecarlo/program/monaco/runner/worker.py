#!/usr/bin/env python
"""
================================================================================
:mod:`worker` -- Monaco worker
================================================================================

.. module:: worker
   :synopsis: Monaco worker

.. inheritance-diagram:: pymontecarlo.program.monaco.runner.worker

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import ntpath as path
import struct
import logging
import shutil
import subprocess

try:
    import _winreg
except ImportError:
    class WinReg:
        HKEY_CURRENT_USER = None
        KEY_ALL_ACCESS = None
        REG_SZ = None

        def OpenKey(self, key, sub_key, res, sam):
            pass

        def CreateKey(self, key, sub_key):
            pass

        def SetValueEx(self, key, value_name, reserved, type, value):
            pass

    _winreg = WinReg()

# Third party modules.

# Local modules.
from pymontecarlo import get_settings

from pymontecarlo.runner.worker import SubprocessWorker as _Worker

from pymontecarlo.input.detector import PhotonIntensityDetector

from pymontecarlo.util.transition import Ka, La, Ma

from pymontecarlo.program.monaco.input.converter import Converter
from pymontecarlo.program.monaco.io.exporter import Exporter
from pymontecarlo.program.monaco.io.importer import Importer

# Globals and constants variables.
_WINKEY = r'Software\GfE\Monaco\3.0'

def _create_mcb(monaco_basedir, jobdir):
    """
    Create Monaco batch file. 
    The batch file is located in *monaco_basedir*\MCUTIL\MCBAT32.MCB.
    
    :arg monaco_basedir: base directory of Monaco program
    :arg jobdir: job directory where the SIM and MAT files are located for a
        given job
        
    :return: path to the batch file
    """
    filepath = os.path.join(monaco_basedir, 'MCUTIL', 'MCBAT32.MCB')
    with open(filepath, 'wb') as fp:
        # BStatus
        # DELPHI: BlockWrite(Bf, VersionSign, 1,f);
        fp.write(struct.pack('B', 255))

        # BVersion
        # DELPHI: BlockWrite(Bf, BVersion, SizeOf(Integer),f);
        fp.write(struct.pack('i', 1))

        # Bstatus
        # DELPHI: BlockWrite(Bf,BStatus,1,f);
        fp.write(struct.pack('b', 2))

        # Job 1 Directory
        # DELPHI: l := 1+Length(Job.Dir); Inc(s,l);BlockWrite(Bf,Job.Dir,l,w); Inc(Sum,w);
        jobdir = path.abspath(jobdir)
        fp.write(struct.pack('b', len(jobdir)))
        fp.write(jobdir)

        # Job 1 Name
        # DELPHI: l := 1+Length(Job.Smp); Inc(s,l);BlockWrite(Bf,Job.Smp,l,w); Inc(Sum,w);
        name = path.basename(jobdir)
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

    return filepath

class Worker(_Worker):
    def __init__(self, queue_options, outputdir, workdir=None, overwrite=True):
        """
        Runner to run Monaco simulation(s).
        
        .. note:: 
        
           The work directory cannot be specified for this worker as the work
           directory must be located in *monaco basedir*/PRB. 
        """
        self._monaco_basedir = get_settings().monaco.basedir
        self._mcsim32exe = os.path.join(self._monaco_basedir, 'Mcsim32.exe')
        self._mccli32exe = os.path.join(self._monaco_basedir, 'Mccli32.exe')

        workdir = os.path.join(self._monaco_basedir, 'PRB')
        _Worker.__init__(self, queue_options, outputdir, workdir, overwrite)

    def _create(self, options, dirpath):
        # Convert
        Converter().convert(options)

        # Create job directory
        jobdir = os.path.join(dirpath, options.name)
        if os.path.exists(jobdir):
            logging.info('Job directory (%s) already exists, so it is removed.', jobdir)
            shutil.rmtree(jobdir, ignore_errors=True)
        os.makedirs(jobdir)

        # Export: create MAT and SIM files
        Exporter().export(options, jobdir)

        return jobdir

    def _run(self, options):
        # Setup registry (in case it is not already set)
        try:
            key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, _WINKEY,
                                  0, _winreg.KEY_ALL_ACCESS)
        except:
            key = _winreg.CreateKey(_winreg.HKEY_CURRENT_USER, _WINKEY)
        with key:
            _winreg.SetValueEx(key, "SysPath", 0, _winreg.REG_SZ,
                               self._monaco_basedir)
        logging.debug("Setup Monaco path in registry")

        # Create job directory and simulation files
        jobdir = self._create(options, self._workdir)

        # Run simulation (in batch)
        self._run_batch(jobdir)

        # Extract transitions
        transitions = self._extract_transitions(options)

        # Extract intensities if photon intensity detectors
        detectors = options.detectors.findall(PhotonIntensityDetector).values()
        for detector in detectors:
            self._run_intensities(options, detector, transitions)

    def _run_batch(self, jobdir):
        # Create batch file
        batch_filepath = _create_mcb(self._monaco_basedir, jobdir)
        logging.debug("Creating batch file")

        # Launch mcsim32.exe
        args = [self._mcsim32exe]
        logging.debug('Launching %s', ' '.join(args))

        self._status = "Running Monaco's mcsim32.exe"

        self._process = subprocess.Popen(args, stdout=subprocess.PIPE,
                                         cwd=self._monaco_basedir)
        self._process.wait()
        self._process = None

        logging.debug("Monaco's mcsim32.exe ended")

        # Remove batch file
        os.remove(batch_filepath)
        logging.debug('Remove batch file')

    def _extract_transitions(self, options):
        zs = set()
        for material in options.geometry.get_materials():
            zs.update(material.composition.keys())

        transitions = []
        for z in sorted(zs):
            for group in [Ka, La, Ma]:
                try:
                    transition = group(z)
                except ValueError: # Does not exist
                    continue

                if transition.most_probable.energy_eV < options.beam.energy_eV:
                    transitions.append(str(transition))

        return transitions

    def _run_intensities(self, jobdir, options, detector_key, detector,
                         transitions):
        # Launch mccli32.exe
        args = [self._mccli32exe, options.name,
                str(detector.takeoffangle_deg)]
        args += transitions
        logging.debug('Launching %s', ' '.join(args))

        self._status = "Running Monaco's mccli32.exe"

        self._process = subprocess.Popen(args, stdout=subprocess.PIPE,
                                         cwd=self._monaco_basedir)
        self._process.wait()
        self._process = None

        logging.debug("Monaco's mcsim32.exe ended")

        # Rename intensities.txt
        logging.debug("Appending detector key to intensities.txt")

        src_filepath = os.path.join(jobdir, 'intensities.txt')
        dst_filepath = os.path.join(jobdir, 'intensities_%s.txt' % detector_key)
        shutil.move(src_filepath, dst_filepath)

    def _save_results(self, options, h5filepath):
        jobdir = self._get_dirpath(options)

        results = Importer().import_from_dir(options, jobdir)
        results.save(h5filepath)

    def _cleanup(self, options):
        _Worker._cleanup(self, options)

        jobdir = self._get_dirpath(options)
        shutil.rmtree(jobdir, ignore_errors=True)
