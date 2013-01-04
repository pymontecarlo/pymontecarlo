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
from pymontecarlo.input.converter import \
    Converter as _Converter, ConversionException

from pymontecarlo.input.particle import ELECTRON
from pymontecarlo.input.beam import GaussianBeam, PencilBeam
from pymontecarlo.input.geometry import \
    Substrate, MultiLayers, GrainBoundaries
from pymontecarlo.input.limit import ShowersLimit
from pymontecarlo.input.detector import \
    (_DelimitedDetector,
     BackscatteredElectronAzimuthalAngularDetector,
     BackscatteredElectronEnergyDetector,
     BackscatteredElectronPolarAngularDetector,
     PhotonIntensityDetector,
     PhotonSpectrumDetector,
     TransmittedElectronAzimuthalAngularDetector,
     TransmittedElectronEnergyDetector,
     TransmittedElectronPolarAngularDetector,
     TimeDetector,
     ElectronFractionDetector)
from pymontecarlo.input.model import \
    (ELASTIC_CROSS_SECTION, IONIZATION_CROSS_SECTION, IONIZATION_POTENTIAL,
     ENERGY_LOSS, MASS_ABSORPTION_COEFFICIENT)

# Globals and constants variables.

class Converter(_Converter):
    BEAMS = [GaussianBeam, PencilBeam]
    GEOMETRIES = [Substrate, MultiLayers, GrainBoundaries]
    DETECTORS = [BackscatteredElectronAzimuthalAngularDetector,
                 BackscatteredElectronEnergyDetector,
                 BackscatteredElectronPolarAngularDetector,
                 #EnergyDepositedSpatialDetector,
                 #PhiRhoZDetector,
                 PhotonIntensityDetector,
                 PhotonSpectrumDetector,
                 TransmittedElectronAzimuthalAngularDetector,
                 TransmittedElectronEnergyDetector,
                 TransmittedElectronPolarAngularDetector,
                 TimeDetector,
                 ElectronFractionDetector]
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
                                                 MASS_ABSORPTION_COEFFICIENT.pouchou_pichoir1991]}
    DEFAULT_MODELS = {ELASTIC_CROSS_SECTION.type: ELASTIC_CROSS_SECTION.elsepa2005,
                      IONIZATION_CROSS_SECTION.type: IONIZATION_CROSS_SECTION.bote_salvat2008,
                      IONIZATION_POTENTIAL.type: IONIZATION_POTENTIAL.berger_seltzer1983,
                      ENERGY_LOSS.type: ENERGY_LOSS.joy_luo1989,
                      MASS_ABSORPTION_COEFFICIENT.type: MASS_ABSORPTION_COEFFICIENT.chantler2005}


    def __init__(self):
        """
        Converter from base options for NistMonte simulation.
        """
        _Converter.__init__(self)

    def _convert_beam(self, options):
        _Converter._convert_beam(self, options)

        if options.beam.particle is not ELECTRON:
            raise ConversionException, "Beam particle must be ELECTRON"

    def _convert_detectors(self, options):
        _Converter._convert_detectors(self, options)

        # Assert delimited detector have the same elevation and azimuth angles
        detectors = options.detectors.findall(_DelimitedDetector).items()
        if len(detectors) <= 1:
            return

        elevation = detectors[0][1].elevation_rad
        azimuth = detectors[0][1].azimuth_rad

        for key, detector in detectors[1:]:
            if abs(detector.elevation_rad[0] - elevation[0]) > 1e-6 or \
                    abs(detector.elevation_rad[1] - elevation[1]) > 1e-6:
                raise ConversionException, \
                    "The elevation of the detector '%s' (%s) should be the same as the others (%s)" % \
                    (key, str(detector.elevation_rad), str(elevation))

            if abs(detector.azimuth_rad[0] - azimuth[0]) > 1e-6 or \
                    abs(detector.azimuth_rad[1] - azimuth[1]) > 1e-6:
                raise ConversionException, \
                    "The azimuth of the detector '%s' (%s) should be the same as the others (%s)" % \
                    (key, str(detector.azimuth_rad), str(azimuth))

    def _convert_limits(self, options):
        _Converter._convert_limits(self, options)

        limit = options.limits.find(ShowersLimit)
        if limit is None:
            raise ConversionException, "A ShowersLimit must be defined."

