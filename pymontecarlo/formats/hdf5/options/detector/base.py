""""""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.base import HDF5Handler

# Globals and constants variables.

class DetectorHDF5HandlerMixin:

    GROUP_DETECTORS = 'detectors'

    def _parse_detector_internal(self, group, ref_detector):
        group_detector = group.file[ref_detector]
        return self._parse_hdf5handlers(group_detector)

    def _find_detectors_group(self, group):
        if self.GROUP_DETECTORS in group:
            return group[self.GROUP_DETECTORS]
        if group.parent == group:
            return None
        return self._find_detectors_group(group.parent)

    def _convert_detector_internal(self, detector, group):
        group_detectors = self._find_detectors_group(group)
        if group_detectors is None:
            group_detectors = group.create_group(self.GROUP_DETECTORS)

        name = '{} [{:d}]'.format(detector.__class__.__name__, id(detector))
        if name in group_detectors:
            return group_detectors[name]

        group_detector = group_detectors.create_group(name)

        self._convert_hdf5handlers(detector, group_detector)

        return group_detector

class DetectorHDF5Handler(HDF5Handler):

    ATTR_NAME = 'name'

    def _parse_name(self, group):
        return group.attrs[self.ATTR_NAME]

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_NAME in group.attrs

    def _convert_name(self, detector, group):
        group.attrs[self.ATTR_NAME] = detector.name

    @abc.abstractmethod
    def convert(self, detector, group):
        super().convert(detector, group)
        self._convert_name(detector, group)
