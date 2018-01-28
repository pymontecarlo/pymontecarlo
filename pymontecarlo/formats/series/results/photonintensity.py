""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.results.photon import \
    PhotonResultSeriesHandlerBase, xrayline_name_func
from pymontecarlo.results.photonintensity import \
    EmittedPhotonIntensityResult, GeneratedPhotonIntensityResult

# Globals and constants variables.

class PhotonIntensityResultSeriesHandlerBase(PhotonResultSeriesHandlerBase):

    def convert(self, result, builder):
        super().convert(result, builder)

        for xrayline, q in result.items():
            name = abbrev = xrayline_name_func(xrayline)
            builder.add_column(name, abbrev, q.n, '1/(sr.electron)')
            builder.add_column(name, abbrev, q.s, '1/(sr.electron)', error=True)

class EmittedPhotonIntensityResultSeriesHandler(PhotonIntensityResultSeriesHandlerBase):

    @property
    def CLASS(self):
        return EmittedPhotonIntensityResult

class GeneratedPhotonIntensityResultSeriesHandler(PhotonIntensityResultSeriesHandlerBase):

    @property
    def CLASS(self):
        return GeneratedPhotonIntensityResult
