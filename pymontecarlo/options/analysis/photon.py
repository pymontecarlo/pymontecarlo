"""
Photon related analysis.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.analysis.base import AnalysisBase, AnalysisBuilderBase
import pymontecarlo.options.base as base

# Globals and constants variables.

COMMON_XRAY_TRANSITION_SETS = ('K', 'L', 'M', 'Ka', 'Kb', 'La', 'Ma', 'Mz')

class PhotonAnalysisBase(AnalysisBase):

    def __init__(self, photon_detector):
        self.photon_detector = photon_detector

    def __eq__(self, other):
        return super().__eq__(other) and \
            base.isclose(self.photon_detector, other.photon_detector)

    def __repr__(self):
        return '<{classname}(detector={photon_detector})>' \
            .format(classname=self.__class__.__name__, **self.__dict__)

    @property
    def detector(self):
        return self.photon_detector

#region HDF5

    ATTR_DETECTOR = 'detector'

    def convert_hdf5(self, group):
        super().convert_hdf5(group)
        self._convert_hdf5(group, self.ATTR_DETECTOR, self.photon_detector)

#endregion

class PhotonAnalysisBuilderBase(AnalysisBuilderBase):

    def __init__(self):
        self.photon_detectors = []

    def __len__(self):
        return len(self.photon_detectors)

    def add_photon_detector(self, detector):
        if detector not in self.photon_detectors:
            self.photon_detectors.append(detector)
