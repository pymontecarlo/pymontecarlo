"""
Analysis to record photon intensity emitted towards a detector.
"""

__all__ = ["PhotonIntensityAnalysis", "PhotonIntensityAnalysisBuilder"]

# Standard library modules.

# Third party modules.
import pyxray

# Local modules.
from pymontecarlo.options.analysis.photon import (
    PhotonAnalysisBase,
    PhotonAnalysisBuilderBase,
)

# Globals and constants variables.


class PhotonIntensityAnalysis(PhotonAnalysisBase):
    def __init__(self, photon_detector):
        super().__init__(photon_detector)

    def apply(self, options):
        return []

    def calculate(self, simulation, simulations):
        return super().calculate(simulation, simulations)

    # region HDF5

    @classmethod
    def parse_hdf5(cls, group):
        detector = cls._parse_hdf5(group, cls.ATTR_DETECTOR)
        return cls(detector)


# endregion


class PhotonIntensityAnalysisBuilder(PhotonAnalysisBuilderBase):
    def build(self):
        return [PhotonIntensityAnalysis(d) for d in self.photon_detectors]
