""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.document.handler import DocumentHandlerBase
from pymontecarlo.options.options import Options
from pymontecarlo.util.cbook import organize_by_type
from pymontecarlo.util.human import camelcase_to_words

# Globals and constants variables.

class OptionsDocumentHandler(DocumentHandlerBase):

    def convert(self, options, builder):
        super().convert(options, builder)

        builder.add_title('Program')
        section = builder.add_section()
        section.add_object(options.program)

        builder.add_title('Beam')
        section = builder.add_section()
        section.add_object(options.beam)

        builder.add_title('Sample')
        section = builder.add_section()
        section.add_object(options.sample)

        builder.add_title('Detector' if len(options.detectors) < 2 else 'Detectors')
        for clasz, detectors in organize_by_type(options.detectors).items():
            section = builder.add_section()
            section.add_title(camelcase_to_words(clasz.__name__))

            for detector in detectors:
                section.add_object(detector)

        builder.add_title('Analysis' if len(options.analyses) < 2 else 'Analyses')
        for analysis in options.analyses:
            section = builder.add_section()
            section.add_object(analysis)

    @property
    def CLASS(self):
        return Options
