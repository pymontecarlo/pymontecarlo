#!/usr/bin/env python
"""
================================================================================
:mod:`worker` -- PAP worker
================================================================================

.. module:: worker
   :synopsis: PAP worker

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import sys
import logging
import tempfile
import time

# Third party modules.

# Local modules.
from pymontecarlo.program._pouchou.input.converter import Converter
from pymontecarlo.runner.worker import Worker as _Worker
from pymontecarlo.util.config import ConfigParser
from pymontecarlo.util.transition import get_transitions
from pymontecarlo.input.model import MASS_ABSORPTION_COEFFICIENT
from pymontecarlo.input.detector import \
    PhotonIntensityDetector, PhotonDepthDetector, TimeDetector
from pymontecarlo.output.result import \
    (PhotonIntensityResult, PhotonDepthResult, TimeResult,
     create_intensity_dict, create_photondist_dict)
from pymontecarlo.output.results import Results

from PouchouPichoirModels.models.XRayTransition import XRayTransition
from SpecimenTools.Element import Element

# Globals and constants variables.
_MACMODELS = {MASS_ABSORPTION_COEFFICIENT.henke1993: 'Henke1993',
              MASS_ABSORPTION_COEFFICIENT.heinrich_ixcom11_dtsa: 'Heinrich'}


class _PouchouWorker(_Worker):
    _MODEL_CLASS = None

    def _create_configuration_file(self):
        """
        Creates a configuration file required to run simulation and returns
        its filepath.
        """
        # Find location of data folder in pymontecarlo.program.pap
        dirname = os.path.dirname(sys.modules[__name__].__file__)
        datapath = os.path.abspath(os.path.join(dirname, '..', 'data'))

        # Create config
        config = ConfigParser()

        section = config.add_section('DTSAXRayTransitionData')
        section.pathname = datapath
        section.basename = 'XrayData'
        section.extension = '.csv'
        section.lineSuffix = 'Line'
        section.edgeSuffix = 'Edge'

        section = config.add_section('MacHenke')
        section.pathname = datapath
        section.filename = 'machenke.tar.gz'

        section = config.add_section('XRayTransitionName')
        section.pathname = datapath
        section.basename = 'XRayTransitionName'
        section.extension = '.csv'

        # Save config
        fileobj = tempfile.NamedTemporaryFile(delete=False)
        config.write(fileobj)

        return fileobj.name

    def create(self, options, outputdir):
        # Convert
        Converter().convert(options)

        # Save
        filepath = os.path.join(outputdir, options.name + '.xml')
        options.save(filepath)
        logging.debug('Save options to: %s', filepath)

        return filepath

    def run(self, options, outputdir, workdir):
        # Create configuration
        config_filepath = self._create_configuration_file()
        logging.debug("Configuration filepath: %s", config_filepath)

        # Create PAP object
        self.create(options, workdir)
        macmodel = options.models.find(MASS_ABSORPTION_COEFFICIENT.type)
        model = self._MODEL_CLASS(None, None, None, None,
                                  configurationFile=config_filepath,
                                  macModel=_MACMODELS[macmodel])

        # Prepare inputs
        energy_eV = options.beam.energy_eV
        energy_keV = energy_eV / 1000.0

        elements = []
        for z, wf in options.geometry.material.composition.iteritems(): # Substrate
            elements.append(Element(z, weightFraction=wf))

        energylow_eV = options.geometry.material.absorption_energy_photon_eV
        transitions = {}
        for z in options.geometry.material.composition.iterkeys():
            for transition in get_transitions(z, energylow_eV, energy_eV):
                try:
                    xraytransition = \
                        XRayTransition(transition.z, transition._siegbahn_nogreek,
                                       config_filepath)
                except:
                    continue

                transitions[transition] = xraytransition

        ## Compute
        start = time.time()
        results = {}

        # Intensity
        dets = options.detectors.findall(PhotonIntensityDetector)
        if dets:
            key, detector = dets.items()[0]
            intensities = self._compute_intensities(model, detector, elements,
                                                    energy_keV, transitions)
            results[key] = PhotonIntensityResult(intensities)

        dets = options.detectors.findall(PhotonDepthDetector)
        if dets:
            key, detector = dets.items()[0]
            distributions = self._compute_prz(model, detector, elements,
                                              energy_keV, transitions)
            results[key] = PhotonDepthResult(distributions)

        end = time.time()

        dets = options.detectors.findall(TimeDetector)
        if dets:
            key = dets.keys()[0]
            results[key] = TimeResult(simulation_time_s=end - start)

        # Remove configuration file
        os.remove(config_filepath)
        logging.debug("Remove configuration filepath")

        return Results(options, results)

    def _compute_intensities(self, model, detector, elements, energy_keV, transitions):
        intensities = {}

        for transition, xraytransition in transitions.iteritems():
            model.setInputParameters(elements, energy_keV, xraytransition,
                                   detector.takeoffangle_deg)
            val = model.compute()

            intensities.update(create_intensity_dict(transition,
                                                     enf=(val, 0.0),
                                                     et=(val, 0.0)))

        return intensities

    def _compute_prz(self, model, detector, elements, energy_keV, transitions):
        distributions = {}

        for transition, xraytransition in transitions.iteritems():
            model.setInputParameters(elements, energy_keV, xraytransition,
                                   detector.takeoffangle_deg)
            zs, values, _chis = model.computePhiRhoZDistribution(detector.channels)
            uncs = [0.0] * len(zs)

            distributions.update(create_photondist_dict(transition,
                                                        enf=(zs, values, uncs),
                                                        et=(zs, values, uncs)))

        return distributions
