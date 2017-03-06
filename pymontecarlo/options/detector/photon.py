"""
Photon (X-ray) detector.
"""

# Standard library modules.
import math

# Third party modules.

# Local modules.
from pymontecarlo.options.detector.base import Detector
from pymontecarlo.util.cbook import DegreesAttribute

# Globals and constants variables.

class PhotonDetector(Detector):

    ELEVATION_TOLERANCE_rad = math.radians(1e-3) # 0.001 deg
    AZIMUTH_TOLERANCE_rad = math.radians(1e-3) # 0.001 deg

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
            math.isclose(self.elevation_rad, other.elevation_rad, abs_tol=self.ELEVATION_TOLERANCE_rad) and \
            math.isclose(self.azimuth_rad, other.azimuth_rad, abs_tol=self.AZIMUTH_TOLERANCE_rad)

    def create_datarow(self, **kwargs):
        datarow = super().create_datarow(**kwargs)
        datarow.add('photon detector elevation angle', self.elevation_rad, 0.0, 'rad', self.ELEVATION_TOLERANCE_rad)
        datarow.add('photon detector azimuth angle', self.azimuth_rad, 0.0, 'rad', self.AZIMUTH_TOLERANCE_rad)
        return datarow

    elevation_deg = DegreesAttribute('elevation_rad')
    azimuth_deg = DegreesAttribute('azimuth_rad')

