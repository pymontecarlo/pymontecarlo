#!/usr/bin/env python
"""
================================================================================
:mod:`converter` -- Converter for Monaco program
================================================================================

.. module:: converter
   :synopsis: Converter for Monaco program

.. inheritance-diagram:: pymontecarlo.program.monaco.input.converter

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
from pymontecarlo.program.converter import Converter as _Converter

from pymontecarlo.options.particle import ELECTRON
from pymontecarlo.options.beam import PencilBeam
from pymontecarlo.options.geometry import Substrate
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.options.detector import \
    PhotonIntensityDetector, PhotonDepthDetector
from pymontecarlo.options.model import \
    (ELASTIC_CROSS_SECTION, IONIZATION_CROSS_SECTION, IONIZATION_POTENTIAL,
     ENERGY_LOSS, MASS_ABSORPTION_COEFFICIENT)

# Globals and constants variables.

class Converter(_Converter):
    BEAMS = [PencilBeam]
    GEOMETRIES = [Substrate]
    DETECTORS = [PhotonIntensityDetector, PhotonDepthDetector]
    LIMITS = [ShowersLimit]
    MODELS = {ELASTIC_CROSS_SECTION: [ELASTIC_CROSS_SECTION.mott_czyzewski1990],
              IONIZATION_CROSS_SECTION: [IONIZATION_CROSS_SECTION.gryzinsky,
                                         IONIZATION_CROSS_SECTION.gryzinsky_bethe,
                                         IONIZATION_CROSS_SECTION.worthington_tomlin1956,
                                         IONIZATION_CROSS_SECTION.hutchins1974],
              IONIZATION_POTENTIAL: [IONIZATION_POTENTIAL.springer1967,
                                     IONIZATION_POTENTIAL.duncumb_decasa1969,
                                     IONIZATION_POTENTIAL.sternheimer1964,
                                     IONIZATION_POTENTIAL.gryzinski],
              ENERGY_LOSS: [ENERGY_LOSS.bethe1930mod],
              MASS_ABSORPTION_COEFFICIENT: [MASS_ABSORPTION_COEFFICIENT.bastin_heijligers1989,
                                            MASS_ABSORPTION_COEFFICIENT.henke1982]}
    DEFAULT_MODELS = {ELASTIC_CROSS_SECTION: ELASTIC_CROSS_SECTION.mott_czyzewski1990,
                      IONIZATION_CROSS_SECTION: IONIZATION_CROSS_SECTION.gryzinsky_bethe,
                      IONIZATION_POTENTIAL: IONIZATION_POTENTIAL.springer1967,
                      ENERGY_LOSS: ENERGY_LOSS.bethe1930mod,
                      MASS_ABSORPTION_COEFFICIENT: MASS_ABSORPTION_COEFFICIENT.bastin_heijligers1989}

    def _convert_beam(self, options):
        if not _Converter._convert_beam(self, options):
            return False

        if options.beam.particle is not ELECTRON:
            self._warn("Beam particle must be ELECTRON.",
                       "This options definition was removed.")
            return False

        if options.beam.energy_eV > 400e3:
            self._warn("Beam energy must be less than 400 keV.",
                       "This options definition was removed.")
            return False

        if options.beam.aperture_rad != 0.0:
            self._warn("Monaco does not support beam aperture.",
                       "This options definition was removed.")
            return False

        return True

    def _convert_geometry(self, options):
        if not _Converter._convert_geometry(self, options):
            return False

        if options.geometry.tilt_rad != 0.0:
            self._warn("Geometry cannot be tilted in Monaco, only the beam direction.",
                       "This options definition was removed.")
            return False

        for material in options.geometry.get_materials():
            if material.absorption_energy_eV[ELECTRON] < 200.0:
                material.absorption_energy_eV[ELECTRON] = 200.0
                self._warn('Electron absorption energy below limit.',
                           'Set to 200 eV')

        return True

    def _convert_detectors(self, options):
        if not _Converter._convert_detectors(self, options):
            return False

        for _key, det in options.detectors.iterclass(PhotonDepthDetector):
            if det.channels != 128:
                self._warn("Number of channels of phi-rho-z detector set to 128")

        return True

    def _convert_limits(self, options):
        if not _Converter._convert_limits(self, options):
            return False

        limits = list(options.limits.iterclass(ShowersLimit))
        if not limits:
            self._warn("A showers limit must be defined.",
                       "This options definition was removed.")
            return False

        return True
