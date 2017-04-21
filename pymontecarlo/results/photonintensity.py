""""""

# Standard library modules.

# Third party modules.
import uncertainties

# Local modules.
from pymontecarlo.results.photon import PhotonSingleResult, PhotonResultBuilder

# Globals and constants variables.

class PhotonIntensityResult(PhotonSingleResult):
    """
    Mapping of :class:`XrayLine` and photon intensities, expressed in
    ``1/(sr.electron)``.
    """
    pass

class EmittedPhotonIntensityResult(PhotonIntensityResult):
    pass

class GeneratedPhotonIntensityResult(PhotonIntensityResult):
    pass

class PhotonIntensityResultBuilder(PhotonResultBuilder):

    def add_intensity(self, xrayline, value, error):
        """
        :arg value: intensity in ``1/(sr.electron)``
        
        :arg error: error on the intensity in ``1/(sr.electron)``
        """
        q = uncertainties.ufloat(value, error)
        self._add(xrayline, q)

class EmittedPhotonIntensityResultBuilder(PhotonIntensityResultBuilder):

    def __init__(self, analysis):
        super().__init__(analysis, EmittedPhotonIntensityResult)

class GeneratedPhotonIntensityResultBuilder(PhotonIntensityResultBuilder):

    def __init__(self, analysis):
        super().__init__(analysis, GeneratedPhotonIntensityResult)
