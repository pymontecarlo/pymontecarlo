#!/usr/bin/env python
"""
================================================================================
:mod:`converter` -- Casino conversion from base options
================================================================================

.. module:: converter
   :synopsis: Casino conversion from base options

.. inheritance-diagram:: pymontecarlo.program.casino2.input.converter

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

from pymontecarlo.options.particle import ELECTRON
from pymontecarlo.options.beam import PencilBeam, GaussianBeam
from pymontecarlo.options.geometry import \
    Substrate, HorizontalLayers, VerticalLayers
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.options.detector import \
    (BackscatteredElectronEnergyDetector,
     BackscatteredElectronPolarAngularDetector,
     BackscatteredElectronRadialDetector,
     PhotonDepthDetector,
     PhotonRadialDetector,
     PhotonIntensityDetector,
     TransmittedElectronEnergyDetector,
     ElectronFractionDetector,
     TrajectoryDetector,
     )
from pymontecarlo.options.model import \
    (ELASTIC_CROSS_SECTION, IONIZATION_CROSS_SECTION, IONIZATION_POTENTIAL,
     RANDOM_NUMBER_GENERATOR, DIRECTION_COSINE, ENERGY_LOSS,
     MASS_ABSORPTION_COEFFICIENT)
from pymontecarlo.util.expander import ExpanderSingleDetectorSameOpening

# Globals and constants variables.

class Converter(_Converter):
    BEAMS = [GaussianBeam]
    GEOMETRIES = [Substrate, HorizontalLayers, VerticalLayers]
    DETECTORS = [BackscatteredElectronEnergyDetector,
                 TransmittedElectronEnergyDetector,
                 BackscatteredElectronPolarAngularDetector,
                 BackscatteredElectronRadialDetector,
                 ElectronFractionDetector,
                 PhotonDepthDetector,
                 PhotonRadialDetector,
                 PhotonIntensityDetector,
                 TrajectoryDetector]
    LIMITS = [ShowersLimit]
    MODELS = {ELASTIC_CROSS_SECTION: [ELASTIC_CROSS_SECTION.mott_czyzewski1990,
                                      ELASTIC_CROSS_SECTION.mott_drouin1993,
                                      ELASTIC_CROSS_SECTION.mott_browning1994,
                                      ELASTIC_CROSS_SECTION.rutherford],
              IONIZATION_CROSS_SECTION: [IONIZATION_CROSS_SECTION.pouchou1986,
                                         IONIZATION_CROSS_SECTION.brown_powell,
                                         IONIZATION_CROSS_SECTION.casnati1982,
                                         IONIZATION_CROSS_SECTION.gryzinsky,
                                         IONIZATION_CROSS_SECTION.jakoby],
              IONIZATION_POTENTIAL: [IONIZATION_POTENTIAL.joy_luo1989,
                                     IONIZATION_POTENTIAL.berger_seltzer1983,
                                     IONIZATION_POTENTIAL.hovington],
              RANDOM_NUMBER_GENERATOR: [RANDOM_NUMBER_GENERATOR.press1966_rand1,
                                        RANDOM_NUMBER_GENERATOR.mersenne],
              DIRECTION_COSINE: [DIRECTION_COSINE.soum1979,
                                 DIRECTION_COSINE.drouin1996],
              ENERGY_LOSS: [ENERGY_LOSS.joy_luo1989],
              MASS_ABSORPTION_COEFFICIENT: [MASS_ABSORPTION_COEFFICIENT.heinrich_ixcom11]}
    DEFAULT_MODELS = {ELASTIC_CROSS_SECTION: ELASTIC_CROSS_SECTION.mott_czyzewski1990,
                      IONIZATION_CROSS_SECTION: IONIZATION_CROSS_SECTION.casnati1982,
                      IONIZATION_POTENTIAL: IONIZATION_POTENTIAL.joy_luo1989,
                      RANDOM_NUMBER_GENERATOR: RANDOM_NUMBER_GENERATOR.press1966_rand1,
                      DIRECTION_COSINE: DIRECTION_COSINE.drouin1996,
                      ENERGY_LOSS: ENERGY_LOSS.joy_luo1989,
                      MASS_ABSORPTION_COEFFICIENT: MASS_ABSORPTION_COEFFICIENT.heinrich_ixcom11}

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

        if options.beam.energy_eV > 1e6:
            self._warn("Beam energy must be less than 1MeV",
                       "This options definition was removed.")
            return False

        if options.beam.aperture_rad != 0.0:
            self._warn('Beam aperture is not supported.'
                       "This options definition was removed.")
            return False

        return True

    def _convert_geometry(self, options):
        if not _Converter._convert_geometry(self, options):
            return False

        if options.geometry.tilt_rad != 0.0:
            self._warn("Geometry tilt is not supported.",
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
