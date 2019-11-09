""""""

__all__ = [
    "EmittedPhotonIntensityResult",
    "GeneratedPhotonIntensityResult",
    "EmittedPhotonIntensityResultBuilder",
    "GeneratedPhotonIntensityResultBuilder",
]

# Standard library modules.

# Third party modules.
import uncertainties

# Local modules.
from pymontecarlo.results.photon import PhotonSingleResultBase, PhotonResultBuilderBase

# Globals and constants variables.


class PhotonIntensityResultBase(PhotonSingleResultBase):
    """
    Mapping of :class:`XrayLine` and photon intensities, expressed in
    ``1/(sr.electron)``.
    """

    DATASET_VALUES = "intensities"

    # region Series

    def convert_series(self, builder):
        super().convert_series(builder)

        for xrayline, q in self.items():
            builder.add_column(xrayline, xrayline, q.n, "1/(sr.electron)")
            builder.add_column(xrayline, xrayline, q.s, "1/(sr.electron)", error=True)


# endregion


class EmittedPhotonIntensityResult(PhotonIntensityResultBase):
    pass


class GeneratedPhotonIntensityResult(PhotonIntensityResultBase):
    pass


class PhotonIntensityResultBuilder(PhotonResultBuilderBase):
    def add_intensity(self, xrayline, value, error):
        """
        :arg value: intensity in ``1/(sr.electron)``

        :arg error: error on the intensity in ``1/(sr.electron)``
        """
        q = uncertainties.ufloat(value, error)
        self._add(xrayline, q)

    def _sum_results(self, results):
        return sum(results)


class EmittedPhotonIntensityResultBuilder(PhotonIntensityResultBuilder):
    def __init__(self, analysis):
        super().__init__(analysis, EmittedPhotonIntensityResult)


class GeneratedPhotonIntensityResultBuilder(PhotonIntensityResultBuilder):
    def __init__(self, analysis):
        super().__init__(analysis, GeneratedPhotonIntensityResult)
