"""
Photon (X-ray) detector.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.detector.base import Detector
from pymontecarlo.util.cbook import DegreesAttribute

# Globals and constants variables.

class PhotonDetector(Detector):

    def __init__(self, elevation_rad, azimuth_rad=0.0):
        super().__init__()

        self.elevation_rad = elevation_rad
        self.azimuth_rad = azimuth_rad

    def __repr__(self):
        return '<{classname}(elevation={elevation_deg}\u00b0, azimuth={azimuth_deg}\u00b0)>' \
            .format(classname=self.__class__.__name__,
                    elevation_deg=self.elevation_deg,
                    azimuth_deg=self.azimuth_deg)

    def __eq__(self, other):
        return super().__eq__(other) and \
            self.elevation_rad == other.elevation_rad and \
            self.azimuth_rad == other.azimuth_rad

    def create_datarow(self):
        datarow = super().create_datarow()
        datarow['photon detector elevation angle (rad)'] = self.elevation_rad
        datarow['photon detector azimuth angle (rad)'] = self.azimuth_rad
        return datarow

    elevation_deg = DegreesAttribute('elevation_rad')
    azimuth_deg = DegreesAttribute('azimuth_rad')

