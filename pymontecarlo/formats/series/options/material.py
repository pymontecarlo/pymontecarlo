""""""

# Standard library modules.

# Third party modules.
import pyxray

# Local modules.
from pymontecarlo.formats.series.handler import SeriesHandler
from pymontecarlo.options.material import Material, VACUUM

# Globals and constants variables.

class MaterialSeriesHandler(SeriesHandler):

    def create_builder(self, material):
        builder = super().create_builder(material)

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

    def create_builder(self, vacuum):
        return super().create_builder(vacuum)

    @property
    def CLASS(self):
        return type(VACUUM)
