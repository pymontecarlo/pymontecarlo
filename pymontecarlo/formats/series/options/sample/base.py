""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.handler import SeriesHandlerBase
from pymontecarlo.options.sample.base import SampleBase, Layer

# Globals and constants variables.

class SampleSeriesHandlerBase(SeriesHandlerBase):

    def convert(self, sample, builder):
        super().convert(sample, builder)
        builder.add_column('sample tilt', 'theta0', sample.tilt_rad, 'rad', SampleBase.TILT_TOLERANCE_rad)
        builder.add_column('sample azimuth', 'phi0', sample.azimuth_rad, 'rad', SampleBase.AZIMUTH_TOLERANCE_rad)

class LayerSeriesHandler(SeriesHandlerBase):

    def convert(self, layer, builder):
        super().convert(layer, builder)
        builder.add_object(layer.material)
        builder.add_column('thickness', 't', layer.thickness_m, 'm', Layer.THICKNESS_TOLERANCE_m)

    @property
    def CLASS(self):
        return Layer

class LayeredSampleHandlerBase(SampleSeriesHandlerBase):

    def convert(self, sample, builder):
        super().convert(sample, builder)

        for i, layer in enumerate(sample.layers):
            prefix = "layer #{0:d} ".format(i)
            prefix_abbrev = "L{0:d} ".format(i)
            builder.add_object(layer, prefix, prefix_abbrev)
