""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.results.photon import \
    PhotonResultSeriesHandler, xrayline_name_func
from pymontecarlo.results.photonintensity import \
    EmittedPhotonIntensityResult, GeneratedPhotonIntensityResult

# Globals and constants variables.

class PhotonIntensityResultSeriesHandler(PhotonResultSeriesHandler):

    def create_builder(self, result):
        builder = super().create_builder(result)

        for xrayline, q in result.items():
            name = abbrev = xrayline_name_func(xrayline)
            builder.add_column(name, abbrev, q.n, '1/(sr.electron)')
            builder.add_column(name, abbrev, q.s, '1/(sr.electron)', error=True)

        return builder

class EmittedPhotonIntensityResultSeriesHandler(PhotonIntensityResultSeriesHandler):

    @property
    def CLASS(self):
        return EmittedPhotonIntensityResult

class GeneratedPhotonIntensityResultSeriesHandler(PhotonIntensityResultSeriesHandler):

    @property
    def CLASS(self):
        return GeneratedPhotonIntensityResult
