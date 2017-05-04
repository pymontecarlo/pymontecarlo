#!/usr/bin/env python3

"""
Figure to draw a sample.
"""

# Standard library modules.
from math import tan
import enum

# Third party modules.
from matplotlib.collections import PatchCollection
from matplotlib.patches import Wedge, Rectangle, Circle
from matplotlib.transforms import Affine2D

# Local modules.
from pymontecarlo.figures.base import Figure
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.sample import SubstrateSample, InclusionSample, HorizontalLayerSample, \
    VerticalLayerSample, SphereSample

# Globals and constant variables.

@enum.unique
class Perspective(enum.Enum):
    XZ = 'xz'
    YZ = 'yz'
    XY = 'xy'

class SampleFigure(Figure):

    def __init__(self, sample=None, beams=None, trajectories=None):
        """
        :param sample: an instance of Sample(Option)
        :param beams: a list of instances of Beam(Option)
        :param trajectories: a list of instances of Trajectory
        """
        super().__init__()

        self.sample = sample

        if not beams:
            beams = []
        self.beams = beams

        if not trajectories:
            trajectories = []
        self.trajectories = trajectories

        self.perspective = Perspective.XZ

        self.sample_draw_methods = {}
        self.sample_draw_methods[SubstrateSample] = self._compose_sample_substrate
        self.sample_draw_methods[InclusionSample] = self._compose_sample_inclusion
        self.sample_draw_methods[HorizontalLayerSample] = self._compose_sample_hlayer
        self.sample_draw_methods[VerticalLayerSample] = self._compose_sample_vlayer
        self.sample_draw_methods[SphereSample] = self._compose_sample_sphere

        self.beam_draw_methods = {}
        self.beam_draw_methods[GaussianBeam] = self._compose_beam_gaussian

        self.view_size_methods = {}
        self.view_size_methods[InclusionSample] = self._calculate_view_size_inclusion_sample
        self.view_size_methods[HorizontalLayerSample] = self._calculate_view_size_layered_sample
        self.view_size_methods[VerticalLayerSample] = self._calculate_view_size_layered_sample
        self.view_size_methods[SphereSample] = self._calculate_view_size_sphere_sample
        self.view_size_methods[GaussianBeam] = self._calculate_view_size_gaussian_beam

    def _recalculate_view_size(self, perspective):
        SCALE_FACTOR = 5
        view_size = 1e-9

        for obj in [self.sample] + self.beams + self.trajectories:
            clasz = obj.__class__
            if clasz not in self.view_size_methods:
                continue

            method = self.view_size_methods[clasz]
            view_size = max(view_size, method(obj, perspective) * SCALE_FACTOR)

        return view_size

    def _calculate_view_size_inclusion_sample(self, sample, perspective):
        return sample.inclusion_diameter_m

    def _calculate_view_size_layered_sample(self, sample, perspective):
        return sum([l.thickness_m for l in sample.layers])

    def _calculate_view_size_sphere_sample(self, sample, perspective):
        return sample.diameter_m

    def _calculate_view_size_gaussian_beam(self, beam, perspective):
        view_size = beam.diameter_m * 2

        if perspective is Perspective.XY:
            return view_size + max(beam.x0_m, beam.y0_m)
        elif perspective is Perspective.XZ:
            return view_size + beam.x0_m
        elif perspective is Perspective.YZ:
            return view_size + beam.y0_m

    def draw(self, ax):
        """
        :param ax: an instance of matplotlib.axes.Axes
        """
        view_size = self._recalculate_view_size(self.perspective)

        if self.sample:
            self._draw_sample(ax, self.sample, self.perspective, view_size)

        for beam in self.beams:
            self._draw_beam(ax, beam, self.perspective, view_size)

        for trajectory in self.trajectories:
            self._draw_trajectory(ax, trajectory, self.perspective, view_size)

        half_view_size = view_size / 2
        ax.set_xlim((-half_view_size, half_view_size))
        ax.set_ylim((-half_view_size, half_view_size))
        ax.set_aspect('equal')

    # DRAW SAMPLES
    def _draw_sample(self, ax, sample, perspective, view_size):
        sample_class = sample.__class__

        if sample_class not in self.sample_draw_methods:
            return

        method = self.sample_draw_methods[sample_class]

        patches = method(sample, perspective, view_size)
        col = PatchCollection(patches, match_original=True)

        if perspective is Perspective.YZ:
            trans = Affine2D().rotate_around(0, 0, sample.tilt_rad)
        else:
            trans = Affine2D().scale(sx=1, sy=1 + tan(abs(sample.tilt_rad)))

        trans += ax.transData
        col.set_transform(trans)

        ax.add_collection(col)

    def _compose_substrate(self, material, perspective, view_size):
        half_view_size = view_size / 2
        color = material.color

        if perspective is Perspective.XY:
            return [Rectangle((-half_view_size, half_view_size),
                              view_size, -view_size,
                              color=color)]
        else:
            return [Rectangle((-half_view_size, 0), view_size, -half_view_size,
                              color=color)]

    def _compose_sample_substrate(self, sample, perspective, view_size):
        return self._compose_substrate(sample.material, perspective, view_size)

    def _compose_sample_inclusion(self, sample, perspective, view_size):
        patches = []

        patches += self._compose_substrate(sample.substrate_material,
                                           perspective, view_size)

        diameter_m = sample.inclusion_diameter_m
        color = sample.inclusion_material.color

        if perspective is Perspective.XY:
            patches.append(Circle((0, 0), diameter_m, color=color))
        else:
            patches.append(Wedge((0, 0), diameter_m, 180, 0, color=color))

        return patches

    def _compose_sample_hlayer(self, sample, perspective, view_size):
        patches = []

        half_view_size = view_size / 2

        if perspective is Perspective.XY:
            if len(sample.layers) > 0:
                patches.append(Rectangle((-half_view_size, half_view_size),
                                         view_size, -view_size,
                                         color=sample.layers[0].material.color))

        else:
            patches += self._compose_substrate(sample.substrate_material,
                                               perspective, view_size)

            depth_m = 0

            for layer in sample.layers:
                patches.append(Rectangle((-half_view_size, depth_m),
                                         view_size, -layer.thickness_m,
                                         color=layer.material.color))
                depth_m -= layer.thickness_m

        return patches

    def _compose_sample_vlayer(self, sample, perspective, view_size):
        patches = []

        half_view_size = view_size / 2

        if perspective is Perspective.XZ:
            patches.append(Rectangle((0, 0), -half_view_size, -half_view_size,
                                     color=sample.left_material.color))
            patches.append(Rectangle((0, 0), half_view_size, -half_view_size,
                                     color=sample.right_material.color))

            for layer, pos in zip(sample.layers, sample.layers_xpositions_m):
                patches.append(Rectangle((pos[0], 0), layer.thickness_m, -half_view_size,
                                         color=layer.material.color))

        elif perspective is Perspective.YZ:
            for layer, pos in zip(sample.layers, sample.layers_xpositions_m):
                if pos[1] >= 0.0:
                    patches.append(Rectangle((-half_view_size, 0),
                                             view_size, -half_view_size,
                                             color=layer.material.color))
                    break

            if len(patches) == 0:
                patches.append(Rectangle((half_view_size, 0),
                                         view_size, -half_view_size,
                                         color=sample.left_material.color))

        elif perspective is Perspective.XY:
            patches.append(Rectangle((0, half_view_size),
                                     - half_view_size, -view_size,
                                     color=sample.left_material.color))
            patches.append(Rectangle((0, half_view_size),
                                     half_view_size, -view_size,
                                     color=sample.right_material.color))

            for layer, pos in zip(sample.layers, sample.layers_xpositions_m):
                patches.append(Rectangle((pos[0], half_view_size),
                                         layer.thickness_m, -view_size,
                                         color=layer.material.color))

        return patches

    def _compose_sample_sphere(self, sample, perspective, view_size):
        radius_m = sample.diameter_m / 2
        color = sample.material.color

        if perspective is Perspective.XY:
            return [Circle((0, 0), radius_m, color=color)]
        else:
            return [Circle((0, -radius_m), radius_m, color=color)]

    # DRAW BEAMS
    def _draw_beam(self, ax, beam, perspective, view_size):
        beam_class = beam.__class__
        if beam_class not in self.beam_draw_methods:
            return

        method = self.beam_draw_methods[beam_class]

        patches = method(beam, perspective, view_size)
        col = PatchCollection(patches, match_original=True)

        # TODO rotate
        if perspective is Perspective.XZ:
            pass
        elif perspective is Perspective.YZ:
            pass
        elif perspective is Perspective.XY:
            pass

        ax.add_collection(col)

    def _compose_beam_gaussian(self, beam, perspective, view_size):
        x0_m = beam.x0_m
        y0_m = beam.y0_m
        radius_m = beam.diameter_m / 2
        color = beam.particle.color

        if perspective is Perspective.XY:
            return [Circle((x0_m, y0_m), radius=radius_m, color=color)]
        elif perspective is Perspective.XZ:
            return [Rectangle((-radius_m - x0_m, 0),
                              beam.diameter_m, (view_size / 2) * 1.5,
                              color=color)]
        elif perspective is Perspective.YZ:
            return [Rectangle((-radius_m - y0_m, 0),
                              beam.diameter_m, (view_size / 2) * 1.5,
                              color=color)]

    # DRAW TRAJECTORIES
    def _draw_trajectory(self, ax, trajectory, perspective):
        raise NotImplementedError
