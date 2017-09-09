""""""

# Standard library modules.

# Third party modules.
import pyxray

import matplotlib.colors

# Local modules.
from pymontecarlo.formats.document.handler import DocumentHandler
from pymontecarlo.options.material import Material, VACUUM

# Globals and constants variables.

class MaterialDocumentHandler(DocumentHandler):

    def convert(self, material, builder):
        super().convert(material, builder)

        table = builder.require_table('materials')

        table.add_column('Name')
        table.add_column('Color')
        table.add_column('Density', 'kg/m^3', Material.DENSITY_TOLERANCE_kg_per_m3)
        for z in sorted(material.composition):
            name = pyxray.element_symbol(z)
            table.add_column(name, tolerance=Material.WEIGHT_FRACTION_TOLERANCE)

        row = {'Name': material.name,
               'Color': matplotlib.colors.to_hex(material.color),
               'Density': material.density_kg_per_m3}
        for z, wf in material.composition.items():
            symbol = pyxray.element_symbol(z)
            row[symbol] = wf
        table.add_row(row)

    @property
    def CLASS(self):
        return Material

class VacuumDocumentHandler(MaterialDocumentHandler):

    @property
    def CLASS(self):
        return type(VACUUM)