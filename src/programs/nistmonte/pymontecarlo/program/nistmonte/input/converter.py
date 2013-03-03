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
import warnings

# Third party modules.

# Local modules.
from pymontecarlo.input.converter import \
    Converter as _Converter, ConversionException, ConversionWarning

from pymontecarlo.input.particle import ELECTRON
from pymontecarlo.input.beam import GaussianBeam, PencilBeam
from pymontecarlo.input.geometry import \
    Substrate, Inclusion, MultiLayers, GrainBoundaries
from pymontecarlo.input.limit import ShowersLimit
from pymontecarlo.input.detector import \
    (
#     BackscatteredElectronAzimuthalAngularDetector,
#     BackscatteredElectronEnergyDetector,
#     BackscatteredElectronPolarAngularDetector,
     PhiRhoZDetector,
     PhotonIntensityDetector,
#     PhotonSpectrumDetector,
#     TransmittedElectronAzimuthalAngularDetector,
#     TransmittedElectronEnergyDetector,
#     TransmittedElectronPolarAngularDetector,
     TimeDetector,
     TrajectoryDetector,
#     ElectronFractionDetector
     )
from pymontecarlo.input.model import \
    (ELASTIC_CROSS_SECTION, IONIZATION_CROSS_SECTION, IONIZATION_POTENTIAL,
     ENERGY_LOSS, MASS_ABSORPTION_COEFFICIENT, FLUORESCENCE)

# Globals and constants variables.

class Converter(_Converter):
    BEAMS = [GaussianBeam, PencilBeam]
    GEOMETRIES = [Substrate, Inclusion, MultiLayers, GrainBoundaries]
    DETECTORS = [
                 #BackscatteredElectronAzimuthalAngularDetector,
                 #BackscatteredElectronEnergyDetector,
                 #BackscatteredElectronPolarAngularDetector,
                 #EnergyDepositedSpatialDetector,
                 PhiRhoZDetector,
                 PhotonIntensityDetector,
                 #PhotonSpectrumDetector,
                 #TransmittedElectronAzimuthalAngularDetector,
                 #TransmittedElectronEnergyDetector,
                 #TransmittedElectronPolarAngularDetector,
                 TimeDetector,
                 TrajectoryDetector,
                 #ElectronFractionDetector
                 ]
    LIMITS = [ShowersLimit]
    MODELS = {ELASTIC_CROSS_SECTION.type: [ELASTIC_CROSS_SECTION.mott_czyzewski1990,
                                           ELASTIC_CROSS_SECTION.rutherford,
                                           ELASTIC_CROSS_SECTION.elsepa2005],
              IONIZATION_CROSS_SECTION.type: [IONIZATION_CROSS_SECTION.bote_salvat2008,
                                              IONIZATION_CROSS_SECTION.casnati1982,
                                              IONIZATION_CROSS_SECTION.dijkstra_heijliger1998,
                                              IONIZATION_CROSS_SECTION.pouchou1986],
              IONIZATION_POTENTIAL.type: [IONIZATION_POTENTIAL.berger_seltzer1964,
                                          IONIZATION_POTENTIAL.berger_seltzer1983,
                                          IONIZATION_POTENTIAL.berger_seltzer1983_citzaf,
                                          IONIZATION_POTENTIAL.bloch1933,
                                          IONIZATION_POTENTIAL.duncumb_decasa1969,
                                          IONIZATION_POTENTIAL.heinrich_yakowitz1970,
                                          IONIZATION_POTENTIAL.springer1967,
                                          IONIZATION_POTENTIAL.sternheimer1964,
                                          IONIZATION_POTENTIAL.wilson1941,
                                          IONIZATION_POTENTIAL.zeller1975],
              ENERGY_LOSS.type: [ENERGY_LOSS.joy_luo1989,
                                #ENERGY_LOSS.bethe1930,
                                 ENERGY_LOSS.bethe1930mod],
              MASS_ABSORPTION_COEFFICIENT.type: [MASS_ABSORPTION_COEFFICIENT.chantler2005,
                                                 MASS_ABSORPTION_COEFFICIENT.heinrich_ixcom11,
                                                 MASS_ABSORPTION_COEFFICIENT.heinrich_ixcom11_dtsa,
                                                 MASS_ABSORPTION_COEFFICIENT.henke1993,
                                                 MASS_ABSORPTION_COEFFICIENT.none,
                                                 MASS_ABSORPTION_COEFFICIENT.pouchou_pichoir1991],
              FLUORESCENCE.type: [FLUORESCENCE.none,
                                  FLUORESCENCE.fluorescence,
                                  FLUORESCENCE.fluorescence_compton]}
    DEFAULT_MODELS = {ELASTIC_CROSS_SECTION.type: ELASTIC_CROSS_SECTION.elsepa2005,
                      IONIZATION_CROSS_SECTION.type: IONIZATION_CROSS_SECTION.bote_salvat2008,
                      IONIZATION_POTENTIAL.type: IONIZATION_POTENTIAL.berger_seltzer1983,
                      ENERGY_LOSS.type: ENERGY_LOSS.joy_luo1989,
                      MASS_ABSORPTION_COEFFICIENT.type: MASS_ABSORPTION_COEFFICIENT.chantler2005,
                      FLUORESCENCE.type: FLUORESCENCE.none}


    def __init__(self):
        """
        Converter from base options for NistMonte simulation.
        """
        _Converter.__init__(self)

    def _convert_beam(self, options):
        _Converter._convert_beam(self, options)

        if options.beam.particle is not ELECTRON:
            raise ConversionException, "Beam particle must be ELECTRON"

        if options.beam.energy_eV < 100:
            raise ConversionException, "Beam energy must be greater or equal to 100 eV"

        if options.beam.origin_m == (0, 0, 1):
            options.beam.origin_m = (0, 0, 0.09)
            message = 'Change origin position to fit inside NISTMonte microscope chamber'
            warnings.warn(message, ConversionWarning)

        if any(map(lambda p: p >= 0.1, options.beam.origin_m)):
            raise ConversionException, "Origin must be within a sphere with radius of 0.1 m"

    def _convert_limits(self, options):
        _Converter._convert_limits(self, options)

        limit = options.limits.find(ShowersLimit)
        if limit is None:
            raise ConversionException, "A ShowersLimit must be defined."

