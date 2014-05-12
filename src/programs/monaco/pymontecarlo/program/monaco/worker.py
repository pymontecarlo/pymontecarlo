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
    import winreg
except ImportError:
    import pymontecarlo.program.monaco.dummy_winreg as winreg

# Third party modules.
from pyxray.transition import Ka, La, Ma

# Local modules.
from pymontecarlo.settings import get_settings

from pymontecarlo.program.worker import SubprocessWorker as _Worker

from pymontecarlo.options.detector import PhotonIntensityDetector, PhotonDepthDetector

# Globals and constants variables.
from pymontecarlo.options.model import \
    (MASS_ABSORPTION_COEFFICIENT, IONIZATION_CROSS_SECTION,
     IONIZATION_POTENTIAL)

_WINKEY = 'Software\\GfE\\Monaco\\3.0'

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

    def __init__(self, program):
        """
        Runner to run Monaco simulation(s).
        """
        _Worker.__init__(self, program)

        self._monaco_basedir = get_settings().monaco.basedir

        try:
            self._mccli32exe = get_settings().monaco.exe
        except AttributeError:
            self._mccli32exe = os.path.join(self._monaco_basedir, 'Mccli32.exe')

    def create(self, options, outputdir, *args, **kwargs):
        # Create job directory
        if kwargs.get('createdir', True):
            jobdir = os.path.join(outputdir, options.name)
            if os.path.exists(jobdir):
                logging.info('Job directory (%s) already exists, so it is removed.', jobdir)
                shutil.rmtree(jobdir)
            os.makedirs(jobdir)
        else:
            jobdir = outputdir

        return _Worker.create(self, options, jobdir, *args, **kwargs)

    def _setup_registry(self):
        try:
            handle = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _WINKEY,
                                  0, winreg.KEY_ALL_ACCESS)
        except:
            handle = winreg.CreateKey(winreg.HKEY_CURRENT_USER, _WINKEY)
        with handle:
            winreg.SetValueEx(handle, "SysPath", 0, winreg.REG_SZ,
                               self._monaco_basedir)
        logging.debug("Setup Monaco path in registry")

    def run(self, options, outputdir, workdir, *args, **kwargs):
        # Setup registry (in case it is not already set)
        self._setup_registry()

        # Create job directory and simulation files
        self.create(options, workdir, createdir=False)

        # Run simulation (in batch)
        self._run_simulation(options, workdir)

        # Extract transitions
        transitions = self._extract_transitions(options)

        # Extract intensities if photon intensity detectors
        detectors = options.detectors.iterclass(PhotonIntensityDetector)
        for detector_key, detector in detectors:
            self._run_intensities(workdir, options, detector_key, detector,
                                  transitions)

        # Extract phi-rho-zs if phi-rho-z detectors
        detectors = options.detectors.iterclass(PhotonDepthDetector)
        for detector_key, detector in detectors:
            self._run_phirhozs(workdir, options, detector_key, detector,
                               transitions)

        return self._importer.import_(options, workdir)

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
            raise RuntimeError('Simulation did not run properly')

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
        model = list(options.models.iterclass(MASS_ABSORPTION_COEFFICIENT))[0]
        mac_id = _MASS_ABSORPTION_COEFFICIENT_REF.get(model, 0)

        model = list(options.models.iterclass(IONIZATION_CROSS_SECTION))[0]
        ics_id = _IONIZATION_CROSS_SECTION_REF.get(model, 0)

        model = list(options.models.iterclass(IONIZATION_POTENTIAL))[0]
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
            raise RuntimeError('Could not extract intensities')

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
        model = options.models.find(MASS_ABSORPTION_COEFFICIENT)
        mac_id = _MASS_ABSORPTION_COEFFICIENT_REF.get(model, 0)

        model = options.models.find(IONIZATION_CROSS_SECTION)
        ics_id = _IONIZATION_CROSS_SECTION_REF.get(model, 0)

        model = options.models.find(IONIZATION_POTENTIAL)
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
            raise RuntimeError('Could not extract phi-rho-z')

        dst_filepath = os.path.join(workdir, 'phi_%s.csv' % detector_key)
        shutil.move(src_filepath, dst_filepath)
        logging.debug("Appending detector key to phi.csv")

