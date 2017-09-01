""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.model.base import ModelSeriesHandler
from pymontecarlo.formats.series.base import NamedSeriesColumn
from pymontecarlo.options.model.photon_scattering_cross_section import PhotonScatteringCrossSectionModel

# Globals and constants variables.

class PhotonScatteringCrossSectionModelSeriesHandler(ModelSeriesHandler):

    def convert(self, model):
        s = super().convert(model)

        column = NamedSeriesColumn('photon scattering cross-section', 'ph. scatter')
        s[column] = model.name

        return s

    @property
    def CLASS(self):
        return PhotonScatteringCrossSectionModel