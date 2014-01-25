#!/usr/bin/env python
"""
================================================================================
:mod:`converter` -- NistMonte conversion from base options
================================================================================

.. module:: converter
   :synopsis: NistMonte conversion from base options

.. inheritance-diagram:: pymontecarlo.program.nistmonte.input.converter

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
from pymontecarlo.options.beam import GaussianBeam, PencilBeam
from pymontecarlo.options.geometry import \
    Substrate, Inclusion, HorizontalLayers, VerticalLayers
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.options.detector import \
    (
#     BackscatteredElectronAzimuthalAngularDetector,
#     BackscatteredElectronEnergyDetector,
#     BackscatteredElectronPolarAngularDetector,
     BackscatteredElectronRadialDetector,
     PhotonDepthDetector,
     PhotonRadialDetector,
     PhotonIntensityDetector,
     PhotonEmissionMapDetector,
     PhotonSpectrumDetector,
#     TransmittedElectronAzimuthalAngularDetector,
#     TransmittedElectronEnergyDetector,
#     TransmittedElectronPolarAngularDetector,
     TimeDetector,
     TrajectoryDetector,
#     ElectronFractionDetector
     )
from pymontecarlo.options.model import \
    (ELASTIC_CROSS_SECTION, IONIZATION_CROSS_SECTION, IONIZATION_POTENTIAL,
     ENERGY_LOSS, MASS_ABSORPTION_COEFFICIENT, FLUORESCENCE)

# Globals and constants variables.

class Converter(_Converter):
    """
    Converter for NistMonte simulation.
    """

    BEAMS = [GaussianBeam, PencilBeam]
    GEOMETRIES = [Substrate, Inclusion, HorizontalLayers, VerticalLayers]
    DETECTORS = [
                 #BackscatteredElectronAzimuthalAngularDetector,
                 #BackscatteredElectronEnergyDetector,
                 #BackscatteredElectronPolarAngularDetector,
                 #EnergyDepositedSpatialDetector,
                 BackscatteredElectronRadialDetector,
                 PhotonDepthDetector,
                 PhotonRadialDetector,
                 PhotonIntensityDetector,
                 PhotonEmissionMapDetector,
                 PhotonSpectrumDetector,
                 #TransmittedElectronAzimuthalAngularDetector,
                 #TransmittedElectronEnergyDetector,
                 #TransmittedElectronPolarAngularDetector,
                 TimeDetector,
                 TrajectoryDetector,
                 #ElectronFractionDetector
                 ]
    LIMITS = [ShowersLimit]
    MODELS = {ELASTIC_CROSS_SECTION: [ELASTIC_CROSS_SECTION.mott_czyzewski1990,
                                      ELASTIC_CROSS_SECTION.rutherford,
                                      ELASTIC_CROSS_SECTION.elsepa2005],
              IONIZATION_CROSS_SECTION: [IONIZATION_CROSS_SECTION.bote_salvat2008,
                                         IONIZATION_CROSS_SECTION.casnati1982,
                                         IONIZATION_CROSS_SECTION.dijkstra_heijliger1998,
                                         IONIZATION_CROSS_SECTION.pouchou1986],
              IONIZATION_POTENTIAL: [IONIZATION_POTENTIAL.berger_seltzer1964,
                                     IONIZATION_POTENTIAL.berger_seltzer1983,
                                     IONIZATION_POTENTIAL.berger_seltzer1983_citzaf,
                                     IONIZATION_POTENTIAL.bloch1933,
                                     IONIZATION_POTENTIAL.duncumb_decasa1969,
                                     IONIZATION_POTENTIAL.heinrich_yakowitz1970,
                                     IONIZATION_POTENTIAL.springer1967,
                                     IONIZATION_POTENTIAL.sternheimer1964,
                                     IONIZATION_POTENTIAL.wilson1941,
                                     IONIZATION_POTENTIAL.zeller1975],
              ENERGY_LOSS: [ENERGY_LOSS.joy_luo1989,
                            ENERGY_LOSS.bethe1930,
                            ENERGY_LOSS.bethe1930mod],
              MASS_ABSORPTION_COEFFICIENT: [MASS_ABSORPTION_COEFFICIENT.chantler2005,
                                            MASS_ABSORPTION_COEFFICIENT.heinrich_ixcom11,
                                            MASS_ABSORPTION_COEFFICIENT.heinrich_ixcom11_dtsa,
                                            MASS_ABSORPTION_COEFFICIENT.henke1993,
                                            MASS_ABSORPTION_COEFFICIENT.none,
                                            MASS_ABSORPTION_COEFFICIENT.pouchou_pichoir1991],
              FLUORESCENCE: [FLUORESCENCE.none,
                             FLUORESCENCE.fluorescence,
                             FLUORESCENCE.fluorescence_compton]}
    DEFAULT_MODELS = {ELASTIC_CROSS_SECTION: ELASTIC_CROSS_SECTION.elsepa2005,
                      IONIZATION_CROSS_SECTION: IONIZATION_CROSS_SECTION.bote_salvat2008,
                      IONIZATION_POTENTIAL: IONIZATION_POTENTIAL.berger_seltzer1983,
                      ENERGY_LOSS: ENERGY_LOSS.joy_luo1989,
                      MASS_ABSORPTION_COEFFICIENT: MASS_ABSORPTION_COEFFICIENT.chantler2005,
                      FLUORESCENCE: FLUORESCENCE.none}


    def _convert_beam(self, options):
        if not _Converter._convert_beam(self, options):
            return False

        if options.beam.particle is not ELECTRON:
            self._warn("Beam particle must be ELECTRON",
                       "This options definition was removed.")
            return False

        if options.beam.energy_eV < 100:
            self._warn("Beam energy must be greater or equal to 100 eV",
                       "This options definition was removed.")
            return False

        if options.beam.origin_m == (0, 0, 1):
            options.beam.origin_m = (0, 0, 0.09)
            self._warn('Change origin position to fit inside NISTMonte microscope chamber')

        if any(map(lambda p: p >= 0.1, options.beam.origin_m)):
            self._warn("Origin must be within a sphere with radius of 0.1 m",
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

