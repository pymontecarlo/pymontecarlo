""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.handler import SeriesHandler
from pymontecarlo.options.sample.base import Sample, Layer

# Globals and constants variables.

class SampleSeriesHandler(SeriesHandler):

    def _convert(self, sample):
        builder = super()._convert(sample)
        builder.add_column('sample tilt', 'theta0', sample.tilt_rad, 'rad', Sample.TILT_TOLERANCE_rad)
        builder.add_column('sample azimuth', 'phi0', sample.azimuth_rad, 'rad', Sample.AZIMUTH_TOLERANCE_rad)
        return builder

class LayerSeriesHandler(SeriesHandler):

    def _convert(self, layer):
        builder = super()._convert(layer)
        builder.add_object(layer.material)
        builder.add_column('thickness', 't', layer.thickness_m, 'm', Layer.THICKNESS_TOLERANCE_m)
        return builder

    @property
    def CLASS(self):
        return Layer

class LayeredSampleHandler(SampleSeriesHandler):

    def _convert(self, sample):
        builder = super()._convert(sample)

        for i, layer in enumerate(sample.layers):
            prefix = "layer #{0:d} ".format(i)
            prefix_abbrev = "L{0:d} ".format(i)
            builder.add_object(layer, prefix, prefix_abbrev)

        return builder



