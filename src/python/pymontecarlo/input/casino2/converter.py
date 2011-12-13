#!/usr/bin/env python
"""
================================================================================
:mod:`converter` -- Casino conversion from base options
================================================================================

.. module:: converter
   :synopsis: Casino conversion from base options

.. inheritance-diagram:: pymontecarlo.input.casino2.converter

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
from pymontecarlo.input.base.geometry import \
    Substrate, MultiLayers, GrainBoundaries
from pymontecarlo.input.base.limit import ShowersLimit
from pymontecarlo.input.base.detector import \
    (BackscatteredElectronEnergyDetector,
     BackscatteredElectronPolarAngularDetector,
     PhiRhoZDetector,
     PhotonIntensityDetector,
     TransmittedElectronEnergyDetector,
     )
from pymontecarlo.input.base.model import \
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
                 PhiRhoZDetector,
                 PhotonIntensityDetector]
    LIMITS = [ShowersLimit]
    MODELS = {ELASTIC_CROSS_SECTION.type: [ELASTIC_CROSS_SECTION.mott_czyzewski,
                                           ELASTIC_CROSS_SECTION.mott_drouin,
                                           ELASTIC_CROSS_SECTION.mott_browning,
                                           ELASTIC_CROSS_SECTION.rutherford],
              IONIZATION_CROSS_SECTION.type: [IONIZATION_CROSS_SECTION.gauvin,
                                              IONIZATION_CROSS_SECTION.pouchou,
                                              IONIZATION_CROSS_SECTION.brown_powell,
                                              IONIZATION_CROSS_SECTION.casnati,
                                              IONIZATION_CROSS_SECTION.gryzinsky,
                                              IONIZATION_CROSS_SECTION.jakoby],
              IONIZATION_POTENTIAL.type: [IONIZATION_POTENTIAL.joy_luo,
                                          IONIZATION_POTENTIAL.berger_seltzer,
                                          IONIZATION_POTENTIAL.hovington],
              RANDOM_NUMBER_GENERATOR.type: [RANDOM_NUMBER_GENERATOR.press_rand1,
                                             RANDOM_NUMBER_GENERATOR.mersenne],
              DIRECTION_COSINE.type: [DIRECTION_COSINE.soum,
                                      DIRECTION_COSINE.drouin],
              ENERGY_LOSS.type: [ENERGY_LOSS.joy_luo],
              MASS_ABSORPTION_COEFFICIENT.type: [MASS_ABSORPTION_COEFFICIENT.heinrich_ixcom11]}
    DEFAULT_MODELS = {ELASTIC_CROSS_SECTION.type: ELASTIC_CROSS_SECTION.mott_czyzewski,
                      IONIZATION_CROSS_SECTION.type: IONIZATION_CROSS_SECTION.casnati,
                      IONIZATION_POTENTIAL.type: IONIZATION_POTENTIAL.joy_luo,
                      RANDOM_NUMBER_GENERATOR.type: RANDOM_NUMBER_GENERATOR.press_rand1,
                      DIRECTION_COSINE.type: DIRECTION_COSINE.drouin,
                      ENERGY_LOSS.type: ENERGY_LOSS.joy_luo,
                      MASS_ABSORPTION_COEFFICIENT.type: MASS_ABSORPTION_COEFFICIENT.heinrich_ixcom11}

    def _convert_beam(self, options):
        try:
            _Converter._convert_beam(self, options)
        except ConversionException as ex:
            if isinstance(options.beam, PencilBeam):
                old = options.beam
                options.beam = GaussianBeam(old.energy, 0.0, old.origin,
                                            old.direction, old.aperture)

                message = "Pencil beam converted to Gaussian beam with 0 m diameter"
                warnings.warn(message, ConversionWarning)
            else:
                raise ex

    def _convert_geometry(self, options):
        _Converter._convert_geometry(self, options)

        if options.geometry.tilt != 0.0:
            options.geometry.tilt = 0.0
            message = "Geometry cannot be tilted in Casino, only the beam direction. Tilt set to 0.0 deg."
            warnings.warn(message, ConversionWarning)

    def _convert_detectors(self, options):
        _Converter._convert_detectors(self, options)

        # There can be only one detector of each type
        for clasz in self.DETECTORS:
            if len(options.detectors.findall(clasz)) > 1:
                raise ConversionException, "There can only one '%s' detector" % clasz.__name__

        # Assert delimited detector of the PhotonIntensityDetector and
        # PhiRhoZDetector are equal
        intensities = options.detectors.findall(PhotonIntensityDetector)
        phirhozs = options.detectors.findall(PhiRhoZDetector)

        if intensities and phirhozs:
            intensity = intensities.values()[0]
            phirhoz = phirhozs.values()[0]

            if abs(intensity.elevation[0] - phirhoz.elevation[0]) > 1e-6 or \
                    abs(intensity.elevation[1] - phirhoz.elevation[1]) > 1e-6:
                raise ConversionException, \
                    "The elevation of the 'PhotonIntensityDetector' (%s) should be the same as the one of the 'PhiRhoZDetector' (%s)" % \
                    (str(intensity.elevation), str(phirhoz.elevation))

            if abs(intensity.azimuth[0] - phirhoz.azimuth[0]) > 1e-6 or \
                    abs(intensity.azimuth[1] - phirhoz.azimuth[1]) > 1e-6:
                raise ConversionException, \
                    "The azimuth of the 'PhotonIntensityDetector' (%s) should be the same as the one of the 'PhiRhoZDetector' (%s)" % \
                    (str(intensity.azimuth), str(phirhoz.azimuth))
