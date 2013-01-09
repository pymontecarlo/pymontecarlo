#!/usr/bin/env python
"""
================================================================================
:mod:`converter` -- Converter for Monaco program
================================================================================

.. module:: converter
   :synopsis: Converter for Monaco program

.. inheritance-diagram:: pymontecarlo.program.monaco.input.converter

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import warnings

# Third party modules.

# Local modules.
from pymontecarlo.input.converter import \
    Converter as _Converter, ConversionWarning, ConversionException

from pymontecarlo.input.particle import ELECTRON
from pymontecarlo.input.beam import PencilBeam
from pymontecarlo.input.geometry import Substrate
from pymontecarlo.input.limit import ShowersLimit
from pymontecarlo.input.detector import PhotonIntensityDetector
from pymontecarlo.input.model import \
    (ELASTIC_CROSS_SECTION, IONIZATION_CROSS_SECTION, IONIZATION_POTENTIAL,
     ENERGY_LOSS, MASS_ABSORPTION_COEFFICIENT)

# Globals and constants variables.

class Converter(_Converter):
    BEAMS = [PencilBeam]
    GEOMETRIES = [Substrate]
    DETECTORS = [PhotonIntensityDetector]
    LIMITS = [ShowersLimit]
    MODELS = {ELASTIC_CROSS_SECTION.type: [ELASTIC_CROSS_SECTION.mott_czyzewski1990],
              IONIZATION_CROSS_SECTION.type: [IONIZATION_CROSS_SECTION.gryzinsky],
              IONIZATION_POTENTIAL.type: [IONIZATION_POTENTIAL.springer1967],
              ENERGY_LOSS.type: [ENERGY_LOSS.bethe1930mod],
              MASS_ABSORPTION_COEFFICIENT.type: [MASS_ABSORPTION_COEFFICIENT.bastin_heijligers1989]}
    DEFAULT_MODELS = {ELASTIC_CROSS_SECTION.type: ELASTIC_CROSS_SECTION.mott_czyzewski1990,
                      IONIZATION_CROSS_SECTION.type: IONIZATION_CROSS_SECTION.gryzinsky,
                      IONIZATION_POTENTIAL.type: IONIZATION_POTENTIAL.springer1967,
                      ENERGY_LOSS.type: ENERGY_LOSS.bethe1930mod,
                      MASS_ABSORPTION_COEFFICIENT.type: MASS_ABSORPTION_COEFFICIENT.bastin_heijligers1989}

    def _convert_beam(self, options):
        _Converter._convert_beam(self, options)

        if options.beam.particle is not ELECTRON:
            raise ConversionException, "Beam particle must be ELECTRON"

        if options.beam.energy_eV > 400e3:
            message = "Beam energy (%s) must be less than 400 keV" % \
                            options.beam.energy_eV
            raise ConversionException, message

        if options.beam.aperture_rad != 0.0:
            message = "Monaco does not support beam aperture."
            warnings.warn(message, ConversionWarning)

    def _convert_geometry(self, options):
        _Converter._convert_geometry(self, options)

        if options.geometry.tilt_rad != 0.0:
            options.geometry.tilt_rad = 0.0
            message = "Geometry cannot be tilted in Monaco, only the beam direction. Tilt set to 0.0 deg."
            warnings.warn(message, ConversionWarning)

    def _convert_limits(self, options):
        _Converter._convert_limits(self, options)

        limit = options.limits.find(ShowersLimit)
        if limit is None:
            raise ConversionException, "A ShowersLimit must be defined."
