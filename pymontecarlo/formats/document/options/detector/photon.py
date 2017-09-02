""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.document.options.detector.base import DetectorDocumentHandler
from pymontecarlo.options.detector.photon import PhotonDetector

# Globals and constants variables.

class PhotonDetectorDocumentHandler(DetectorDocumentHandler):

    def convert(self, detector, builder):
        super().convert(detector, builder)

        table = builder.require_table('photon detector')

        table.add_column('Name')
        table.add_column('Elevation', 'rad', PhotonDetector.ELEVATION_TOLERANCE_rad)
        table.add_column('Azimuth', 'rad', PhotonDetector.AZIMUTH_TOLERANCE_rad)

        row = {'Name': detector.name,
               'Elevation': detector.elevation_rad,
               'Azimuth': detector.azimuth_rad}
        table.add_row(row)

    @property
    def CLASS(self):
        return PhotonDetector
