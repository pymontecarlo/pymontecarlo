"""
Intensity detector for photons.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.util.cbook import DegreesAttribute
from pymontecarlo.options.detector.base import Detector

# Globals and constants variables.

class PhotonIntensityDetector(Detector):

    def __init__(self, elevation_rad):
        self.elevation_rad = elevation_rad

    def __repr__(self):
        return '<{classname}({elevation_deg}\u00b0)>' \
            .format(classname=self.__class__.__name__,
                    elevation_deg=self.elevation_deg)

    def __eq__(self, other):
        return super().__eq__(other) and \
            self.elevation_rad == other.elevation_rad

    elevation_deg = DegreesAttribute('elevation_rad')

