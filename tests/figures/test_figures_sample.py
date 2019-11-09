#!/usr/bin/env python3

# Standard library modules.

# Third party modules.
import pytest

import matplotlib.pyplot as plt

# Local modules.
from pymontecarlo.figures.sample import SampleFigure, Perspective
from pymontecarlo.options.beam import GaussianBeam, CylindricalBeam, PencilBeam
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import (
    SubstrateSample,
    InclusionSample,
    HorizontalLayerSample,
    VerticalLayerSample,
    SphereSample,
)
from pymontecarlo.options.sample.base import Layer


@pytest.fixture
def ax():
    fig, ax = plt.subplots(1, 1)

    yield ax

    plt.close()
    del fig


@pytest.fixture
def samplefigure():
    return SampleFigure()


MATERIAL_DS = Material("Ds", {110: 1.0}, 1.0)
MATERIAL_RG = Material("Rg", {111: 1.0}, 1.0)
MATERIAL_AU = Material("Au", {79: 1.0}, 1.0)

LAYERS = [
    Layer(MATERIAL_DS, 0.1),
    Layer(MATERIAL_RG, 0.15),
    Layer(MATERIAL_AU, 0.2),
    Layer(MATERIAL_DS, 0.05),
]


def test_samplefigure_draw_nothing(samplefigure, ax):
    samplefigure.draw(ax)
    assert len(ax.collections) == 0


@pytest.mark.parametrize(
    "sample,perspective,expected_path_count",
    [
        (SubstrateSample(MATERIAL_DS), Perspective.XY, 1),
        (SubstrateSample(MATERIAL_DS), Perspective.XZ, 1),
        (SubstrateSample(MATERIAL_DS), Perspective.YZ, 1),
        (InclusionSample(MATERIAL_DS, MATERIAL_RG, 0.5), Perspective.XY, 2),
        (InclusionSample(MATERIAL_DS, MATERIAL_RG, 0.5), Perspective.XZ, 2),
        (InclusionSample(MATERIAL_DS, MATERIAL_RG, 0.5), Perspective.YZ, 2),
        (HorizontalLayerSample(MATERIAL_DS, LAYERS), Perspective.XY, 1),
        (HorizontalLayerSample(MATERIAL_DS, LAYERS), Perspective.XZ, 5),
        (HorizontalLayerSample(MATERIAL_DS, LAYERS), Perspective.YZ, 5),
        (VerticalLayerSample(MATERIAL_DS, MATERIAL_AU, LAYERS), Perspective.XY, 6),
        (VerticalLayerSample(MATERIAL_DS, MATERIAL_AU, LAYERS), Perspective.XZ, 6),
        (VerticalLayerSample(MATERIAL_DS, MATERIAL_AU, LAYERS), Perspective.YZ, 1),
        (SphereSample(MATERIAL_DS, 0.5), Perspective.XY, 1),
        (SphereSample(MATERIAL_DS, 0.5), Perspective.XZ, 1),
        (SphereSample(MATERIAL_DS, 0.5), Perspective.YZ, 1),
    ],
)
def test_samplefigure_draw_sample(
    samplefigure, ax, sample, perspective, expected_path_count
):
    samplefigure.sample = sample
    samplefigure.perspective = perspective

    samplefigure.draw(ax)

    assert len(ax.collections) == 1
    assert len(ax.collections[0]._paths) == expected_path_count


@pytest.mark.parametrize(
    "beam,perspective,expected_path_count",
    [
        (GaussianBeam(1, 1), Perspective.XY, 1),
        (GaussianBeam(1, 1), Perspective.XZ, 1),
        (GaussianBeam(1, 1), Perspective.YZ, 1),
        (CylindricalBeam(1, 1), Perspective.XY, 1),
        (CylindricalBeam(1, 1), Perspective.XZ, 1),
        (CylindricalBeam(1, 1), Perspective.YZ, 1),
        (PencilBeam(1), Perspective.XY, 1),
        (PencilBeam(1), Perspective.XZ, 1),
        (PencilBeam(1), Perspective.YZ, 1),
    ],
)
def test_samplefigure_draw_beam(
    samplefigure, ax, beam, perspective, expected_path_count
):
    samplefigure.beams.append(beam)
    samplefigure.perspective = perspective

    samplefigure.draw(ax)

    assert len(ax.collections) == 1
    assert len(ax.collections[0]._paths) == expected_path_count


# def test_compose_beam_gaussian(self):
#    beam = GaussianBeam(energy_eV=1, diameter_m=1)
#    sf = SampleFigure(None, [beam], [])
#
#    for perspective in self.perspectives:
#        c = sf._compose_beam_gaussian(beam, perspective, 2.0)
#        self.assertEqual(len(c), 1)
