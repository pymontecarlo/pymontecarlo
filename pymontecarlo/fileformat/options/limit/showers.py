""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.fileformat.options.limit.base import LimitHDF5Handler
from pymontecarlo.options.limit.showers import ShowersLimit

# Globals and constants variables.

class ShowersLimitHDF5Handler(LimitHDF5Handler):

    ATTR_SHOWERS = 'showers'

    def _parse_showers(self, group):
        return int(group.attrs[self.ATTR_SHOWERS])

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_SHOWERS in group.attrs

    def parse(self, group):
        showers = self._parse_showers(group)
        return self.CLASS(showers)

    def _convert_showers(self, showers, group):
        group.attrs[self.ATTR_SHOWERS] = showers

    def convert(self, limit, group):
        super().convert(limit, group)
        self._convert_showers(limit.showers, group)

    @property
    def CLASS(self):
        return ShowersLimit
