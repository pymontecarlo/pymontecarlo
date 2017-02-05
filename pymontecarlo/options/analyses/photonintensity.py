""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.analyses.base import Analysis

# Globals and constants variables.

class PhotonIntensityAnalysis(Analysis):

    def __eq__(self, other):
        return super().__eq__(other)

    def apply(self, options):
        return []

    def calculate(self, simulations):
        pass
