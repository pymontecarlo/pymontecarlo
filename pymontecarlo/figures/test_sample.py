#!/usr/bin/env python3

# Standard library modules.
import unittest
import logging

# Third party modules.
from matplotlib import figure

# Local modules.
from pymontecarlo.figures.sample import SampleFigure, Perspective
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import \
    (SubstrateSample, InclusionSample, HorizontalLayerSample,
     VerticalLayerSample, SphereSample)
from pymontecarlo.options.sample.base import Layer

class TestSampleFigure(unittest.TestCase):

    def setUp(self):

        # test data
        self.perspectives = (Perspective.XZ, Perspective.YZ, Perspective.XY)

        self.mat_ds = Material('Ds', {110: 1.}, 1.)
        self.mat_rg = Material('Rg', {111: 1.}, 1.)
        self.mat_au = Material('Au', {79: 1.}, 1.)

        self.layer = [Layer(Material('Re', {75: 1.}, 1.), .1),
                      Layer(Material('Os', {76: 1.}, 1.), .15),
                      Layer(Material('Ir', {77: 1.}, 1.), .2),
                      Layer(Material('Pt', {78: 1.}, 1.), .05)]

        # matplotlib
        self.figure = figure.Figure()
        self.ax = self.figure.add_subplot(111)

    # DRAW TEST
    def test_draw_nothing(self):
        sf = SampleFigure()
        sf.draw(self.ax)
        self.assertEqual(len(self.ax.collections), 0)

    # DRAW SAMPLES TEST
    def test_draw_sample(self):
        sample = SubstrateSample(self.mat_ds)
        sf = SampleFigure(sample)

        sf._draw_sample(self.ax, sample, Perspective.XZ, 2.0)
        self.assertEqual(len(self.ax.collections), 1)

    def _compose_sample(self, sample, patches_counts):
        for perspective, expected in zip(self.perspectives, patches_counts):
            sf = SampleFigure(sample)
            method = sf.sample_draw_methods[sample.__class__]
            patches = method(sample, perspective, 2.0)
            self.assertEqual(expected, len(patches))

    def test_compose_sample_substrate(self):
        sample = SubstrateSample(self.mat_ds)
        self._compose_sample(sample, (1, 1, 1))

    def test_compose_sample_inclusion(self):
        sample = InclusionSample(self.mat_ds, self.mat_au, 0.5)
        self._compose_sample(sample, (2, 2, 2))

    def test_compose_sample_hlayer(self):
        sample = HorizontalLayerSample(self.mat_ds, self.layer)
        self._compose_sample(sample, (5, 5, 1))

    def test_compose_sample_vlayer(self):
        sample = VerticalLayerSample(self.mat_ds, self.mat_rg, self.layer)
        self._compose_sample(sample, (6, 1, 6))

    def test_compose_sample_sphere(self):
        sample = SphereSample(self.mat_au, 0.5)
        self._compose_sample(sample, (1, 1, 1))

    # DRAW BEAMS TEST
    def test_draw_beam(self):
        beam = GaussianBeam(energy_eV=1, diameter_m=1)
        sf = SampleFigure(None, [beam], [])

        sf._draw_beam(self.ax, beam, Perspective.XZ, 2.0)
        self.assertEqual(len(self.ax.collections), 1)

    def test_compose_beam_gaussian(self):
        beam = GaussianBeam(energy_eV=1, diameter_m=1)
        sf = SampleFigure(None, [beam], [])

        for perspective in self.perspectives:
            c = sf._compose_beam_gaussian(beam, perspective, 2.0)
            self.assertEqual(len(c), 1)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
