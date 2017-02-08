"""
Photon related analysis.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.analyses.base import Analysis

# Globals and constants variables.

class PhotonAnalysis(Analysis):

    def __init__(self, photon_detector):
        self.photon_detector = photon_detector

    def __eq__(self, other):
        return super().__eq__(other) and \
            self.photon_detector == other.photon_detector

    @property
    def detectors(self):
        return super().detectors + (self.photon_detector,)