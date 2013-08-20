#!/usr/bin/env python
"""
================================================================================
:mod:`converter` -- WinX-Ray conversion from base options
================================================================================

.. module:: converter
   :synopsis: WinX-Ray conversion from base options

.. inheritance-diagram:: pymontecarlo.program.winxray.input.converter

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
from pymontecarlo.input.converter import Converter as _Converter

from pymontecarlo.input.particle import ELECTRON
from pymontecarlo.input.beam import PencilBeam, GaussianBeam
from pymontecarlo.input.geometry import Substrate
from pymontecarlo.input.limit import ShowersLimit
from pymontecarlo.input.detector import \
    (BackscatteredElectronEnergyDetector,
     BackscatteredElectronPolarAngularDetector,
     PhotonDepthDetector,
     PhotonIntensityDetector,
     PhotonSpectrumDetector,
     ElectronFractionDetector,
     TimeDetector,
     ShowersStatisticsDetector,
     )
from pymontecarlo.input.model import \
    (ELASTIC_CROSS_SECTION, IONIZATION_CROSS_SECTION, IONIZATION_POTENTIAL,
     RANDOM_NUMBER_GENERATOR, DIRECTION_COSINE, ENERGY_LOSS,
     MASS_ABSORPTION_COEFFICIENT)
from pymontecarlo.input.expander import ExpanderSingleDetectorSameOpening

# Globals and constants variables.

class Converter(_Converter):
    BEAMS = [GaussianBeam]
    GEOMETRIES = [Substrate]
    DETECTORS = [BackscatteredElectronEnergyDetector,
                 BackscatteredElectronPolarAngularDetector,
                 PhotonDepthDetector,
                 PhotonIntensityDetector,
                 PhotonSpectrumDetector,
                 ElectronFractionDetector,
                 TimeDetector,
                 ShowersStatisticsDetector]
    LIMITS = [ShowersLimit]
    MODELS = {ELASTIC_CROSS_SECTION: [ELASTIC_CROSS_SECTION.mott_czyzewski1990,
                                           ELASTIC_CROSS_SECTION.mott_czyzewski1990_linear,
                                           ELASTIC_CROSS_SECTION.mott_czyzewski1990_powerlaw,
                                           ELASTIC_CROSS_SECTION.mott_czyzewski1990_cubicspline,
                                           ELASTIC_CROSS_SECTION.mott_demers,
                                           ELASTIC_CROSS_SECTION.rutherford,
                                           ELASTIC_CROSS_SECTION.rutherford_relativistic],
              IONIZATION_CROSS_SECTION: [IONIZATION_CROSS_SECTION.casnati1982],
              IONIZATION_POTENTIAL: [IONIZATION_POTENTIAL.joy_luo1989],
              RANDOM_NUMBER_GENERATOR: [RANDOM_NUMBER_GENERATOR.press1966_rand1,
                                             RANDOM_NUMBER_GENERATOR.press1966_rand2,
                                             RANDOM_NUMBER_GENERATOR.press1966_rand3,
                                             RANDOM_NUMBER_GENERATOR.press1966_rand4],
              DIRECTION_COSINE: [DIRECTION_COSINE.demers2000],
              ENERGY_LOSS: [ENERGY_LOSS.joy_luo1989],
              MASS_ABSORPTION_COEFFICIENT: [MASS_ABSORPTION_COEFFICIENT.heinrich_ixcom11,
                                                 MASS_ABSORPTION_COEFFICIENT.henke1993,
                                                 MASS_ABSORPTION_COEFFICIENT.thinh_leroux1979]}
    DEFAULT_MODELS = {ELASTIC_CROSS_SECTION: ELASTIC_CROSS_SECTION.mott_czyzewski1990,
                      IONIZATION_CROSS_SECTION: IONIZATION_CROSS_SECTION.casnati1982,
                      IONIZATION_POTENTIAL: IONIZATION_POTENTIAL.joy_luo1989,
                      RANDOM_NUMBER_GENERATOR: RANDOM_NUMBER_GENERATOR.press1966_rand3,
                      DIRECTION_COSINE: DIRECTION_COSINE.demers2000,
                      ENERGY_LOSS: ENERGY_LOSS.joy_luo1989,
                      MASS_ABSORPTION_COEFFICIENT: MASS_ABSORPTION_COEFFICIENT.henke1993}

    def __init__(self):
        _Converter.__init__(self)

        self._expander = ExpanderSingleDetectorSameOpening(self.DETECTORS)

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
