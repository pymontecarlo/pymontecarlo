""""""

# Standard library modules.
from collections import OrderedDict

# Third party modules.
import pyxray

# Local modules.
from pymontecarlo.formats.html.options.analysis.photon import PhotonAnalysisHtmlHandler
from pymontecarlo.options.analysis.kratio import KRatioAnalysis

# Globals and constants variables.

class KRatioAnalysisHtmlHandler(PhotonAnalysisHtmlHandler):

    def convert(self, analysis, level=1):
        root = super().convert(analysis, level)

        root += self._create_header(level, 'Standards')

        rows = []
        for z, material in analysis.standard_materials.items():
            row = OrderedDict()

            key = self._create_label('Element')
            value = self._format_value(pyxray.element_symbol(z))
            row[key] = value

            key = self._create_label('Material')
            value = self._format_value(material.name)
            row[key] = value

            rows.append(row)

        root += self._create_table(rows)

        return root

    @property
    def CLASS(self):
        return KRatioAnalysis
