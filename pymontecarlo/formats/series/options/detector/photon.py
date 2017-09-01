""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.detector.base import DetectorSeriesHandler
from pymontecarlo.formats.series.base import NamedSeriesColumn
from pymontecarlo.options.detector.photon import PhotonDetector

# Globals and constants variables.

class PhotonDetectorSeriesHandler(DetectorSeriesHandler):

    def convert(self, detector):
        s = super().convert(detector)

        name = '{} elevation angle'.format(detector.name)
        abbrev = '{} theta'.format(detector.name)
        column = NamedSeriesColumn(name, abbrev, 'rad', PhotonDetector.ELEVATION_TOLERANCE_rad)
        s[column] = detector.elevation_rad

        name = '{} azimuth angle'.format(detector.name)
        abbrev = '{} phi'.format(detector.name)
        column = NamedSeriesColumn(name, abbrev, 'rad', PhotonDetector.AZIMUTH_TOLERANCE_rad)
        s[column] = detector.azimuth_rad

        return s

    @property
    def CLASS(self):
        return PhotonDetector
