""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.options.limit.base import LimitHDF5Handler
from pymontecarlo.formats.hdf5.options.detector.base import DetectorHDF5HandlerMixin
from pymontecarlo.options.limit.uncertainty import UncertaintyLimit

# Globals and constants variables.

class UncertaintyLimitHDF5Handler(LimitHDF5Handler, DetectorHDF5HandlerMixin):

    GROUP_XRAYLINE = 'xrayline'
    ATTR_DETECTOR = 'detector'
    ATTR_UNCERTAINTY = 'uncertainty'

    def _parse_xrayline(self, group):
        group_xrayline = group[self.GROUP_XRAYLINE]
        return self._parse_hdf5handlers(group_xrayline)

    def _parse_detector(self, group):
        ref_detector = group.attrs[self.ATTR_DETECTOR]
        return self._parse_detector_internal(group, ref_detector)

    def _parse_uncertainty(self, group):
        return float(group.attrs[self.ATTR_UNCERTAINTY])

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.GROUP_XRAYLINE in group and \
            self.ATTR_DETECTOR in group.attrs and \
            self.ATTR_UNCERTAINTY in group.attrs

    def parse(self, group):
        xrayline = self._parse_xrayline(group)
        detector = self._parse_detector(group)
        uncertainty = self._parse_uncertainty(group)
        return self.CLASS(xrayline, detector, uncertainty)

    def _convert_xrayline(self, xrayline, group):
        group_xrayline = group.create_group(self.GROUP_XRAYLINE)
        self._convert_hdf5handlers(xrayline, group_xrayline)

    def _convert_detector(self, detector, group):
        group_detector = self._convert_detector_internal(detector, group)
        group.attrs[self.ATTR_DETECTOR] = group_detector.ref

    def _convert_uncertainty(self, uncertainty, group):
        group.attrs[self.ATTR_UNCERTAINTY] = uncertainty

    def convert(self, limit, group):
        super().convert(limit, group)
        self._convert_xrayline(limit.xrayline, group)
        self._convert_detector(limit.detector, group)
        self._convert_uncertainty(limit.uncertainty, group)

    @property
    def CLASS(self):
        return UncertaintyLimit
