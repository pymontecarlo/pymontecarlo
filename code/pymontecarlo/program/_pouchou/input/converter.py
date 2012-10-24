#!/usr/bin/env python
"""
================================================================================
:mod:`converter` -- Pouchou analytical model conversion from base options
================================================================================

.. module:: converter
   :synopsis: Pouchou analytical model conversion from base options

.. inheritance-diagram:: pymontecarlo.program._pouchou.input.converter

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
from pymontecarlo.input.beam import PencilBeam, GaussianBeam
from pymontecarlo.input.geometry import Substrate
from pymontecarlo.input.detector import \
    (PhotonIntensityDetector,
     TimeDetector,
     PhiRhoZDetector)
from pymontecarlo.input.model import MASS_ABSORPTION_COEFFICIENT

# Globals and constants variables.

class Converter(_Converter):
    BEAMS = [PencilBeam]
    GEOMETRIES = [Substrate]
    DETECTORS = [PhiRhoZDetector,
                 PhotonIntensityDetector,
                 TimeDetector]
    LIMITS = []
    MODELS = {MASS_ABSORPTION_COEFFICIENT.type: [MASS_ABSORPTION_COEFFICIENT.pouchou_pichoir1991,
                                                 MASS_ABSORPTION_COEFFICIENT.heinrich_ixcom11_dtsa,
                                                 MASS_ABSORPTION_COEFFICIENT.henke1993]}
    DEFAULT_MODELS = {MASS_ABSORPTION_COEFFICIENT.type: MASS_ABSORPTION_COEFFICIENT.henke1993}


    def __init__(self):
        """
        Converter from base options for PAP simulation.
        """
        _Converter.__init__(self)

    def _convert_beam(self, options):
        try:
            _Converter._convert_beam(self, options)
        except ConversionException as ex:
            if isinstance(options.beam, GaussianBeam):
                old = options.beam
                options.beam = PencilBeam(old.energy_eV, old.particle,
                                          old.origin_m, old.direction,
                                          old.aperture_rad)

                message = "Gaussian beam converted to pencil beam"
                warnings.warn(message, ConversionWarning)
            else:
                raise ex

        if options.beam.particle is not ELECTRON:
            raise ConversionException, "Beam particle must be ELECTRON"

    def _convert_detectors(self, options):
        _Converter._convert_detectors(self, options)

        # Assert that there is only one PhotonIntensityDetector
        detectors = options.detectors.findall(PhotonIntensityDetector)
        if len(detectors) > 1:
            raise ConversionException, "Too many photon intensity detectors. Only one is accepted"

        # Assert that there is only one PhiRhoZDetector
        detectors = options.detectors.findall(PhiRhoZDetector)
        if len(detectors) > 1:
            raise ConversionException, "Too many phi-rho-z detectors. Only one is accepted"

