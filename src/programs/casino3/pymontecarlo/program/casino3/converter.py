#!/usr/bin/env python
"""
================================================================================
:mod:`converter` -- Casino 3 conversion from base options
================================================================================

.. module:: converter
   :synopsis: Casino 3 conversion from base options

.. inheritance-diagram:: pymontecarlo.program.casino3.input.converter

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.program.converter import Converter as _Converter

from pymontecarlo.options.beam import GaussianBeam, PencilBeam
from pymontecarlo.options.geometry import Substrate, HorizontalLayers
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.options.detector import TrajectoryDetector, ElectronFractionDetector
from pymontecarlo.options.model import \
    (ELASTIC_CROSS_SECTION, IONIZATION_POTENTIAL,
     RANDOM_NUMBER_GENERATOR, DIRECTION_COSINE, ENERGY_LOSS)

# Globals and constants variables.
from pymontecarlo.options.particle import ELECTRON

class Converter(_Converter):
    BEAMS = [GaussianBeam]
    GEOMETRIES = [Substrate, HorizontalLayers]
    DETECTORS = [TrajectoryDetector, ElectronFractionDetector]
    LIMITS = [ShowersLimit]
    MODELS = {ELASTIC_CROSS_SECTION: [ELASTIC_CROSS_SECTION.mott_czyzewski1990,
                                           ELASTIC_CROSS_SECTION.mott_drouin1993,
                                           ELASTIC_CROSS_SECTION.mott_browning1994,
                                           ELASTIC_CROSS_SECTION.rutherford,
                                           ELASTIC_CROSS_SECTION.elsepa2005,
                                           ELASTIC_CROSS_SECTION.reimer],
              IONIZATION_POTENTIAL: [IONIZATION_POTENTIAL.joy_luo1989,
                                     IONIZATION_POTENTIAL.hovington,
                                     IONIZATION_POTENTIAL.berger_seltzer1964],
              RANDOM_NUMBER_GENERATOR: [RANDOM_NUMBER_GENERATOR.lagged_fibonacci,
                                        RANDOM_NUMBER_GENERATOR.mersenne],
              DIRECTION_COSINE: [DIRECTION_COSINE.lowney1994],
              ENERGY_LOSS: [ENERGY_LOSS.joy_luo_lowney]}
    DEFAULT_MODELS = {ELASTIC_CROSS_SECTION: ELASTIC_CROSS_SECTION.elsepa2005,
                      IONIZATION_POTENTIAL: IONIZATION_POTENTIAL.joy_luo1989,
                      RANDOM_NUMBER_GENERATOR: RANDOM_NUMBER_GENERATOR.lagged_fibonacci,
                      DIRECTION_COSINE: DIRECTION_COSINE.lowney1994,
                      ENERGY_LOSS: ENERGY_LOSS.joy_luo_lowney}

    def _convert_beam(self, options):
        if type(options.beam) is PencilBeam:
            old = options.beam
            options.beam = GaussianBeam(old.energy_eV, 0.0, old.particle,
                                        old.origin_m, old.direction,
                                        old.aperture_rad)

            self._warn("Pencil beam converted to Gaussian beam with 0 m diameter")

        if not _Converter._convert_beam(self, options):
            return False

        if options.beam.particle is not ELECTRON:
            self._warn("Beam particle must be ELECTRON",
                       "This options definition was removed.")
            return False

        if options.beam.energy_eV > 1e6:
            self._warn("Beam energy must be less than 1MeV",
                       "This options definition was removed.")
            return False

        if options.beam.aperture_rad != 0.0:
            self._warn('Beam aperture is not supported.'
                       "This options definition was removed.")
            return False

        return True

    def _convert_limits(self, options):
        if not _Converter._convert_limits(self, options):
            return False

        limits = list(options.limits.iterclass(ShowersLimit))
        if not limits:
            self._warn("A ShowersLimit must be defined.",
                       "This options definition was removed.")
            return False

        return True

