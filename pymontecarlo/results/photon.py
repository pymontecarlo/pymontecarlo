"""
Photon based results.
"""

# Standard library modules.
import collections.abc

# Third party modules.
import pyxray
import uncertainties

# Local modules.
from pymontecarlo.results.base import ResultBase, ResultBuilderBase

# Globals and constants variables.

def _convert_xrayline(xrayline):
    if isinstance(xrayline, pyxray.XrayLine):
        return xrayline

    try:
        return pyxray.xray_line(*xrayline)
    except:
        raise ValueError('"{}" is not an XrayLine'.format(xrayline))

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
        xrayline = _convert_xrayline(xrayline)
        return self.data[xrayline]

    def __repr__(self):
        return '<{}({})>'.format(self.__class__.__name__,
                                 ', '.join(map(str, self)))

    @property
    def atomic_numbers(self):
        return frozenset(xrayline.z for xrayline in self.keys())

class PhotonSingleResultBase(PhotonResultBase):

    _DEFAULT = object()

    def get(self, key, default=_DEFAULT):
        if default is self._DEFAULT:
            default = uncertainties.ufloat(0.0, 0.0)
        return super().get(key, default)

class PhotonResultBuilderBase(ResultBuilderBase):

    def __init__(self, analysis, result_class):
        super().__init__(analysis)
        self.data = {}
        self.result_class = result_class

    def _add(self, xrayline, datum):
        xrayline = _convert_xrayline(xrayline)
        self.data[xrayline] = datum

    def build(self):
        return self.result_class(self.analysis, self.data.copy())
