#!/usr/bin/env python3

# Standard library modules.
import unittest
# import logging

# Third party modules.

# Local modules.
from pymontecarlo.figures.sample import SampleFigure
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import SubstrateSample, InclusionSample, HorizontalLayerSample, \
    VerticalLayerSample, SphereSample
from pymontecarlo.options.sample.base import Layer

# from pymontecarlo.testcase import TestCase
# from pymontecarlo.options.detector import PhotonDetector
# from pymontecarlo.options.detector.base import Detector
# from pymontecarlo.options.limit import ShowersLimit, UncertaintyLimit
# from pymontecarlo.options.model import ElasticCrossSectionModel, EnergyLossModel

from matplotlib import figure

class TestSampleFigure(unittest.TestCase):

    def setUp(self):

        # test data
        self.perspectives = ('XZ', 'YZ', 'XY')

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

    def tearDown(self):
        del self.perspectives
        del self.mat_ds
        del self.mat_rg
        del self.mat_au
        del self.layer

        del self.figure
        del self.ax

    def test_get_color(self):
        # TODO implement test_get_color
        raise NotImplementedError

    def test_get_material_color(self):
        # TODO implement test_get_material
        raise NotImplementedError

    # DRAW TEST
    def test_draw(self):
        sf = SampleFigure(None, [], [])
        self.assertRaises(TypeError, sf.draw, ax=None)

    # DRAW SAMPLES TEST
    def test_draw_sample(self):
        sample = SubstrateSample(self.mat_ds)
        sf = SampleFigure(sample, [], [])

        sf._draw_sample(self.ax, sample)
        self.assertEqual(len(self.ax.collections), 1)

    def _compose_sample(self, sample, len_):
        for p, l in zip(self.perspectives, len_):
            sf = SampleFigure(sample, [], [])
            c = sf.sample_draw_methods[sample.__class__](sample, p)
            self.assertEqual(len(c), l, msg='perspective: {}'.format(p))

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

        sf._draw_beam(self.ax, beam)
        self.assertEqual(len(self.ax.collections), 1)

    def test_compose_beam_gaussian(self):
        beam = GaussianBeam(energy_eV=1, diameter_m=1)
        sf = SampleFigure(None, [beam], [])

        for p in self.perspectives:
            c = sf._compose_beam_gaussian(beam=beam, perspective=p)
            self.assertEqual(len(c), 1)

    # DRAW TRAJECTORIES TEST
    def test_draw_trajectory(self):
        # TODO implement test_draw_trajectory
        raise NotImplementedError