""""""

# Standard library modules.

# Third party modules.
import dominate.tags as tags

# Local modules.
from pymontecarlo.formats.html.options.analysis.base import AnalysisHtmlHandler

# Globals and constants variables.

class PhotonAnalysisHtmlHandler(AnalysisHtmlHandler):

    def convert(self, analysis, level=1):
        root = super().convert(analysis, level)

        dl = tags.dl()
        dl += self._create_description('Detector', analysis.photon_detector.name)
        root += dl

        return root
