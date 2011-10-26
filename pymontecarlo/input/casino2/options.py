#!/usr/bin/env python
"""
================================================================================
:mod:`options` -- Casino v2 options
================================================================================

.. module:: options
   :synopsis: Casino v2 options

.. inheritance-diagram:: options

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
from pymontecarlo.input.base.options import Options
from pymontecarlo.input.base.beam import GaussianBeam
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

class Casino2Options(Options):
    BEAMS = [GaussianBeam]
    GEOMETRIES = [Substrate, MultiLayers, GrainBoundaries]
    DETECTORS = [BackscatteredElectronEnergyDetector,
                 TransmittedElectronEnergyDetector,
                 BackscatteredElectronPolarAngularDetector,
                 PhiRhoZDetector,
                 PhotonIntensityDetector]
    LIMITS = [ShowersLimit]

    def __init__(self, name='Untitled'):
        """
        
        """
        Options.__init__(self, name)


