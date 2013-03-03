#!/usr/bin/env python
"""
================================================================================
:mod:`converter` -- PENSHOWER conversion from base options
================================================================================

.. module:: converter
   :synopsis: PENSHOWER conversion from base options

.. inheritance-diagram:: pymontecarlo.program.penshower.input.converter

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
from pymontecarlo.program._penelope.input.converter import \
    Converter as _Converter, ConversionException

from pymontecarlo.input.beam import GaussianBeam, PencilBeam
from pymontecarlo.input.limit import ShowersLimit
from pymontecarlo.input.detector import TrajectoryDetector

# Globals and constants variables.

class Converter(_Converter):
    BEAMS = [GaussianBeam]
    DETECTORS = [TrajectoryDetector]
    LIMITS = [ShowersLimit]

    def __init__(self, elastic_scattering=(0.0, 0.0),
                 cutoff_energy_inelastic=50.0,
                 cutoff_energy_bremsstrahlung=50.0):
        """
        Converter from base options to PENSHOWER options.
        
        During the conversion, the materials are converted to :class:`PenelopeMaterial`. 
        For this, the specified elastic scattering and cutoff energies are used
        as the default values in the conversion.
        """
        _Converter.__init__(self, elastic_scattering, cutoff_energy_inelastic,
                            cutoff_energy_bremsstrahlung)

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
        if len(dets) != 1:
            raise ConversionException, 'Only one TrajectoryDetector must be defined'

    def _convert_limits(self, options):
        _Converter._convert_limits(self, options)

        limit = options.limits.find(ShowersLimit)
        if limit is None:
            raise ConversionException, "A ShowersLimit must be defined."
