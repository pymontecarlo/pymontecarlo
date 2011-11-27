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
    Converter, ConversionWarning, ConversionException
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

# Globals and constants variables.

class Casino2Converter(Converter):
    BEAMS = [GaussianBeam]
    GEOMETRIES = [Substrate, MultiLayers, GrainBoundaries]
    DETECTORS = [BackscatteredElectronEnergyDetector,
                 TransmittedElectronEnergyDetector,
                 BackscatteredElectronPolarAngularDetector,
                 PhiRhoZDetector,
                 PhotonIntensityDetector]
    LIMITS = [ShowersLimit]

    def _convert_beam(self, options):
        try:
            Converter._convert_beam(self, options)
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
        Converter._convert_geometry(self, options)

        if options.geometry.tilt != 0.0:
            options.geometry.tilt = 0.0
            message = "Geometry cannot be tilted in Casino, only the beam direction. Tilt set to 0.0 deg."
            warnings.warn(message, ConversionWarning)

    def _convert_detectors(self, options):
        Converter._convert_detectors(self, options)

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
