"""
Photon (X-ray) detector.
"""

__all__ = ["PhotonDetector", "PhotonDetectorBuilder"]

# Standard library modules.
import math
import itertools

# Third party modules.

# Local modules.
from pymontecarlo.options.detector.base import DetectorBase, DetectorBuilderBase
import pymontecarlo.options.base as base

# Globals and constants variables.


class PhotonDetector(DetectorBase):

    ELEVATION_TOLERANCE_rad = math.radians(1e-3)  # 0.001 deg
    AZIMUTH_TOLERANCE_rad = math.radians(1e-3)  # 0.001 deg

    def __init__(self, name, elevation_rad, azimuth_rad=0.0):
        super().__init__(name)

        self.elevation_rad = elevation_rad
        self.azimuth_rad = azimuth_rad

    def __repr__(self):
        return "<{classname}({name}, elevation={elevation_deg}\u00b0, azimuth={azimuth_deg}\u00b0)>".format(
            classname=self.__class__.__name__,
            name=self.name,
            elevation_deg=self.elevation_deg,
            azimuth_deg=self.azimuth_deg,
        )

    def __eq__(self, other):
        return (
            super().__eq__(other)
            and base.isclose(
                self.elevation_rad,
                other.elevation_rad,
                abs_tol=self.ELEVATION_TOLERANCE_rad,
            )
            and base.isclose(
                self.azimuth_rad, other.azimuth_rad, abs_tol=self.AZIMUTH_TOLERANCE_rad
            )
        )

    elevation_deg = base.DegreesAttribute("elevation_rad")
    azimuth_deg = base.DegreesAttribute("azimuth_rad")

    # region HDF5

    ATTR_ELEVATION = "elevation (rad)"
    ATTR_AZIMUTH = "azimuth (rad)"

    @classmethod
    def parse_hdf5(cls, group):
        name = cls._parse_hdf5(group, cls.ATTR_NAME, str)
        elevation_rad = cls._parse_hdf5(group, cls.ATTR_ELEVATION, float)
        azimuth_rad = cls._parse_hdf5(group, cls.ATTR_AZIMUTH, float)
        return cls(name, elevation_rad, azimuth_rad)

    def convert_hdf5(self, group):
        super().convert_hdf5(group)
        self._convert_hdf5(group, self.ATTR_ELEVATION, self.elevation_rad)
        self._convert_hdf5(group, self.ATTR_AZIMUTH, self.azimuth_rad)

    # endregion

    # region Series

    def convert_series(self, builder):
        super().convert_series(builder)
        name = "{} elevation angle".format(self.name)
        abbrev = "{} theta".format(self.name)
        builder.add_column(
            name, abbrev, self.elevation_rad, "rad", self.ELEVATION_TOLERANCE_rad
        )

        name = "{} azimuth angle".format(self.name)
        abbrev = "{} phi".format(self.name)
        builder.add_column(
            name, abbrev, self.azimuth_rad, "rad", self.AZIMUTH_TOLERANCE_rad
        )

    # endregion

    # region Document

    TABLE_PHOTON_DETECTOR = "photon detector"

    def convert_document(self, builder):
        super().convert_document(builder)

        table = builder.require_table(self.TABLE_PHOTON_DETECTOR)

        table.add_column("Name")
        table.add_column("Elevation", "rad", self.ELEVATION_TOLERANCE_rad)
        table.add_column("Azimuth", "rad", self.AZIMUTH_TOLERANCE_rad)

        row = {
            "Name": self.name,
            "Elevation": self.elevation_rad,
            "Azimuth": self.azimuth_rad,
        }
        table.add_row(row)


# endregion


class PhotonDetectorBuilder(DetectorBuilderBase):
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
        return [
            PhotonDetector("det{:d}".format(i), *args) for i, args in enumerate(product)
        ]
