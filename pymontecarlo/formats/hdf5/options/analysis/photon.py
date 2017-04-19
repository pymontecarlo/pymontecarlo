""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.options.analysis.base import AnalysisHDF5Handler

# Globals and constants variables.

class PhotonAnalysisHDF5Handler(AnalysisHDF5Handler):

    ATTR_DETECTOR = 'detector'

    def _parse_photon_detector(self, group):
        ref_detector = group.attrs[self.ATTR_DETECTOR]
        return self._parse_detector_internal(group, ref_detector)

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_DETECTOR in group.attrs

    def _convert_photon_detector(self, detector, group):
        group_detector = self._convert_detector_internal(detector, group)
        group.attrs[self.ATTR_DETECTOR] = group_detector.ref

    def convert(self, analysis, group):
        super().convert(analysis, group)
        self._convert_photon_detector(analysis.photon_detector, group)
