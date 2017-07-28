""""""

# Standard library modules.

# Third party modules.
import pyxray

# Local modules.
from pymontecarlo.formats.series.base import SeriesHandler, NamedSeriesColumn
from pymontecarlo.options.material import Material, VACUUM

# Globals and constants variables.

class MaterialSeriesHandler(SeriesHandler):

    def convert(self, material, settings):
        s = super().convert(material, settings)

        for z, wf in material.composition.items():
            symbol = pyxray.element_symbol(z)
            name = '{} weight fraction'.format(symbol)
            abbrev = 'wt{}'.format(symbol)
            tolerance = Material.WEIGHT_FRACTION_TOLERANCE
            column = NamedSeriesColumn(settings, name, abbrev, tolerance=tolerance)
            s[column] = wf

        column = NamedSeriesColumn(settings, 'density', 'rho', 'kg/m^3', Material.DENSITY_TOLERANCE_kg_per_m3)
        s[column] = material.density_kg_per_m3

        return s

    @property
    def CLASS(self):
        return Material

class VacuumSeriesHandler(SeriesHandler):

    def convert(self, vacuum, settings):
        return super().convert(vacuum, settings)

    @property
    def CLASS(self):
        return type(VACUUM)
