"""
Base detector.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.util.cbook import Builder

# Globals and constants variables.

class Detector(object):

    def __eq__(self, other):
        return True

class DetectorBuilder(Builder):
    pass