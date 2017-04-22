""""""

# Standard library modules.
from collections import OrderedDict

# Third party modules.

# Local modules.
from pymontecarlo.formats.html.options.detector.base import DetectorHtmlHandler
from pymontecarlo.options.detector.photon import PhotonDetector

# Globals and constants variables.

class PhotonDetectorHtmlHandler(DetectorHtmlHandler):

    def convert_rows(self, detector):
        row = OrderedDict()

        key = self._create_label('Name')
        value = self._format_value(detector.name)
        row[key] = value

        key = self._create_label('Elevation', 'rad')
        value = self._format_value(detector.elevation_rad, 'rad', PhotonDetector.ELEVATION_TOLERANCE_rad)
        row[key] = value

        key = self._create_label('Azimuth', 'rad')
        value = self._format_value(detector.azimuth_rad, 'rad', PhotonDetector.AZIMUTH_TOLERANCE_rad)
        row[key] = value

        rows = super().convert_rows(detector)
        rows.append(row)
        return rows

    @property
    def CLASS(self):
        return PhotonDetector
