""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo import unit_registry
from pymontecarlo.results.photon import PhotonResult, PhotonResultBuilder
from pymontecarlo.util.datarow import DataRowCreator

# Globals and constants variables.

class PhotonIntensityResult(PhotonResult, DataRowCreator):
    """
    Mapping of :class:`XrayLine` and photon intensities, expressed in
    ``1/(sr.electron)``.
    """

    _DEFAULT = object()

    def get(self, key, default=_DEFAULT):
        if default is self._DEFAULT:
            default = unit_registry.Quantity(0.0, '1/(sr.electron)').plus_minus(0.0)
        return super().get(key, default)

    def create_datarow(self, **kwargs):
        datarow = super().create_datarow()

        for xrayline, q in self.items():
            datarow.add(xrayline, q.n, q.s, q.units)

        return datarow

class EmittedPhotonIntensityResult(PhotonIntensityResult):
    pass

class GeneratedPhotonIntensityResult(PhotonIntensityResult):
    pass

class PhotonIntensityResultBuilder(PhotonResultBuilder):

    def add_intensity(self, xrayline, value, error, unit='1/(sr.electron)'):
        q = unit_registry.Quantity(value, unit).plus_minus(error)
        q = q.to('1/(sr.electron)')
        self._add(xrayline, q)

class EmittedPhotonIntensityResultBuilder(PhotonIntensityResultBuilder):

    def __init__(self, analysis):
        super().__init__(analysis, EmittedPhotonIntensityResult)

class GeneratedPhotonIntensityResultBuilder(PhotonIntensityResultBuilder):

    def __init__(self, analysis):
        super().__init__(analysis, GeneratedPhotonIntensityResult)
