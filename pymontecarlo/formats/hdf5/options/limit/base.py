""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.base import HDF5Handler

# Globals and constants variables.

class LimitHDF5HandlerMixin:

    GROUP_LIMITS = 'limits'

    def _parse_limit_internal(self, group, ref_limit):
        group_limit = group.file[ref_limit]
        return self._parse_hdf5handlers(group_limit)

    def _require_limits_group(self, group):
        return group.file.require_group(self.GROUP_LIMITS)

    def _convert_limit_internal(self, limit, group):
        group_limits = self._require_limits_group(group)

        name = '{} [{:d}]'.format(limit.__class__.__name__, id(limit))
        if name in group_limits:
            return group_limits[name]

        group_limit = group_limits.create_group(name)

        self._convert_hdf5handlers(limit, group_limit)

        return group_limit

class LimitHDF5Handler(HDF5Handler):
    pass