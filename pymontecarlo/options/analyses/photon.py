"""
Photon related analysis.
"""

# Standard library modules.

# Third party modules.
import pyxray

# Local modules.
from pymontecarlo.options.analyses.base import Analysis

# Globals and constants variables.

COMMON_XRAY_TRANSITION_SETS = \
    [pyxray.xray_transitionset('K'),
     pyxray.xray_transitionset('L'),
     pyxray.xray_transitionset('M'),
     pyxray.xray_transitionset('Ka'), pyxray.xray_transitionset('Kb'),
     pyxray.xray_transitionset('La'),
     pyxray.xray_transitionset('Ma'), pyxray.xray_transitionset('Mz')]

class PhotonAnalysis(Analysis):

    def __init__(self, photon_detector):
        self.photon_detector = photon_detector

    def __eq__(self, other):
        return super().__eq__(other) and \
            self.photon_detector == other.photon_detector

    def create_datarow(self, **kwargs):
        datarow = super().create_datarow(**kwargs)
        datarow |= self.photon_detector.create_datarow(**kwargs)
        return datarow

    @property
    def detectors(self):
        return super().detectors + (self.photon_detector,)
