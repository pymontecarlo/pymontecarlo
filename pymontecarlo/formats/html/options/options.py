""""""

# Standard library modules.

# Third party modules.
import dominate.tags as tags

# Local modules.
from pymontecarlo.formats.html.base import HtmlHandler
from pymontecarlo.options.options import Options
from pymontecarlo.util.human import camelcase_to_words
from pymontecarlo.util.cbook import organize_by_type

# Globals and constants variables.

class OptionsHtmlHandler(HtmlHandler):

    def convert(self, options, level=1):
        root = super().convert(options, level=1)

        root += self._create_header(level, 'Program')
        dl = tags.dl()
        dl += self._create_description('Identifier', options.program.getidentifier())
        root += dl

        classname = camelcase_to_words(options.beam.__class__.__name__)
        root += self._create_header(level, classname)
        root += self._find_and_convert(options.beam, level + 1).children

        classname = camelcase_to_words(options.sample.__class__.__name__)
        root += self._create_header(level, classname)
        root += self._find_and_convert(options.sample, level + 1).children

        root += self._create_header(level, 'Detectors')
        for clasz, detectors in organize_by_type(options.detectors).items():
            classname = camelcase_to_words(clasz.__name__)
            root += self._create_header(level + 1, classname)
            root += self._create_table_objects(detectors)

        root += self._create_header(level, 'Analyses')
        for analysis in options.analyses:
            classname = camelcase_to_words(analysis.__class__.__name__)
            root += self._create_header(level + 1, classname)
            root += self._find_and_convert(analysis, level + 1)

        root += self._create_header(level, 'Limits')
        for limit in options.limits:
            classname = camelcase_to_words(limit.__class__.__name__)
            root += self._create_header(level + 1, classname)
            root += self._find_and_convert(limit, level + 1)

        root += self._create_header(level, 'Models')
        root += self._create_table_objects(options.models)

        return root

    @property
    def CLASS(self):
        return Options
