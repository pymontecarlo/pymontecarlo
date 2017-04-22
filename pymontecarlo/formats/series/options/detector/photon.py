""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.detector.base import DetectorSeriesHandler
from pymontecarlo.formats.series.base import SeriesColumn
from pymontecarlo.options.detector.photon import PhotonDetector

# Globals and constants variables.

class PhotonDetectorSeriesHandler(DetectorSeriesHandler):

    def convert(self, detector):
        s = super().convert(detector)

        column = SeriesColumn('photon detector elevation angle', 'ph. det. theta', 'rad', PhotonDetector.ELEVATION_TOLERANCE_rad)
        s[column] = detector.elevation_rad

        column = SeriesColumn('photon detector azimuth angle', 'ph. det. phi', 'rad', PhotonDetector.AZIMUTH_TOLERANCE_rad)
        s[column] = detector.azimuth_rad

        return s

    @property
    def CLASS(self):
        return PhotonDetector
