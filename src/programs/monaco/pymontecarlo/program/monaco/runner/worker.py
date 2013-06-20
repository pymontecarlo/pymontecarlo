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
from pymontecarlo.settings import get_settings

from pymontecarlo.runner.worker import SubprocessWorker as _Worker

from pymontecarlo.input.detector import PhotonIntensityDetector, PhotonDepthDetector

from pymontecarlo.util.transition import Ka, La, Ma

from pymontecarlo.program.monaco.input.converter import Converter
from pymontecarlo.program.monaco.input.exporter import Exporter
from pymontecarlo.program.monaco.output.importer import Importer

# Globals and constants variables.
from pymontecarlo.input.model import \
    (MASS_ABSORPTION_COEFFICIENT, IONIZATION_CROSS_SECTION,
     IONIZATION_POTENTIAL)

_WINKEY = r'Software\GfE\Monaco\3.0'

_MASS_ABSORPTION_COEFFICIENT_REF = \
    {MASS_ABSORPTION_COEFFICIENT.bastin_heijligers1989: 1,
     MASS_ABSORPTION_COEFFICIENT.henke1982: 2}

_IONIZATION_CROSS_SECTION_REF = \
    {IONIZATION_CROSS_SECTION.gryzinsky_bethe: 1,
     IONIZATION_CROSS_SECTION.gryzinsky: 2,
     IONIZATION_CROSS_SECTION.hutchins1974: 3,
     IONIZATION_CROSS_SECTION.worthington_tomlin1956: 4}

_IONIZATION_POTENTIAL_REF = \
    {IONIZATION_POTENTIAL.duncumb_decasa1969: 1,
     IONIZATION_POTENTIAL.gryzinski: 2,
     IONIZATION_POTENTIAL.springer1967: 3,
     IONIZATION_POTENTIAL.sternheimer1964: 4}

class Worker(_Worker):
    def __init__(self):
        """
        Runner to run Monaco simulation(s).
        """
        _Worker.__init__(self)

        self._monaco_basedir = get_settings().monaco.basedir
        self._mccli32exe = os.path.join(self._monaco_basedir, 'Mccli32.exe')

    def create(self, options, outputdir, createdir=True):
        # Convert
        Converter().convert(options)

        # Create job directory
        if createdir:
            jobdir = os.path.join(outputdir, options.name)
            if os.path.exists(jobdir):
                logging.info('Job directory (%s) already exists, so it is removed.', jobdir)
                shutil.rmtree(jobdir)
            os.makedirs(jobdir)
        else:
            jobdir = outputdir

        # Export: create MAT and SIM files
        Exporter().export(options, jobdir)

        return jobdir

    def _setup_registry(self):
        try:
            key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, _WINKEY,
                                  0, _winreg.KEY_ALL_ACCESS)
        except:
            key = _winreg.CreateKey(_winreg.HKEY_CURRENT_USER, _WINKEY)
        with key:
            _winreg.SetValueEx(key, "SysPath", 0, _winreg.REG_SZ,
                               self._monaco_basedir)
        logging.debug("Setup Monaco path in registry")

    def run(self, options, outputdir, workdir):
        # Setup registry (in case it is not already set)
        self._setup_registry()

        # Create job directory and simulation files
        self.create(options, workdir, False)

        # Run simulation (in batch)
        self._run_simulation(options, workdir)

        # Extract transitions
        transitions = self._extract_transitions(options)

        # Extract intensities if photon intensity detectors
        detectors = options.detectors.findall(PhotonIntensityDetector)
        for detector_key, detector in detectors.iteritems():
            self._run_intensities(workdir, options, detector_key, detector,
                                  transitions)

        # Extract phi-rho-zs if phi-rho-z detectors
        detectors = options.detectors.findall(PhotonDepthDetector)
        for detector_key, detector in detectors.iteritems():
            self._run_phirhozs(workdir, options, detector_key, detector,
                               transitions)

        return self._extract_results(options, outputdir, workdir)

    def _run_simulation(self, options, workdir):
        mat_filepath = os.path.join(workdir, options.name + '.MAT')
        sim_filepath = os.path.join(workdir, options.name + '.SIM')
        args = [self._mccli32exe, 'sim', mat_filepath, sim_filepath, workdir]
        logging.debug('Launching %s', ' '.join(args))

        self._status = "Running Monaco's mccli32.exe"

        self._process = subprocess.Popen(args, stdout=subprocess.PIPE,
                                         cwd=self._monaco_basedir)
        self._process.wait()
        self._process = None

        logging.debug("Monaco's mccli32.exe ended")

        # Check that simulation ran
        nez_filepath = os.path.join(workdir, 'NEZ.1')
        if not os.path.exists(nez_filepath):
            raise RuntimeError, 'Simulation did not run properly'

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

                if transition.most_probable.dest.ionization_energy_eV < options.beam.energy_eV:
                    transitions.append(str(transition))

        return transitions

    def _run_intensities(self, workdir, options, detector_key, detector,
                         transitions):
        # Paths
        mat_filepath = os.path.join(workdir, options.name + '.MAT')
        sim_filepath = os.path.join(workdir, options.name + '.SIM')
        nez_filepath = os.path.join(workdir, 'NEZ.1')

        # Find models
        model = options.models.find(MASS_ABSORPTION_COEFFICIENT.type)
        mac_id = _MASS_ABSORPTION_COEFFICIENT_REF.get(model, 0)

        model = options.models.find(IONIZATION_CROSS_SECTION.type)
        ics_id = _IONIZATION_CROSS_SECTION_REF.get(model, 0)

        model = options.models.find(IONIZATION_POTENTIAL.type)
        ip_id = _IONIZATION_POTENTIAL_REF.get(model, 0)

        # Launch mccli32.exe
        args = [self._mccli32exe, "int",
                mat_filepath, sim_filepath, nez_filepath, workdir,
                detector.takeoffangle_deg, mac_id, ics_id, ip_id]
        args += transitions
        args = map(str, args)
        logging.debug('Launching %s', ' '.join(args))

        self._status = "Running Monaco's mccli32.exe"

        self._process = subprocess.Popen(args, stdout=subprocess.PIPE,
                                         cwd=self._monaco_basedir)
        self._process.wait()
        self._process = None

        logging.debug("Monaco's mccli32.exe ended")

        # Rename intensities.txt
        src_filepath = os.path.join(workdir, 'intensities.csv')
        if not os.path.exists(src_filepath):
            raise RuntimeError, 'Could not extract intensities'

        dst_filepath = os.path.join(workdir, 'intensities_%s.csv' % detector_key)
        shutil.move(src_filepath, dst_filepath)
        logging.debug("Appending detector key to intensities.csv")

    def _run_phirhozs(self, workdir, options, detector_key, detector,
                      transitions):
        # Paths
        mat_filepath = os.path.join(workdir, options.name + '.MAT')
        sim_filepath = os.path.join(workdir, options.name + '.SIM')
        nez_filepath = os.path.join(workdir, 'NEZ.1')

        # Find models
        model = options.models.find(MASS_ABSORPTION_COEFFICIENT.type)
        mac_id = _MASS_ABSORPTION_COEFFICIENT_REF.get(model, 0)

        model = options.models.find(IONIZATION_CROSS_SECTION.type)
        ics_id = _IONIZATION_CROSS_SECTION_REF.get(model, 0)

        model = options.models.find(IONIZATION_POTENTIAL.type)
        ip_id = _IONIZATION_POTENTIAL_REF.get(model, 0)

        # Launch mccli32.exe
        args = [self._mccli32exe, "phi",
                mat_filepath, sim_filepath, nez_filepath, workdir,
                detector.takeoffangle_deg, mac_id, ics_id, ip_id]
        args += transitions
        args = map(str, args)
        logging.debug('Launching %s', ' '.join(args))

        self._status = "Running Monaco's mccli32.exe"

        self._process = subprocess.Popen(args, stdout=subprocess.PIPE,
                                         cwd=self._monaco_basedir)
        self._process.wait()
        self._process = None

        logging.debug("Monaco's mccli32.exe ended")

        # Rename intensities.txt
        src_filepath = os.path.join(workdir, 'phi.csv')
        if not os.path.exists(src_filepath):
            raise RuntimeError, 'Could not extract phi-rho-z'

        dst_filepath = os.path.join(workdir, 'phi_%s.csv' % detector_key)
        shutil.move(src_filepath, dst_filepath)
        logging.debug("Appending detector key to phi.csv")

    def _extract_results(self, options, outputdir, workdir):
        return Importer().import_from_dir(options, workdir)

