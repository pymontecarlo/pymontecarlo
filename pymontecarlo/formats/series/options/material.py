""""""

# Standard library modules.

# Third party modules.
import pyxray

# Local modules.
from pymontecarlo.formats.series.handler import SeriesHandlerBase
from pymontecarlo.options.material import Material, VACUUM

# Globals and constants variables.

class MaterialSeriesHandler(SeriesHandlerBase):

    def convert(self, material, builder):
        super().convert(material, builder)

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

class VacuumSeriesHandler(SeriesHandlerBase):

    def convert(self, vacuum, builder):
        return super().convert(vacuum, builder)

    @property
    def CLASS(self):
        return type(VACUUM)
