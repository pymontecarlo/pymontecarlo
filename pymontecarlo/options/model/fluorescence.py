"""
Fluorescence models.
"""

__all__ = ["FluorescenceModel"]

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.model.base import ModelBase

# Globals and constants variables.


class FluorescenceModel(ModelBase):

    NONE = "no fluorescence"
    FLUORESCENCE = "fluorescence"
    FLUORESCENCE_COMPTON = "fluorescence with Compton"
