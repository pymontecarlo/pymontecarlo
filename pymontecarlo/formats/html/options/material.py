""""""

# Standard library modules.
from collections import OrderedDict

# Third party modules.
import pyxray

import dominate.tags as tags

import matplotlib.colors

# Local modules.
from pymontecarlo.formats.html.base import TableHtmlHandler
from pymontecarlo.options.material import Material, VACUUM

# Globals and constants variables.

class MaterialHtmlHandler(TableHtmlHandler):

    def convert_rows(self, material, settings):
        row = OrderedDict()

        key = self._create_label(settings, 'Name')
        value = self._format_value(settings, material.name)
        row[key] = value

        key = self._create_label(settings, 'Color')
        color = matplotlib.colors.to_hex(material.color)
        value = tags.span(color, style='color: ' + color)
        row[key] = value

        key = self._create_label(settings, 'Density', 'kg/m^3')
        value = self._format_value(settings, material.density_kg_per_m3, 'kg/m^3', Material.DENSITY_TOLERANCE_kg_per_m3)
        row[key] = value

        for z, wf in sorted(material.composition.items()):
            key = self._create_label(settings, pyxray.element_symbol(z))
            value = self._format_value(settings, wf, tolerance=Material.WEIGHT_FRACTION_TOLERANCE)
            row[key] = value

        rows = super().convert_rows(material, settings)
        rows.append(row)
        return rows

    @property
    def CLASS(self):
        return Material

class VacuumHtmlHandler(MaterialHtmlHandler):

    @property
    def CLASS(self):
        return type(VACUUM)