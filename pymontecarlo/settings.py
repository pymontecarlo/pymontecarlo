"""
Settings for pymontecarlo
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.fileformat.mixin import ReadWriteMixin

# Globals and constants variables.

class Settings(ReadWriteMixin):

    def __init__(self, programs=None):
        if programs is None:
            programs = []
        self.programs = programs

