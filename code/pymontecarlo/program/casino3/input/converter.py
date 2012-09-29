#!/usr/bin/env python
"""
================================================================================
:mod:`converter` -- Casino 3 conversion from base options
================================================================================

.. module:: converter
   :synopsis: Casino 3 conversion from base options

.. inheritance-diagram:: pymontecarlo.program.casino3.input.converter

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
from pymontecarlo.input.converter import ConversionWarning
from pymontecarlo.input.converter import Converter as _Converter, ConversionException

from pymontecarlo.input.beam import GaussianBeam, PencilBeam
from pymontecarlo.input.geometry import Substrate, MultiLayers
from pymontecarlo.input.limit import ShowersLimit
from pymontecarlo.input.detector import TrajectoryDetector
from pymontecarlo.input.model import \
    (ELASTIC_CROSS_SECTION, IONIZATION_POTENTIAL,
     RANDOM_NUMBER_GENERATOR, DIRECTION_COSINE, ENERGY_LOSS)

# Globals and constants variables.

class Converter(_Converter):
    BEAMS = [GaussianBeam]
    GEOMETRIES = [Substrate, MultiLayers]
    DETECTORS = [TrajectoryDetector]
    LIMITS = [ShowersLimit]
    MODELS = {ELASTIC_CROSS_SECTION.type: [ELASTIC_CROSS_SECTION.mott_czyzewski1990,
                                           ELASTIC_CROSS_SECTION.mott_drouin1993,
                                           ELASTIC_CROSS_SECTION.mott_browning1994,
                                           ELASTIC_CROSS_SECTION.rutherford,
                                           ELASTIC_CROSS_SECTION.elsepa2005,
                                           ELASTIC_CROSS_SECTION.reimer],
              IONIZATION_POTENTIAL.type: [IONIZATION_POTENTIAL.joy_luo1989,
                                          IONIZATION_POTENTIAL.hovington,
                                          IONIZATION_POTENTIAL.berger_seltzer1964],
              RANDOM_NUMBER_GENERATOR.type: [RANDOM_NUMBER_GENERATOR.lagged_fibonacci,
                                             RANDOM_NUMBER_GENERATOR.mersenne],
              DIRECTION_COSINE.type: [DIRECTION_COSINE.lowney1994],
              ENERGY_LOSS.type: [ENERGY_LOSS.joy_luo_lowney]}
    DEFAULT_MODELS = {ELASTIC_CROSS_SECTION.type: ELASTIC_CROSS_SECTION.elsepa2005,
                      IONIZATION_POTENTIAL.type: IONIZATION_POTENTIAL.joy_luo1989,
                      RANDOM_NUMBER_GENERATOR.type: RANDOM_NUMBER_GENERATOR.lagged_fibonacci,
                      DIRECTION_COSINE.type: DIRECTION_COSINE.lowney1994,
                      ENERGY_LOSS.type: ENERGY_LOSS.joy_luo_lowney}

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

    def _convert_detectors(self, options):
        _Converter._convert_detectors(self, options)

        dets = options.detectors.findall(TrajectoryDetector)
        if not dets:
            raise ConversionException, 'A TrajectoryDetector must be defined'

    def _convert_limits(self, options):
        _Converter._convert_limits(self, options)

        limit = options.limits.find(ShowersLimit)
        if limit is None:
            raise ConversionException, "A ShowersLimit must be defined."

        det = options.detectors.findall(TrajectoryDetector).values()[0]
        if det.showers != limit.showers:
            raise ConversionException, \
                'The number of showers in the TrajectoryDetector (%i) must equal the number in the ShowersLimit (%i)' % \
                    (det.showers, limit.showers)



