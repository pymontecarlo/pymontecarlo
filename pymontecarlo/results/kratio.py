""""""

# Standard library modules.

# Third party modules.
import uncertainties

# Local modules.
from pymontecarlo.results.photon import PhotonSingleResultBase, PhotonResultBuilderBase
from pymontecarlo.formats.xrayline import LazyXrayLineFormat

# Globals and constants variables.

class KRatioResult(PhotonSingleResultBase):
    """
    Mapping of :class:`XrayLine` and k-ratios.
    """

    DATASET_VALUES = 'k-ratios'

#region Series

    def convert_series(self, builder):
        super().convert_series(builder)

        for xrayline, q in self.items():
            name = abbrev = LazyXrayLineFormat(xrayline)
            builder.add_column(name, abbrev, q.n)
            builder.add_column(name, abbrev, q.s, error=True)

#endregion

class KRatioResultBuilder(PhotonResultBuilderBase):

    def __init__(self, analysis):
        super().__init__(analysis, KRatioResult)

    def add_kratio(self, xrayline, unkintensity, stdintensity):
        kratio = unkintensity / stdintensity
        if not hasattr(kratio, 's'):
            kratio = uncertainties.ufloat(kratio, 0.0)
        self._add(xrayline, kratio)
