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

# Third party modules.

# Local modules.
from pymontecarlo.program._penelope.converter import Converter as _Converter

from pymontecarlo.options.beam import GaussianBeam, PencilBeam
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.options.detector import TrajectoryDetector

from pymontecarlo.util.expander import ExpanderSingleDetector

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

        self._expander = ExpanderSingleDetector([TrajectoryDetector])

    def _convert_beam(self, options):
        if type(options.beam) is PencilBeam:
            old = options.beam
            options.beam = GaussianBeam(old.energy_eV, 0.0, old.particle,
                                        old.origin_m, old.direction,
                                        old.aperture_rad)

            self._warn("Pencil beam converted to Gaussian beam with 0 m diameter")

        return _Converter._convert_beam(self, options)

    def _convert_detectors(self, options):
        if not _Converter._convert_detectors(self, options):
            return False

        dets = list(options.detectors.iterclass(TrajectoryDetector))
        if not dets:
            self._warn('A trajectory detector must be defined',
                       "This options definition was removed.")
            return False

        return True

    def _convert_limits(self, options):
        if not _Converter._convert_limits(self, options):
            return False

        limits = list(options.limits.iterclass(ShowersLimit))
        if not limits:
            self._warn("A showers limit must be defined."
                       "This options definition was removed.")
            return False

        return True
