"""
Analysis to record photon intensity emitted towards a detector.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.analyses.base import Analysis

# Globals and constants variables.

class PhotonIntensityAnalysis(Analysis):

    def __init__(self, photon_detector):
        self.photon_detector = photon_detector

    def __eq__(self, other):
        return super().__eq__(other) and \
            self.photon_detector == other.photon_detector

    def apply(self, options):
        return []

    def calculate(self, simulation, simulations):
        pass

    @property
    def detectors(self):
        return super().detectors + (self.photon_detector,)
