""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.document.options.sample.base import SampleDocumentHandlerBase
from pymontecarlo.options.sample.inclusion import InclusionSample

# Globals and constants variables.

class InclusionSampleDocumentHandler(SampleDocumentHandlerBase):

    def convert(self, sample, builder):
        super().convert(sample, builder)

        section = builder.add_section()
        section.add_title('Substrate')
        description = section.require_description('substrate')
        description.add_item('Material', sample.substrate_material.name)

        section = builder.add_section()
        section.add_title('Inclusion')
        description = section.require_description('inclusion')
        description.add_item('Material', sample.inclusion_material.name)
        description.add_item('Diameter', sample.inclusion_diameter_m, 'm', InclusionSample.INCLUSION_DIAMETER_TOLERANCE_m)

    @property
    def CLASS(self):
        return InclusionSample
