"""
Figure to draw a sample.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.figures.base import Figure
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.sample import SubstrateSample

# Globals and constants variables.

class SampleFigure(Figure):

    def __init__(self):
        super().__init__()

        self.sample = None
        self.beams = []
        self.trajectories = []

        self.sample_draw_methods = {}
        self.sample_draw_methods[SubstrateSample] = self._draw_sample_substrate

        self.beam_draw_methods = {}
        self.beam_draw_methods[GaussianBeam] = self._draw_beam_gaussian

    def draw(self, ax):
        if self.sample:
            self._draw_sample(ax, self.sample)

        for beam in self.beams:
            self._draw_beam(ax, beam)

    def _draw_sample(self, ax, sample):
        sample_class = sample.__class__
        if sample_class not in self.sample_draw_methods:
            return

        method = self.sample_draw_methods[sample_class]
        method(ax, sample)

    def _draw_sample_substrate(self, ax, sample):
        pass

    def _draw_beam(self, ax, beam):
        beam_class = beam.__class__
        if beam_class not in self.beam_draw_methods:
            return

        method = self.sample_draw_methods[beam_class]
        method(ax, beam)

    def _draw_beam_gaussian(self, ax, beam):
        pass
