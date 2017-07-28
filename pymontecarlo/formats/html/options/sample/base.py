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

    def convert(self, sample, settings, level=1):
        root = super().convert(sample, settings, level)

        root += self._create_header(level, 'Angles')
        dl = tags.dl()
        dl += self._create_description(settings, 'Tilt', sample.tilt_rad, 'rad', Sample.TILT_TOLERANCE_rad)
        dl += self._create_description(settings, 'Azimuth', sample.azimuth_rad, 'rad', Sample.AZIMUTH_TOLERANCE_rad)
        root += dl

        root += self._create_header(level, 'Material(s)')
        root += self._create_table_objects(sample.materials, settings)

        return root

class LayerHtmlHandler(TableHtmlHandler):

    def convert_rows(self, layer, settings):
        row = OrderedDict()

        key = self._create_label(settings, 'Material')
        value = self._format_value(settings, layer.material.name)
        row[key] = value

        key = self._create_label(settings, 'Thickness', 'm')
        value = self._format_value(settings, layer.thickness_m, 'm', Layer.THICKNESS_TOLERANCE_m)
        row[key] = value

        rows = super().convert_rows(layer, settings)
        rows.append(row)
        return rows

    @property
    def CLASS(self):
        return Layer

class LayeredSampleHtmlHandler(SampleHtmlHandler):

    def convert(self, sample, settings, level=1):
        root = super().convert(sample, settings, level)

        root += self._create_header(level, 'Layer(s)')
        root += self._create_table_objects(sample.layers, settings)

        return root
