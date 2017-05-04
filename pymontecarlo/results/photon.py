"""
Photon based results.
"""

# Standard library modules.
import collections

# Third party modules.
import uncertainties

# Local modules.
from pymontecarlo.results.base import Result, ResultBuilder
from pymontecarlo.util.xrayline import XrayLine

# Globals and constants variables.

class PhotonResult(Result, collections.Mapping):
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
        xrayline = XrayLine(*xrayline)
        return self.data[xrayline]

    def __repr__(self):
        return '<{}({})>'.format(self.__class__.__name__,
                                 ', '.join(map(str, self)))

class PhotonSingleResult(PhotonResult):

    _DEFAULT = object()

    def get(self, key, default=_DEFAULT):
        if default is self._DEFAULT:
            default = uncertainties.ufloat(0.0, 0.0)
        return super().get(key, default)

class PhotonResultBuilder(ResultBuilder):

    def __init__(self, analysis, result_class):
        super().__init__(analysis)
        self.data = {}
        self.result_class = result_class

    def _add(self, xrayline, datum):
        xrayline = XrayLine(*xrayline)
        self.data[xrayline] = datum

    def build(self):
        return self.result_class(self.analysis, self.data.copy())
