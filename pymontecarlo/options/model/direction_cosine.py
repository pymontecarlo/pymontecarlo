"""
Direction cosine models.
"""

__all__ = ["DirectionCosineModel"]

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.model.base import ModelBase

# Globals and constants variables.


class DirectionCosineModel(ModelBase):

    SOUM1979 = ("Soum et al.", "Soum et al. (1979)")
    DROUIN1996 = ("Drouin", "Drouin (1996)")
    DEMERS2000 = ("Demers - Matrices rotation", "Demers (2000)")
    LOWNEY1994 = ("Lowney (1994)",)
