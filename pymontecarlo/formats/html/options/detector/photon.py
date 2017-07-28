""""""

# Standard library modules.
from collections import OrderedDict

# Third party modules.

# Local modules.
from pymontecarlo.formats.html.options.detector.base import DetectorHtmlHandler
from pymontecarlo.options.detector.photon import PhotonDetector

# Globals and constants variables.

class PhotonDetectorHtmlHandler(DetectorHtmlHandler):

    def convert_rows(self, detector, settings):
        row = OrderedDict()

        key = self._create_label(settings, 'Name')
        value = self._format_value(settings, detector.name)
        row[key] = value

        key = self._create_label(settings, 'Elevation', 'rad')
        value = self._format_value(settings, detector.elevation_rad, 'rad', PhotonDetector.ELEVATION_TOLERANCE_rad)
        row[key] = value

        key = self._create_label(settings, 'Azimuth', 'rad')
        value = self._format_value(settings, detector.azimuth_rad, 'rad', PhotonDetector.AZIMUTH_TOLERANCE_rad)
        row[key] = value

        rows = super().convert_rows(detector, settings)
        rows.append(row)
        return rows

    @property
    def CLASS(self):
        return PhotonDetector
