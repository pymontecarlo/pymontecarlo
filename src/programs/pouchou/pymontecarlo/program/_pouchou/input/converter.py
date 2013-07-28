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

# Third party modules.

# Local modules.
from pymontecarlo.input.converter import Converter as _Converter
from pymontecarlo.input.expander import ExpanderSingleDetector
from pymontecarlo.input.particle import ELECTRON
from pymontecarlo.input.beam import PencilBeam, GaussianBeam
from pymontecarlo.input.geometry import Substrate
from pymontecarlo.input.detector import \
    (PhotonIntensityDetector,
     TimeDetector,
     PhotonDepthDetector)
from pymontecarlo.input.model import MASS_ABSORPTION_COEFFICIENT

# Globals and constants variables.

class Converter(_Converter):
    """
    Converter from base options for PAP simulation.
    """

    BEAMS = [PencilBeam]
    GEOMETRIES = [Substrate]
    DETECTORS = [PhotonDepthDetector,
                 PhotonIntensityDetector,
                 TimeDetector]
    LIMITS = []
    MODELS = {MASS_ABSORPTION_COEFFICIENT: [MASS_ABSORPTION_COEFFICIENT.pouchou_pichoir1991,
                                            MASS_ABSORPTION_COEFFICIENT.heinrich_ixcom11_dtsa,
                                            MASS_ABSORPTION_COEFFICIENT.henke1993]}
    DEFAULT_MODELS = {MASS_ABSORPTION_COEFFICIENT: MASS_ABSORPTION_COEFFICIENT.henke1993}

    def __init__(self):
        _Converter.__init__(self)
        self._expander = ExpanderSingleDetector(self.DETECTORS)

    def _convert_beam(self, options):
        if isinstance(options.beam, GaussianBeam):
            old = options.beam
            options.beam = PencilBeam(old.energy_eV, old.particle,
                                      old.origin_m, old.direction,
                                      old.aperture_rad)
            self._warn("Gaussian beam converted to pencil beam")
        
        if not _Converter._convert_beam(self, options):
            return False
        
        if options.beam.particle is not ELECTRON:
            self._warn("Beam particle must be ELECTRON",
                       "This options definition was removed.")
            return False
        
        return True

    def _convert_limits(self, options):
        # Pass-through since no limit is required.
        return True
