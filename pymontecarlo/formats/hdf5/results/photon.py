""""""

# Standard library modules.
import abc
import operator

# Third party modules.
import h5py

import numpy as np

import uncertainties

# Local modules.
from pymontecarlo.formats.hdf5.results.base import ResultHDF5Handler
from pymontecarlo.formats.hdf5.options.analysis.base import AnalysisHDF5HandlerMixin
from pymontecarlo.formats.hdf5.util.xrayline import XrayLineHDF5HandlerMixin

# Globals and constants variables.

class PhotonResultHDF5Handler(ResultHDF5Handler,
                              AnalysisHDF5HandlerMixin,
                              XrayLineHDF5HandlerMixin):

    ATTR_ANALYSIS = 'analysis'
    DATASET_XRAYLINE_REFERENCES = 'xrayline scale'
    DATASET_QUANTITY = 'quantity scale'

    def _parse_analysis(self, group):
        ref_analysis = group.attrs[self.ATTR_ANALYSIS]
        return self._parse_analysis_internal(group, ref_analysis)

    def _parse_keys(self, group):
        keys = []

        for ref_xrayline in group[self.DATASET_XRAYLINE_REFERENCES]:
            keys.append(self._parse_xrayline_internal(group, ref_xrayline))

        return keys

    @abc.abstractmethod
    def _parse_values(self, group):
        raise NotImplementedError

    def _parse_values_0d(self, name, group):
        values = []

        for n, s in group[name]:
            q = uncertainties.ufloat(n, s)
            values.append(q)

        return values

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_ANALYSIS in group.attrs and \
            self.DATASET_XRAYLINE_REFERENCES in group and \
            self.DATASET_QUANTITY in group

    def parse(self, group):
        analysis = self._parse_analysis(group)
        keys = self._parse_keys(group)
        values = self._parse_values(group)
        data = dict(zip(keys, values))
        return self.CLASS(analysis, data)

    def _convert_analysis(self, analysis, group):
        group_analysis = self._convert_analysis_internal(analysis, group)
        group.attrs[self.ATTR_ANALYSIS] = group_analysis.ref

    def _convert_keys(self, keys, group):
        shape = (len(keys),)
        dtype = h5py.special_dtype(ref=h5py.Reference)
        ds_keys = group.create_dataset(self.DATASET_XRAYLINE_REFERENCES,
                                       shape=shape, dtype=dtype)

        for i, xrayline in enumerate(keys):
            group_xrayline = self._convert_xrayline_internal(xrayline, group)
            ds_keys[i] = group_xrayline.ref

        return ds_keys

    @abc.abstractmethod
    def _convert_values(self, values, group):
        raise NotImplementedError

    def _convert_values_0d(self, values, name, group):
        shape = (len(values), 2)
        dtype = np.float
        ds_values = group.create_dataset(name, shape=shape, dtype=dtype)

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
