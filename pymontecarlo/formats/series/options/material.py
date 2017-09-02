""""""

# Standard library modules.

# Third party modules.
import pyxray

# Local modules.
from pymontecarlo.formats.series.base import SeriesHandler
from pymontecarlo.options.material import Material, VACUUM

# Globals and constants variables.

class MaterialSeriesHandler(SeriesHandler):

    def _convert(self, material):
        builder = super()._convert(material)

        for z, wf in material.composition.items():
            symbol = pyxray.element_symbol(z)
            name = '{} weight fraction'.format(symbol)
            abbrev = 'wt{}'.format(symbol)
            tolerance = Material.WEIGHT_FRACTION_TOLERANCE
            builder.add_column(name, abbrev, wf, tolerance=tolerance)

        builder.add_column('density', 'rho', material.density_kg_per_m3, 'kg/m^3', Material.DENSITY_TOLERANCE_kg_per_m3)

        return builder

    @property
    def CLASS(self):
        return Material

class VacuumSeriesHandler(SeriesHandler):

    def _convert(self, vacuum):
        return super()._convert(vacuum)

    @property
    def CLASS(self):
        return type(VACUUM)
