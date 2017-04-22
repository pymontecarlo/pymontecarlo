"""
Photon (X-ray) detector.
"""

# Standard library modules.
import math
import itertools

# Third party modules.

# Local modules.
from pymontecarlo.options.detector.base import Detector, DetectorBuilder
from pymontecarlo.util.cbook import DegreesAttribute

# Globals and constants variables.

class PhotonDetector(Detector):

    ELEVATION_TOLERANCE_rad = math.radians(1e-3) # 0.001 deg
    AZIMUTH_TOLERANCE_rad = math.radians(1e-3) # 0.001 deg

    def __init__(self, name, elevation_rad, azimuth_rad=0.0):
        super().__init__(name)

        self.elevation_rad = elevation_rad
        self.azimuth_rad = azimuth_rad

    def __repr__(self):
        return '<{classname}({name}, elevation={elevation_deg}\u00b0, azimuth={azimuth_deg}\u00b0)>' \
            .format(classname=self.__class__.__name__,
                    name=self.name,
                    elevation_deg=self.elevation_deg,
                    azimuth_deg=self.azimuth_deg)

    def __eq__(self, other):
        return super().__eq__(other) and \
            math.isclose(self.elevation_rad, other.elevation_rad, abs_tol=self.ELEVATION_TOLERANCE_rad) and \
            math.isclose(self.azimuth_rad, other.azimuth_rad, abs_tol=self.AZIMUTH_TOLERANCE_rad)

    elevation_deg = DegreesAttribute('elevation_rad')
    azimuth_deg = DegreesAttribute('azimuth_rad')

class PhotonDetectorBuilder(DetectorBuilder):

    def __init__(self):
        self.elevations_rad = set()
        self.azimuths_rad = set()

    def __len__(self):
        azimuths_rad = self._calculate_azimuth_combinations()
        return len(self.elevations_rad) * len(azimuths_rad)

    def _calculate_azimuth_combinations(self):
        azimuths_rad = self.azimuths_rad

        if not azimuths_rad:
            azimuths_rad = [0.0]

        return azimuths_rad

    def add_elevation_rad(self, elevation_rad):
        self.elevations_rad.add(elevation_rad)

    def add_elevation_deg(self, elevation_deg):
        self.add_elevation_rad(math.radians(elevation_deg))

    def add_azimuth_rad(self, azimuth_rad):
        self.azimuths_rad.add(azimuth_rad)

    def add_azimuth_deg(self, azimuth_deg):
        self.add_azimuth_rad(math.radians(azimuth_deg))

    def build(self):
        elevations_rad = self.elevations_rad
        azimuths_rad = self._calculate_azimuth_combinations()

        product = itertools.product(elevations_rad, azimuths_rad)
        return [PhotonDetector('det{:d}'.format(i), *args)
                for i, args in enumerate(product)]
