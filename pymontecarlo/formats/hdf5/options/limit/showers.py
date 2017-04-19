""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.options.limit.base import LimitHDF5Handler
from pymontecarlo.options.limit.showers import ShowersLimit

# Globals and constants variables.

class ShowersLimitHDF5Handler(LimitHDF5Handler):

    ATTR_NUMBER_TRAJECTORIES = 'number trajectories'

    def _parse_showers(self, group):
        return int(group.attrs[self.ATTR_NUMBER_TRAJECTORIES])

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_NUMBER_TRAJECTORIES in group.attrs

    def parse(self, group):
        showers = self._parse_showers(group)
        return self.CLASS(showers)

    def _convert_number_trajectories(self, number_trajectories, group):
        group.attrs[self.ATTR_NUMBER_TRAJECTORIES] = number_trajectories

    def convert(self, limit, group):
        super().convert(limit, group)
        self._convert_number_trajectories(limit.number_trajectories, group)

    @property
    def CLASS(self):
        return ShowersLimit
