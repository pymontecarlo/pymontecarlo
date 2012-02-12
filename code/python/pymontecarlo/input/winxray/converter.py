#!/usr/bin/env python
"""
================================================================================
:mod:`converter` -- WinX-Ray conversion from base options
================================================================================

.. module:: converter
   :synopsis: WinX-Ray conversion from base options

.. inheritance-diagram:: pymontecarlo.input.winxray.converter

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
from pymontecarlo.input.base.converter import \
    Converter as _Converter, ConversionWarning, ConversionException
from pymontecarlo.input.base.beam import PencilBeam, GaussianBeam
from pymontecarlo.input.base.geometry import Substrate
from pymontecarlo.input.base.limit import ShowersLimit
from pymontecarlo.input.base.detector import \
    (_DelimitedDetector,
     BackscatteredElectronEnergyDetector,
     BackscatteredElectronPolarAngularDetector,
     PhiRhoZDetector,
     PhotonIntensityDetector,
     PhotonSpectrumDetector,
     ElectronFractionDetector,
     TimeDetector,
     )
from pymontecarlo.input.base.model import \
    (ELASTIC_CROSS_SECTION, IONIZATION_CROSS_SECTION, IONIZATION_POTENTIAL,
     RANDOM_NUMBER_GENERATOR, DIRECTION_COSINE, ENERGY_LOSS,
     MASS_ABSORPTION_COEFFICIENT)

# Globals and constants variables.

class Converter(_Converter):
    BEAMS = [GaussianBeam]
    GEOMETRIES = [Substrate]
    DETECTORS = [BackscatteredElectronEnergyDetector,
                 BackscatteredElectronPolarAngularDetector,
                 PhiRhoZDetector,
                 PhotonIntensityDetector,
                 PhotonSpectrumDetector,
                 ElectronFractionDetector,
                 TimeDetector]
    LIMITS = [ShowersLimit]
    MODELS = {ELASTIC_CROSS_SECTION.type: [ELASTIC_CROSS_SECTION.mott_czyzewski1990,
                                           ELASTIC_CROSS_SECTION.mott_czyzewski1990_linear,
                                           ELASTIC_CROSS_SECTION.mott_czyzewski1990_powerlaw,
                                           ELASTIC_CROSS_SECTION.mott_czyzewski1990_cubicspline,
                                           ELASTIC_CROSS_SECTION.mott_demers,
                                           ELASTIC_CROSS_SECTION.rutherford,
                                           ELASTIC_CROSS_SECTION.rutherford_relativistic],
              IONIZATION_CROSS_SECTION.type: [IONIZATION_CROSS_SECTION.casnati1982],
              IONIZATION_POTENTIAL.type: [IONIZATION_POTENTIAL.joy_luo1989],
              RANDOM_NUMBER_GENERATOR.type: [RANDOM_NUMBER_GENERATOR.press1966_rand1,
                                             RANDOM_NUMBER_GENERATOR.press1966_rand2,
                                             RANDOM_NUMBER_GENERATOR.press1966_rand3,
                                             RANDOM_NUMBER_GENERATOR.press1966_rand4],
              DIRECTION_COSINE.type: [DIRECTION_COSINE.demers2000],
              ENERGY_LOSS.type: [ENERGY_LOSS.joy_luo1989],
              MASS_ABSORPTION_COEFFICIENT.type: [MASS_ABSORPTION_COEFFICIENT.heinrich_ixcom11,
                                                 MASS_ABSORPTION_COEFFICIENT.henke1993,
                                                 MASS_ABSORPTION_COEFFICIENT.thinh_leroux1979]}
    DEFAULT_MODELS = {ELASTIC_CROSS_SECTION.type: ELASTIC_CROSS_SECTION.mott_czyzewski1990,
                      IONIZATION_CROSS_SECTION.type: IONIZATION_CROSS_SECTION.casnati1982,
                      IONIZATION_POTENTIAL.type: IONIZATION_POTENTIAL.joy_luo1989,
                      RANDOM_NUMBER_GENERATOR.type: RANDOM_NUMBER_GENERATOR.press1966_rand3,
                      DIRECTION_COSINE.type: DIRECTION_COSINE.demers2000,
                      ENERGY_LOSS.type: ENERGY_LOSS.joy_luo1989,
                      MASS_ABSORPTION_COEFFICIENT.type: MASS_ABSORPTION_COEFFICIENT.henke1993}

    def _convert_beam(self, options):
        try:
            _Converter._convert_beam(self, options)
        except ConversionException as ex:
            if isinstance(options.beam, PencilBeam):
                old = options.beam
                options.beam = GaussianBeam(old.energy_eV, 0.0, old.origin_m,
                                            old.direction, old.aperture_rad)

                message = "Pencil beam converted to Gaussian beam with 0 m diameter"
                warnings.warn(message, ConversionWarning)
            else:
                raise ex

    def _convert_geometry(self, options):
        _Converter._convert_geometry(self, options)

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
