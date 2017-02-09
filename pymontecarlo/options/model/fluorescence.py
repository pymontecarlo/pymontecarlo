"""
Fluorescence models.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.model.base import Model

# Globals and constants variables.

class FluorescenceModel(Model):

    NAME = 'fluorescence model'
    DESCRIPTION = 'Models X-ray fluorescence and/or Compton scattering.'

    @property
    def category(self):
        return 'fluorescence'

NONE = FluorescenceModel('no fluorescence')
FLUORESCENCE = FluorescenceModel('fluorescence')
FLUORESCENCE_COMPTON = FluorescenceModel('fluorescence with Compton')
