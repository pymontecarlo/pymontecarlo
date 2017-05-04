""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.options.detector.base import DetectorHDF5Handler
from pymontecarlo.options.detector.photon import PhotonDetector

# Globals and constants variables.

class PhotonDetectorHDF5Handler(DetectorHDF5Handler):

    ATTR_ELEVATION = 'elevation (rad)'
    ATTR_AZIMUTH = 'azimuth (rad)'

    def _parse_elevation_rad(self, group):
        return float(group.attrs[self.ATTR_ELEVATION])

    def _parse_azimuth_rad(self, group):
        return float(group.attrs[self.ATTR_AZIMUTH])

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_ELEVATION in group.attrs and \
            self.ATTR_AZIMUTH in group.attrs

    def parse(self, group):
        name = self._parse_name(group)
        elevation_rad = self._parse_elevation_rad(group)
        azimuth_rad = self._parse_azimuth_rad(group)
        return self.CLASS(name, elevation_rad, azimuth_rad)

    def _convert_elevation_rad(self, elevation_rad, group):
        group.attrs[self.ATTR_ELEVATION] = elevation_rad

    def _convert_azimuth_rad(self, azimuth_rad, group):
        group.attrs[self.ATTR_AZIMUTH] = azimuth_rad

    def convert(self, detector, group):
        super().convert(detector, group)
        self._convert_elevation_rad(detector.elevation_rad, group)
        self._convert_azimuth_rad(detector.azimuth_rad, group)

    @property
    def CLASS(self):
        return PhotonDetector
