""""""

# Standard library modules.

# Third party modules.
import pyxray

# Local modules.
from pymontecarlo.formats.document.options.analysis.photon import PhotonAnalysisDocumentHandlerBase
from pymontecarlo.options.analysis.kratio import KRatioAnalysis

# Globals and constants variables.

class KRatioAnalysisDocumentHandler(PhotonAnalysisDocumentHandlerBase):

    def convert(self, analysis, builder):
        super().convert(analysis, builder)

        # Standards
        section = builder.add_section()
        section.add_title('Standards')

        if analysis.standard_materials:
            table = section.require_table('standards')

            table.add_column('Element')
            table.add_column('Material')

            for z, material in analysis.standard_materials.items():
                row = {'Element': pyxray.element_symbol(z),
                       'Material': material.name}
                table.add_row(row)

            section = builder.add_section()
            section.add_title('Materials')

            for material in analysis.standard_materials.values():
                section.add_object(material)

        else:
            section.add_text('No standard defined')

    @property
    def CLASS(self):
        return KRatioAnalysis
