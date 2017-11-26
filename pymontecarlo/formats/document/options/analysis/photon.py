""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.document.options.analysis.base import AnalysisDocumentHandler

# Globals and constants variables.

class PhotonAnalysisDocumentHandler(AnalysisDocumentHandler):

    def convert(self, analysis, builder):
        super().convert(analysis, builder)

        description = builder.require_description('detector')
        description.add_item('Detector', analysis.photon_detector.name)