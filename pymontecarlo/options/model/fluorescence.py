"""
Fluorescence models.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.model.base import Model

# Globals and constants variables.

class FluorescenceModel(Model):

    NONE = ('no fluorescence')
    FLUORESCENCE = ('fluorescence')
    FLUORESCENCE_COMPTON = ('fluorescence with Compton')
