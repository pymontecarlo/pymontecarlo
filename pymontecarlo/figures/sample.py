"""
Figure to draw a sample.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.figures.base import Figure

# Globals and constants variables.

class SampleFigure(Figure):

    def __init__(self):
        super().__init__()

        self.sample = None
        self.beams = []
        self.trajectories = []

        self.sample_draw_methods = {}
        self.beam_draw_methods = {}

    def draw(self, ax):

        raise NotImplementedError
