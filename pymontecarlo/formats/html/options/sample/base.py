""""""

# Standard library modules.
from collections import OrderedDict

# Third party modules.
import dominate.tags as tags

# Local modules.
from pymontecarlo.formats.html.base import HtmlHandler, TableHtmlHandler
from pymontecarlo.options.sample.base import Sample, Layer

# Globals and constants variables.

class SampleHtmlHandler(HtmlHandler):

    def convert(self, sample, level=1):
        root = super().convert(sample, level=1)

        root += self._create_header(level, 'Angles')
        dl = tags.dl()
        dl += self._create_description('Tilt', sample.tilt_rad, 'rad', Sample.TILT_TOLERANCE_rad)
        dl += self._create_description('Azimuth', sample.azimuth_rad, 'rad', Sample.AZIMUTH_TOLERANCE_rad)
        root += dl

        root += self._create_header(level, 'Material(s)')
        root += self._create_table_objects(sample.materials)

        return root

class LayerHtmlHandler(TableHtmlHandler):

    def convert_rows(self, layer):
        row = OrderedDict()

        key = self._create_label('Material')
        value = self._format_value(layer.material.name)
        row[key] = value

        key = self._create_label('Thickness', 'm')
        value = self._format_value(layer.thickness_m, 'm', Layer.THICKNESS_TOLERANCE_m)
        row[key] = value

        rows = super().convert_rows(layer)
        rows.append(row)
        return rows

    @property
    def CLASS(self):
        return Layer

class LayeredSampleHtmlHandler(SampleHtmlHandler):

    def convert(self, sample, level=1):
        root = super().convert(sample, level=1)

        root += self._create_header(level, 'Layer(s)')
        root += self._create_table_objects(sample.layers)

        return root
