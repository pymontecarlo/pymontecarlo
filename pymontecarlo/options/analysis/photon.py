"""
Photon related analysis.
"""

# Standard library modules.

# Third party modules.
import pyxray

# Local modules.
from pymontecarlo.options.analysis.base import Analysis, AnalysisBuilder

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

    def __repr__(self):
        return '<{classname}(detector={photon_detector})>' \
            .format(classname=self.__class__.__name__, **self.__dict__)

    @property
    def detectors(self):
        return super().detectors + (self.photon_detector,)

class PhotonAnalysisBuilder(AnalysisBuilder):

    def __init__(self):
        self.photon_detectors = []

    def __len__(self):
        return len(self.photon_detectors)

    def add_photon_detector(self, detector):
        if detector not in self.photon_detectors:
            self.photon_detectors.append(detector)
