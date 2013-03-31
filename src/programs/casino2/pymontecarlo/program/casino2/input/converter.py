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
import warnings

# Third party modules.

# Local modules.
from pymontecarlo.input.converter import \
    Converter as _Converter, ConversionWarning, ConversionException

from pymontecarlo.input.particle import ELECTRON
from pymontecarlo.input.beam import PencilBeam, GaussianBeam
from pymontecarlo.input.geometry import \
    Substrate, MultiLayers, GrainBoundaries
from pymontecarlo.input.limit import ShowersLimit
from pymontecarlo.input.detector import \
    (_DelimitedDetector,
     BackscatteredElectronEnergyDetector,
     BackscatteredElectronPolarAngularDetector,
     BackscatteredElectronRadialDetector,
     PhotonDepthDetector,
     PhotonRadialDetector,
     PhotonIntensityDetector,
     TransmittedElectronEnergyDetector,
     ElectronFractionDetector,
     TrajectoryDetector,
     )
from pymontecarlo.input.model import \
    (ELASTIC_CROSS_SECTION, IONIZATION_CROSS_SECTION, IONIZATION_POTENTIAL,
     RANDOM_NUMBER_GENERATOR, DIRECTION_COSINE, ENERGY_LOSS,
     MASS_ABSORPTION_COEFFICIENT)

# Globals and constants variables.

class Converter(_Converter):
    BEAMS = [GaussianBeam]
    GEOMETRIES = [Substrate, MultiLayers, GrainBoundaries]
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
    MODELS = {ELASTIC_CROSS_SECTION.type: [ELASTIC_CROSS_SECTION.mott_czyzewski1990,
                                           ELASTIC_CROSS_SECTION.mott_drouin1993,
                                           ELASTIC_CROSS_SECTION.mott_browning1994,
                                           ELASTIC_CROSS_SECTION.rutherford],
              IONIZATION_CROSS_SECTION.type: [IONIZATION_CROSS_SECTION.pouchou1986,
                                              IONIZATION_CROSS_SECTION.brown_powell,
                                              IONIZATION_CROSS_SECTION.casnati1982,
                                              IONIZATION_CROSS_SECTION.gryzinsky,
                                              IONIZATION_CROSS_SECTION.jakoby],
              IONIZATION_POTENTIAL.type: [IONIZATION_POTENTIAL.joy_luo1989,
                                          IONIZATION_POTENTIAL.berger_seltzer1983,
                                          IONIZATION_POTENTIAL.hovington],
              RANDOM_NUMBER_GENERATOR.type: [RANDOM_NUMBER_GENERATOR.press1966_rand1,
                                             RANDOM_NUMBER_GENERATOR.mersenne],
              DIRECTION_COSINE.type: [DIRECTION_COSINE.soum1979,
                                      DIRECTION_COSINE.drouin1996],
              ENERGY_LOSS.type: [ENERGY_LOSS.joy_luo1989],
              MASS_ABSORPTION_COEFFICIENT.type: [MASS_ABSORPTION_COEFFICIENT.heinrich_ixcom11]}
    DEFAULT_MODELS = {ELASTIC_CROSS_SECTION.type: ELASTIC_CROSS_SECTION.mott_czyzewski1990,
                      IONIZATION_CROSS_SECTION.type: IONIZATION_CROSS_SECTION.casnati1982,
                      IONIZATION_POTENTIAL.type: IONIZATION_POTENTIAL.joy_luo1989,
                      RANDOM_NUMBER_GENERATOR.type: RANDOM_NUMBER_GENERATOR.press1966_rand1,
                      DIRECTION_COSINE.type: DIRECTION_COSINE.drouin1996,
                      ENERGY_LOSS.type: ENERGY_LOSS.joy_luo1989,
                      MASS_ABSORPTION_COEFFICIENT.type: MASS_ABSORPTION_COEFFICIENT.heinrich_ixcom11}

    def _convert_beam(self, options):
        try:
            _Converter._convert_beam(self, options)
        except ConversionException as ex:
            if isinstance(options.beam, PencilBeam):
                old = options.beam
                options.beam = GaussianBeam(old.energy_eV, 0.0, old.particle,
                                            old.origin_m, old.direction,
                                            old.aperture_rad)

                message = "Pencil beam converted to Gaussian beam with 0 m diameter"
                warnings.warn(message, ConversionWarning)
            else:
                raise ex

        if options.beam.particle is not ELECTRON:
            raise ConversionException, "Beam particle must be ELECTRON"

        if options.beam.energy_eV > 1e6:
            message = "Beam energy (%s) must be less than 1MeV" % \
                            options.beam.energy_eV
            raise ConversionException, message

        if options.beam.aperture_rad != 0.0:
            message = "Casino 2 does not support beam aperture."
            warnings.warn(message, ConversionWarning)

    def _convert_geometry(self, options):
        _Converter._convert_geometry(self, options)

        if options.geometry.tilt_rad != 0.0:
            options.geometry.tilt_rad = 0.0
            message = "Geometry cannot be tilted in Casino, only the beam direction. Tilt set to 0.0 deg."
            warnings.warn(message, ConversionWarning)

    def _convert_detectors(self, options):
        _Converter._convert_detectors(self, options)

        # There can be only one detector of each type
        for clasz in self.DETECTORS:
            if len(options.detectors.findall(clasz)) > 1:
                raise ConversionException, "There can only one '%s' detector" % clasz.__name__

        # Assert elevation and azimuth of delimited detectors are equal
        detectors = options.detectors.findall(_DelimitedDetector).values()
        if not detectors:
            return

        detector_class = detectors[0].__class__.__name__
        elevation_rad = detectors[0].elevation_rad
        azimuth_rad = detectors[0].azimuth_rad

        for detector in detectors[1:]:
            if abs(elevation_rad[0] - detector.elevation_rad[0]) > 1e-6 or \
                    abs(elevation_rad[1] - detector.elevation_rad[1]) > 1e-6:
                raise ConversionException, \
                    "The elevation of the '%s' (%s) should be the same as the one of the '%s' (%s)" % \
                        (detector_class, str(elevation_rad),
                         detector.__class__.__name__, str(detector.elevation_rad))

            if abs(azimuth_rad[0] - detector.azimuth_rad[0]) > 1e-6 or \
                    abs(azimuth_rad[1] - detector.azimuth_rad[1]) > 1e-6:
                raise ConversionException, \
                    "The azimuth of the '%s' (%s) should be the same as the one of the '%s' (%s)" % \
                        (detector_class, str(elevation_rad),
                         detector.__class__.__name__, str(detector.elevation_rad))

    def _convert_limits(self, options):
        _Converter._convert_limits(self, options)

        limit = options.limits.find(ShowersLimit)
        if limit is None:
            raise ConversionException, "A ShowersLimit must be defined."
