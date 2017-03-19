""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo import unit_registry
from pymontecarlo.results.photon import PhotonResult, PhotonResultBuilder
from pymontecarlo.util.datarow import DataRowCreator

# Globals and constants variables.

class KRatioResult(PhotonResult, DataRowCreator):
    """
    Mapping of :class:`XrayLine` and k-ratios.
    """

    _DEFAULT = object()

    def get(self, key, default=_DEFAULT):
        if default is self._DEFAULT:
            default = unit_registry.Quantity(0.0).plus_minus(0.0)
        return super().get(key, default)

    def create_datarow(self, **kwargs):
        datarow = super().create_datarow()

        for xrayline, q in self.items():
            datarow.add(xrayline, q.n, q.s, q.units)

        return datarow

class KRatioResultBuilder(PhotonResultBuilder):

    def __init__(self, analysis):
        super().__init__(analysis, KRatioResult)

    def add_kratio(self, xrayline, unkintensity, stdintensity):
        kratio = unkintensity / stdintensity
        self._add(xrayline, kratio)
