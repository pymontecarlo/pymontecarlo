""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.detector.base import DetectorSeriesHandler
from pymontecarlo.options.detector.photon import PhotonDetector

# Globals and constants variables.

class PhotonDetectorSeriesHandler(DetectorSeriesHandler):

    def create_builder(self, detector):
        builder = super().create_builder(detector)

        name = '{} elevation angle'.format(detector.name)
        abbrev = '{} theta'.format(detector.name)
        builder.add_column(name, abbrev, detector.elevation_rad, 'rad', PhotonDetector.ELEVATION_TOLERANCE_rad)

        name = '{} azimuth angle'.format(detector.name)
        abbrev = '{} phi'.format(detector.name)
        builder.add_column(name, abbrev, detector.azimuth_rad, 'rad', PhotonDetector.AZIMUTH_TOLERANCE_rad)

        return builder

    @property
    def CLASS(self):
        return PhotonDetector
