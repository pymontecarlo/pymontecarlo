"""
Direction cosine models.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.model.base import Model

# Globals and constants variables.

class DirectionCosineModel(Model):

    @property
    def category(self):
        return 'direction cosine'

SOUM1979 = DirectionCosineModel('Soum et al.', 'Soum et al. (1979)')
DROUIN1996 = DirectionCosineModel('Drouin', 'Drouin (1996)')
DEMERS2000 = DirectionCosineModel('Demers - Matrices rotation', 'Demers (2000)')
LOWNEY1994 = DirectionCosineModel('Lowney (1994)',)