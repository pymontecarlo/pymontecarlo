""""""

# Standard library modules.

# Third party modules.
import pyxray

# Local modules.
from pymontecarlo.formats.series.base import SeriesHandler, NamedSeriesColumn
from pymontecarlo.options.material import Material, VACUUM

# Globals and constants variables.

class MaterialSeriesHandler(SeriesHandler):

    def convert(self, material):
        s = super().convert(material)

        for z, wf in material.composition.items():
            symbol = pyxray.element_symbol(z)
            name = '{} weight fraction'.format(symbol)
            abbrev = 'wt{}'.format(symbol)
            tolerance = Material.WEIGHT_FRACTION_TOLERANCE
            column = NamedSeriesColumn(name, abbrev, tolerance=tolerance)
            s[column] = wf

        column = NamedSeriesColumn('density', 'rho', 'kg/m^3', Material.DENSITY_TOLERANCE_kg_per_m3)
        s[column] = material.density_kg_per_m3

        return s

    @property
    def CLASS(self):
        return Material

class VacuumSeriesHandler(SeriesHandler):

    def convert(self, vacuum):
        return super().convert(vacuum)

    @property
    def CLASS(self):
        return type(VACUUM)
