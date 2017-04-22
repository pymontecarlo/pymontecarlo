""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.results.photon import \
    PhotonResultSeriesHandler, XrayLineSeriesColumn
from pymontecarlo.results.photonintensity import \
    EmittedPhotonIntensityResult, GeneratedPhotonIntensityResult

# Globals and constants variables.

class PhotonIntensityResultSeriesHandler(PhotonResultSeriesHandler):

    def convert(self, result):
        s = super().convert(result)

        for xrayline, q in result.items():
            column = XrayLineSeriesColumn(xrayline, unit='1/(sr.electron)')
            s[column] = q

        return s

class EmittedPhotonIntensityResultSeriesHandler(PhotonIntensityResultSeriesHandler):

    @property
    def CLASS(self):
        return EmittedPhotonIntensityResult

class GeneratedPhotonIntensityResultSeriesHandler(PhotonIntensityResultSeriesHandler):

    @property
    def CLASS(self):
        return GeneratedPhotonIntensityResult
