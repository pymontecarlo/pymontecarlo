""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.base import SeriesHandler
from pymontecarlo.options.sample.base import Sample, Layer

# Globals and constants variables.

class SampleSeriesHandler(SeriesHandler):

    def convert(self, sample):
        s = super().convert(sample)

        column = self._create_column('sample tilt', 'theta0', 'rad', Sample.TILT_TOLERANCE_rad)
        s[column] = sample.tilt_rad

        column = self._create_column('sample azimuth', 'phi0', 'rad', Sample.AZIMUTH_TOLERANCE_rad)
        s[column] = sample.azimuth_rad

        return s

class LayerSeriesHandler(SeriesHandler):

    def convert(self, layer):
        s = super().convert(layer)

        s_material = self._convert_serieshandlers(layer.material)
        s = s.append(s_material)

        column = self._create_column('thickness', 't', 'm', Layer.THICKNESS_TOLERANCE_m)
        s[column] = layer.thickness_m

        return s

    @property
    def CLASS(self):
        return Layer

class LayeredSampleHandler(SampleSeriesHandler):

    def convert(self, sample):
        s = super().convert(sample)

        for i, layer in enumerate(sample.layers):
            prefix = "layer #{0:d} ".format(i)
            prefix_abbrev = "L#{0:d} ".format(i)

            s_layer = self._convert_serieshandlers(layer)
            s_layer = self._update_with_prefix(s_layer, prefix, prefix_abbrev)
            s = s.append(s_layer)

        return s



