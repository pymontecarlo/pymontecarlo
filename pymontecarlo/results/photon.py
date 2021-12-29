"""
Photon based results.
"""

# Standard library modules.
import collections.abc
import abc

# Third party modules.
import uncertainties
import h5py
import numpy as np
import pyxray

# Local modules.
from pymontecarlo.results.base import ResultBase, ResultBuilderBase
from pymontecarlo.util.xrayline import convert_xrayline

# Globals and constants variables.


class PhotonResultBase(ResultBase, collections.abc.Mapping):
    """
    Base class for photon based results.
    It consists of a :class:`Mapping` where keys are :class:`XrayLine` and
    values are the photon result (intensity, distribution, etc.).
    """

    def __init__(self, analysis, data):
        super().__init__(analysis)
        self.data = data

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, xrayline):
        xrayline = convert_xrayline(xrayline)
        return self.data[xrayline]

    def __repr__(self):
        return "<{}({})>".format(self.__class__.__name__, ", ".join(map(str, self)))

    @property
    def atomic_numbers(self):
        return frozenset(xrayline.z for xrayline in self.keys())

    # region HDF5

    DATASET_XRAYLINES = "x-ray lines"


# endregion


class PhotonSingleResultBase(PhotonResultBase):

    _DEFAULT = object()

    def get(self, key, default=_DEFAULT):
        if default is self._DEFAULT:
            default = uncertainties.ufloat(0.0, 0.0)
        return super().get(key, default)

    # region HDF5

    DATASET_VALUES = "values"
    DATASET_SCALE = "scale"

    @classmethod
    def parse_hdf5(cls, group):
        analysis = cls._parse_hdf5(group, cls.ATTR_ANALYSIS)

        keys = [
            convert_xrayline(iupac.split(" ", 1))
            for iupac in group[cls.DATASET_XRAYLINES].asstr()
        ]
        values = [uncertainties.ufloat(n, s) for n, s in group[cls.DATASET_VALUES]]
        data = dict(zip(keys, values))

        return cls(analysis, data)

    def convert_hdf5(self, group):
        super().convert_hdf5(group)

        # Create datasets
        shape = (len(self.data),)
        dtype = h5py.special_dtype(vlen=str)
        dataset_keys = group.create_dataset(self.DATASET_XRAYLINES, shape, dtype)

        shape = (len(self.data), 2)
        dtype = float
        dataset_values = group.create_dataset(self.DATASET_VALUES, shape, dtype)

        # Scale of values
        data = np.string_(["nominal", "standard deviation"])
        dataset_scale = group.create_dataset(self.DATASET_SCALE, data=data)

        dataset_scale.make_scale()
        dataset_values.dims[1].label = self.DATASET_SCALE
        dataset_values.dims[1].attach_scale(dataset_scale)

        # Store values
        for i, (xrayline, value) in enumerate(self.data.items()):
            dataset_keys[i] = xrayline.iupac
            dataset_values[i] = [value.n, value.s]


# endregion


class PhotonResultBuilderBase(ResultBuilderBase):

    _EXTRA_TRANSITIONS = (
        pyxray.xray_transition("K"),
        pyxray.xray_transition("L"),
        pyxray.xray_transition("M"),
        pyxray.xray_transition("N"),
        pyxray.xray_transition("Ka"),
        pyxray.xray_transition("La"),
        pyxray.xray_transition("Ll,n"),
        pyxray.xray_transition("Ma"),
        pyxray.xray_transition("Mz"),
    )

    def __init__(self, analysis, result_class):
        super().__init__(analysis)
        self.data = {}
        self.result_class = result_class

    def _add(self, xrayline, result):
        xrayline = convert_xrayline(xrayline)
        self.data[xrayline] = result

    @abc.abstractmethod
    def _sum_results(self, results):
        raise NotImplementedError

    def _create_extra_transitions(self):
        # Expand data
        element_transition_results = {}
        for xrayline, result in self.data.items():
            element_transition_results.setdefault(xrayline.element, {})[
                xrayline.transition
            ] = result

        newdata = {}
        for element in element_transition_results:
            for extra_transition in self._EXTRA_TRANSITIONS:
                # If the transition already exists, we skip
                if extra_transition in element_transition_results[element]:
                    continue

                # Search for the possible transitions (i.e. expand the extra transition)
                try:
                    possible_transitions = pyxray.element_xray_transitions(
                        element, extra_transition
                    )
                except pyxray.NotFound:
                    continue

                # Find the results
                results = [
                    result
                    for transition, result in element_transition_results[
                        element
                    ].items()
                    if transition in possible_transitions
                ]

                # If no results, do nothing
                if not results:
                    continue

                # Add new entry
                try:
                    xrayline = pyxray.xray_line(element, extra_transition)
                except pyxray.NotFound:
                    continue

                newdata[xrayline] = self._sum_results(results)

        return newdata

    def build(self):
        data = self.data.copy()
        data.update(self._create_extra_transitions())
        return self.result_class(self.analysis, data)
