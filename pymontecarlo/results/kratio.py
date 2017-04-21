""""""

# Standard library modules.

# Third party modules.
import uncertainties

# Local modules.
from pymontecarlo.results.photon import PhotonSingleResult, PhotonResultBuilder

# Globals and constants variables.

class KRatioResult(PhotonSingleResult):
    """
    Mapping of :class:`XrayLine` and k-ratios.
    """
    pass

class KRatioResultBuilder(PhotonResultBuilder):

    def __init__(self, analysis):
        super().__init__(analysis, KRatioResult)

    def add_kratio(self, xrayline, unkintensity, stdintensity):
        kratio = unkintensity / stdintensity
        if not hasattr(kratio, 's'):
            kratio = uncertainties.ufloat(kratio, 0.0)
        self._add(xrayline, kratio)
