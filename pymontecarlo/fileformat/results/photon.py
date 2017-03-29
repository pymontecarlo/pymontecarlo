""""""

# Standard library modules.
import abc
import operator

# Third party modules.
import h5py

import numpy as np

# Local modules.
from pymontecarlo import unit_registry
from pymontecarlo.fileformat.results.base import ResultHDF5Handler

# Globals and constants variables.

class PhotonResultHDF5Handler(ResultHDF5Handler):

    GROUP_ANALYSIS = 'analysis'
    GROUP_XRAYLINES = 'xraylines'
    DATASET_XRAYLINE_REFERENCES = 'xrayline scale'

    DATASET_QUANTITY = 'quantity scale'
    ATTR_UNIT = 'unit'

    def _parse_analysis(self, group):
        group_analysis = group[self.GROUP_ANALYSIS]
        return self._parse_hdf5handlers(group_analysis)

    def _parse_keys(self, group):
        keys = []

        for ref_xrayline in group[self.DATASET_XRAYLINE_REFERENCES]:
            group_xrayline = group.file[ref_xrayline]
            keys.append(self._parse_hdf5handlers(group_xrayline))

        return keys

    @abc.abstractmethod
    def _parse_values(self, group):
        raise NotImplementedError

    def _parse_values_0d(self, name, group):
        unit = unit_registry.parse_units(group[name].attrs[self.ATTR_UNIT])

        values = []

        for n, s in group[name]:
            q = unit_registry.Quantity(n, unit).plus_minus(s)
            values.append(q)

        return values

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.GROUP_ANALYSIS in group and \
            self.GROUP_XRAYLINES in group and \
            self.DATASET_XRAYLINE_REFERENCES in group

    def parse(self, group):
        analysis = self._parse_analysis(group)
        keys = self._parse_keys(group)
        values = self._parse_values(group)
        data = dict(zip(keys, values))
        return self.CLASS(analysis, data)

    def _convert_analysis(self, analysis, group):
        group_analysis = group.create_group(self.GROUP_ANALYSIS)
        self._convert_hdf5handlers(analysis, group_analysis)

    def _convert_keys(self, keys, group):
        group_xraylines = group.create_group(self.GROUP_XRAYLINES)

        shape = (len(keys),)
        dtype = h5py.special_dtype(ref=h5py.Reference)
        ds_keys = group.create_dataset(self.DATASET_XRAYLINE_REFERENCES,
                                       shape=shape, dtype=dtype)

        for i, xrayline in enumerate(keys):
            group_xrayline = group_xraylines.create_group(str(xrayline))
            self._convert_hdf5handlers(xrayline, group_xrayline)
            ds_keys[i] = group_xrayline.ref

        return ds_keys

    @abc.abstractmethod
    def _convert_values(self, values, group):
        raise NotImplementedError

    def _convert_values_0d(self, values, name, group):
        shape = (len(values), 2)
        dtype = np.float
        ds_values = group.create_dataset(name, shape=shape, dtype=dtype)
        ds_values.attrs[self.ATTR_UNIT] = str(values[0].units)

        for i, quantity in enumerate(values):
            ds_values[i] = [quantity.n, quantity.s]

        # Scale of second axis
        data = np.string_(['nominal', 'standard deviation'])
        ds_quantity = group.create_dataset(self.DATASET_QUANTITY, data=data)
        ds_values.dims.create_scale(ds_quantity)
        ds_values.dims[1].attach_scale(ds_quantity)

        return ds_values

    def convert(self, result, group):
        super().convert(result, group)

        self._convert_analysis(result.analysis, group)

        items = result.items()
        keys = list(map(operator.itemgetter(0), items))
        values = list(map(operator.itemgetter(1), items))
        ds_keys = self._convert_keys(keys, group)
        ds_values = self._convert_values(values, group)

        ds_values.dims.create_scale(ds_keys)
        ds_values.dims[0].attach_scale(ds_keys)
