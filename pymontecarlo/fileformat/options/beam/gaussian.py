""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.fileformat.options.beam.base import BeamHDF5Handler
from pymontecarlo.options.beam.gaussian import GaussianBeam

# Globals and constants variables.

class GaussianBeamHDF5Handler(BeamHDF5Handler):

    ATTR_DIAMETER = 'diameter (m)'
    ATTR_X0 = 'x0 (m)'
    ATTR_Y0 = 'y0 (m)'
    ATTR_POLAR = 'polar (rad)'
    ATTR_AZIMUTH = 'azimuth (rad)'

    def _parse_diameter_m(self, group):
        return float(group.attrs[self.ATTR_DIAMETER])

    def _parse_x0_m(self, group):
        return float(group.attrs[self.ATTR_X0])

    def _parse_y0_m(self, group):
        return float(group.attrs[self.ATTR_Y0])

    def _parse_polar_rad(self, group):
        return float(group.attrs[self.ATTR_POLAR])

    def _parse_azimuth_rad(self, group):
        return float(group.attrs[self.ATTR_AZIMUTH])

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_DIAMETER in group.attrs and \
            self.ATTR_X0 in group.attrs and \
            self.ATTR_Y0 in group.attrs and \
            self.ATTR_POLAR in group.attrs and \
            self.ATTR_AZIMUTH in group.attrs

    def parse(self, group):
        energy_eV = self._parse_energy_eV(group)
        diameter_m = self._parse_diameter_m(group)
        particle = self._parse_particle(group)
        x0_m = self._parse_x0_m(group)
        y0_m = self._parse_y0_m(group)
        polar_rad = self._parse_polar_rad(group)
        azimuth_rad = self._parse_azimuth_rad(group)
        return self.CLASS(energy_eV, diameter_m, particle, x0_m, y0_m,
                          polar_rad, azimuth_rad)

    def _convert_diameter_m(self, beam, group):
        group.attrs[self.ATTR_DIAMETER] = beam.diameter_m

    def _convert_x0_m(self, beam, group):
        group.attrs[self.ATTR_X0] = beam.x0_m

    def _convert_y0_m(self, beam, group):
        group.attrs[self.ATTR_Y0] = beam.y0_m

    def _convert_polar_rad(self, beam, group):
        group.attrs[self.ATTR_POLAR] = beam.polar_rad

    def _convert_azimuth_rad(self, beam, group):
        group.attrs[self.ATTR_AZIMUTH] = beam.azimuth_rad

    def convert(self, beam, group):
        super().convert(beam, group)
        self._convert_diameter_m(beam, group)
        self._convert_x0_m(beam, group)
        self._convert_y0_m(beam, group)
        self._convert_polar_rad(beam, group)
        self._convert_azimuth_rad(beam, group)

    @property
    def CLASS(self):
        return GaussianBeam
