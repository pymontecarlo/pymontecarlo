""""""

# Standard library modules.

# Third party modules.
import dominate.tags as tags

# Local modules.
from pymontecarlo.formats.html.options.analysis.base import AnalysisHtmlHandler

# Globals and constants variables.

class PhotonAnalysisHtmlHandler(AnalysisHtmlHandler):

    def convert(self, analysis, settings, level=1):
        root = super().convert(analysis, settings, level)

        dl = tags.dl()
        dl += self._create_description(settings, 'Detector', analysis.photon_detector.name)
        root += dl

        return root
