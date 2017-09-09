""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.document.options.sample.base import SampleDocumentHandler
from pymontecarlo.options.sample.sphere import SphereSample

# Globals and constants variables.

class SphereSampleDocumentHandler(SampleDocumentHandler):

    def convert(self, sample, builder):
        super().convert(sample, builder)

        section = builder.add_section()
        section.add_title('Sphere')
        description = section.require_description('sphere')
        description.add_item('Material', sample.material.name)
        description.add_item('Diameter', sample.diameter_m, 'm', SphereSample.DIAMETER_TOLERANCE_m)

    @property
    def CLASS(self):
        return SphereSample
