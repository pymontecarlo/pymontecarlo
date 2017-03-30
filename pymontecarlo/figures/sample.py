#!/usr/bin/env python3

"""
Figure to draw a sample.
"""

# Standard library modules.
from math import tan
import enum

# Third party modules.
import matplotlib
matplotlib.use('qt5agg')
from matplotlib.collections import PatchCollection
from matplotlib.patches import Wedge, Rectangle, Circle
from matplotlib.transforms import Affine2D

# Local modules.
from pymontecarlo.figures.base import Figure
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import SubstrateSample, InclusionSample, HorizontalLayerSample, \
    VerticalLayerSample, SphereSample
from pymontecarlo.options.sample.base import Layer

# Globals and constant variables.

@enum.unique
class Perspective(enum.Enum):
    XZ = 'xz'
    XY = 'xy'
    YZ = 'yz'

class SampleFigure(Figure):

    def __init__(self, sample=None, beams=None, trajectories=None):
        """
        :param sample: an instance of Sample(Option)
        :param beams: a list of instances of Beam(Option)
        :param trajectories: a list of instances of Trajectory
        """
        super().__init__()

        self._view_size = 2

        self.sample = sample

        if not beams:
            beams = []
        self.beams = beams

        if not trajectories:
            trajectories = []
        self.trajectories = trajectories

        self.perspective = Perspective.XZ

        self.sample_draw_methods = dict()
        self.sample_draw_methods[SubstrateSample] = self._compose_sample_substrate
        self.sample_draw_methods[InclusionSample] = self._compose_sample_inclusion
        self.sample_draw_methods[HorizontalLayerSample] = self._compose_sample_hlayer
        self.sample_draw_methods[VerticalLayerSample] = self._compose_sample_vlayer
        self.sample_draw_methods[SphereSample] = self._compose_sample_sphere

        self.beam_draw_methods = dict()
        self.beam_draw_methods[GaussianBeam] = self._compose_beam_gaussian

    def _recalc_view_size(self):

        SCALE_FACTOR = 5
        view_size = 0.
        sample_view_size = 0.
        beam_view_size = 0.

        # Consider sample
        if self.sample.__class__ == SubstrateSample:
            pass

        elif self.sample.__class__ == InclusionSample:
            sample_view_size = self.sample.inclusion_diameter_m

        elif self.sample.__class__ == HorizontalLayerSample or \
             self.sample.__class__ == VerticalLayerSample:
            sample_view_size = sum([l.thickness_m for l in self.sample.layers])

        elif self.sample.__class__ == SphereSample:
            sample_view_size = self.sample.diameter_m

        # Consider beams
        for beam in self.beams:
            if beam.__class__ == GaussianBeam:
                beam_view_size = max(beam_view_size, beam.diameter_m)

        # TODO consider trajectories
        for trajectory in self.trajectories:
            pass

        self._view_size = max(sample_view_size * SCALE_FACTOR,
                              beam_view_size * SCALE_FACTOR * 2,
                              10e-16)

    def draw(self, ax):
        """
        :param ax: an instance of matplotlib.axes.Axes
        """
        self._recalc_view_size()

        if self.sample:
            self._draw_sample(ax, self.sample, self.perspective)

        for beam in self.beams:
            self._draw_beam(ax, beam, self.perspective)

        for trajectory in self.trajectories:
            self._draw_trajectory(ax, trajectory, self.perspective)

        # self._view_size *= 1.1
        ax.set_xlim((-self._view_size / 2., self._view_size / 2.))
        ax.set_ylim((-self._view_size / 2., self._view_size / 2.))
        ax.set_aspect('equal')

    # DRAW SAMPLES
    def _draw_sample(self, ax, sample, perspective):
        sample_class = sample.__class__

        if sample_class not in self.sample_draw_methods:
            return

        method = self.sample_draw_methods[sample_class]

        patches = method(sample, perspective)
        col = PatchCollection(patches, match_original=True)

        if perspective is Perspective.XZ:
            trans = Affine2D().scale(sx=1, sy=1 + tan(abs(sample.tilt_rad))) + ax.transData
            col.set_transform(trans)
        elif perspective is Perspective.YZ:
            trans = Affine2D().rotate_around(0, 0, sample.tilt_rad) + ax.transData
            col.set_transform(trans)
        elif perspective is Perspective.XY:
            trans = Affine2D().scale(sx=1, sy=1 + tan(abs(sample.tilt_rad))) + ax.transData
            col.set_transform(trans)

        ax.add_collection(col)

    def _compose_substrate(self, material, perspective):
        if perspective is Perspective.XY:
            patches = [Rectangle((-self._view_size / 2., self._view_size / 2.),
                                 self._view_size, -self._view_size,
                                 color=material.color)]
        else:
            patches = [Rectangle((-self._view_size / 2., 0), self._view_size, -self._view_size / 2.,
                                 color=material.color)]

        return patches

    def _compose_sample_substrate(self, sample, perspective):
        return self._compose_substrate(sample.material, perspective)

    def _compose_sample_inclusion(self, sample, perspective):
        patches = list()

        patches.extend(self._compose_substrate(sample.substrate_material, perspective))

        if perspective is Perspective.XY:
            patches.append(Circle((0, 0), sample.inclusion_diameter_m,
                                  color=sample.inclusion_material.color))
        else:
            patches.append(Wedge((0, 0), sample.inclusion_diameter_m, 180, 0,
                                 color=sample.inclusion_material.color))

        return patches

    def _compose_sample_hlayer(self, sample, perspective):
        patches = list()

        if perspective is Perspective.XY:
            if len(sample.layers) > 0:
                patches.append(Rectangle((-self._view_size / 2., self._view_size / 2.),
                                         self._view_size, -self._view_size,
                                         color=sample.layers[0].material.color))

        else:
            depth_m = 0
            patches.extend(self._compose_substrate(sample.substrate_material, perspective))

            for layer in sample.layers:
                patches.append(Rectangle((-self._view_size / 2., depth_m),
                                         self._view_size, -layer.thickness_m,
                                         color=layer.material.color))
                depth_m -= layer.thickness_m

        return patches

    def _compose_sample_vlayer(self, sample, perspective):
        patches = list()

        if perspective is Perspective.XZ:
            patches.append(Rectangle((0, 0), -self._view_size / 2., -self._view_size / 2.,
                                     color=sample.left_material.color))
            patches.append(Rectangle((0, 0), self._view_size / 2., -self._view_size / 2.,
                                     color=sample.right_material.color))

            for layer, pos in zip(sample.layers, sample.layers_xpositions_m):
                patches.append(Rectangle((pos[0], 0), layer.thickness_m, -self._view_size / 2.,
                                         color=layer.material.color))
        elif perspective is Perspective.YZ:
            for layer, pos in zip(sample.layers, sample.layers_xpositions_m):
                if pos[1] >= 0.0:
                    patches.append(Rectangle((-self._view_size / 2., 0),
                                             self._view_size, -self._view_size / 2.,
                                             color=layer.material.color))
                    break

            if len(patches) == 0:
                patches.append(Rectangle((self._view_size / 2., 0),
                                         self._view_size, -self._view_size / 2.,
                                         color=sample.left_material.color))

        elif perspective is Perspective.XY:
            patches.append(Rectangle((0, self._view_size / 2.),
                                     - self._view_size / 2., -self._view_size,
                                     color=sample.left_material.color))
            patches.append(Rectangle((0, self._view_size / 2.),
                                     self._view_size / 2., -self._view_size,
                                     color=sample.right_material.color))

            for layer, pos in zip(sample.layers, sample.layers_xpositions_m):
                patches.append(Rectangle((pos[0], self._view_size / 2.),
                                         layer.thickness_m, -self._view_size,
                                         color=layer.material.color))

        return patches

    def _compose_sample_sphere(self, sample, perspective):
        patches = list()

        if perspective is Perspective.XY:
            patches.append(Circle((0, 0), sample.diameter_m / 2.,
                                  color=sample.material.color))
        else:
            patches.append(Circle((0, sample.diameter_m / -2.), sample.diameter_m / 2.,
                                  color=sample.material.color))

        return patches

    # DRAW BEAMS
    def _draw_beam(self, ax, beam, perspective):
        beam_class = beam.__class__
        if beam_class not in self.beam_draw_methods:
            return

        method = self.beam_draw_methods[beam_class]

        patches = method(beam, perspective)
        col = PatchCollection(patches, match_original=True)

        # TODO rotate
        if perspective is Perspective.XZ:
            pass
        elif perspective is Perspective.YZ:
            pass
        elif perspective is Perspective.XY:
            pass

        ax.add_collection(col)

    def _compose_beam_gaussian(self, beam, perspective):
        patches = []

        radius = beam.diameter_m / 2
        color = beam.particle.color

        if perspective is Perspective.XY:
            patches.append(Circle((0, 0), radius=radius, color=color))
        else:
            width = beam.diameter_m
            height = (self._view_size / 2) * 1.5
            patches.append(Rectangle((-radius, 0), width, height, color=color))

        return patches

    # DRAW TRAJECTORIES
    def _draw_trajectory(self, ax, trajectory, perspective):
        raise NotImplementedError


# for testing purpose TODO remove
####################################################################################################
####################################################################################################

import sys
from math import pi

from matplotlib import figure
from matplotlib.backends.backend_qt5agg import FigureCanvas, NavigationToolbar2QT

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QApplication, QVBoxLayout, QHBoxLayout, QGridLayout, \
    QComboBox, QSlider, QRadioButton, QButtonGroup, QLabel

DS = Material('Ds', {110: 1.}, 1.)
RG = Material('Rg', {111: 1.}, 1.)
AU = Material('Au', {79: 1.}, 1.)
RE = Material('Re', {75: 1.}, 1.)
OS = Material('Os', {76: 1.}, 1.)
IR = Material('Ir', {77: 1.}, 1.)
PT = Material('Pt', {78: 1.}, 1.)

class QtPlt (QDialog):

    cos = 0
    sin = 0

    def __init__ (self):
        QDialog.__init__ (self)

        # matplotlib
        self._figure = figure.Figure()
        self._canvas = FigureCanvas(self._figure)
        self._toolbar = NavigationToolbar2QT(self._canvas, self)

        # comboboxes
        self._combo_sample = QComboBox()
        self._combo_sample.addItem('--- choose sample ---', None)
        self._combo_sample.addItem('SubstrateSample', SubstrateSample)
        self._combo_sample.addItem('InclusionSample', InclusionSample)
        self._combo_sample.addItem('HLayerSample', HorizontalLayerSample)
        self._combo_sample.addItem('VLayerSample', VerticalLayerSample)
        self._combo_sample.addItem('SphereSample', SphereSample)
        self._combo_sample.currentIndexChanged.connect(self.plot)

        self._combo_beam = QComboBox()
        self._combo_beam.addItem('--- choose beam ---', None)
        self._combo_beam.addItem('GaussianBeam', GaussianBeam)
        self._combo_beam.currentIndexChanged.connect(self.plot)

        self._combo_trajectory = QComboBox()
        self._combo_trajectory.addItem('--- choose trajectory ---', None)
        self._combo_trajectory.currentIndexChanged.connect(self.plot)

        # slider
        self._slider_tilt_deg = QSlider(Qt.Horizontal)
        self._slider_tilt_deg.setMinimum(-180)
        self._slider_tilt_deg.setMaximum(180)
        self._slider_tilt_deg.setValue(0)
        self._slider_tilt_deg.sliderReleased.connect(self.plot)

        self._slider_rotation_deg = QSlider(Qt.Horizontal)
        self._slider_rotation_deg.setMinimum(-180)
        self._slider_rotation_deg.setMaximum(180)
        self._slider_rotation_deg.setValue(0)
        self._slider_rotation_deg.sliderReleased.connect(self.plot)
        self._slider_rotation_deg.setDisabled(True)

        # radio buttons
        self._radio_xz = QRadioButton('XZ')
        self.radio_yz = QRadioButton('YZ')
        self.radio_xy = QRadioButton('XY')
        self._radio_xz.setChecked(True)

        self._radio_perspective = QButtonGroup()
        self._radio_perspective.addButton(self._radio_xz)
        self._radio_perspective.addButton(self.radio_yz)
        self._radio_perspective.addButton(self.radio_xy)
        self._radio_perspective.buttonClicked.connect(self.plot)

        # layout
        sublayout_combo = QHBoxLayout()
        sublayout_combo.addWidget(self._combo_sample)
        sublayout_combo.addWidget(self._combo_beam)
        sublayout_combo.addWidget(self._combo_trajectory)

        sublayout_perspective = QGridLayout()
        sublayout_perspective.addWidget(self._radio_xz, 1, 1)
        sublayout_perspective.addWidget(self.radio_yz, 2, 1)
        sublayout_perspective.addWidget(self.radio_xy, 3, 1)
        sublayout_perspective.addWidget(QLabel('tilt'), 1, 2)
        sublayout_perspective.addWidget(QLabel('rotation'), 2, 2)
        sublayout_perspective.addWidget(self._slider_tilt_deg, 1, 3)
        sublayout_perspective.addWidget(self._slider_rotation_deg, 2, 3)

        layout = QVBoxLayout()
        layout.addWidget(self._toolbar)
        layout.addWidget(self._canvas)
        layout.addLayout(sublayout_combo)
        layout.addLayout(sublayout_perspective)
        self.setLayout(layout)

        self.plot()

    # def slider_event(self):
    #     pass

    def plot(self):
        deg2rad = lambda a: (a * 2. * pi) / 360.



        tilt_rad = deg2rad(self._slider_tilt_deg.value())
        rotation_rad = deg2rad(self._slider_rotation_deg.value())

        layer = [Layer(RE, .1), Layer(OS, .15),
                 Layer(IR, .2), Layer(PT, .05)]

        sample_cls = self._combo_sample.currentData()

        if sample_cls == SubstrateSample:
            sample = SubstrateSample(DS, tilt_rad=tilt_rad, rotation_rad=rotation_rad)
        elif sample_cls == InclusionSample:
            sample = InclusionSample(DS, AU, 0.5, tilt_rad=tilt_rad, rotation_rad=rotation_rad)
        elif sample_cls == HorizontalLayerSample:
            sample = HorizontalLayerSample(DS, layer, tilt_rad=tilt_rad, rotation_rad=rotation_rad)
        elif sample_cls == VerticalLayerSample:
            sample = VerticalLayerSample(DS, RG, layer, tilt_rad=tilt_rad,
                                         rotation_rad=rotation_rad)
        elif sample_cls == SphereSample:
            sample = SphereSample(AU, 0.5, tilt_rad=tilt_rad, rotation_rad=rotation_rad)
        else:
            sample = None

        beam_cls = self._combo_beam.currentData()

        if beam_cls == GaussianBeam:
            beams = [GaussianBeam(42., 0.05)]
        else:
            beams = []

        trajectory_cls = beam_cls = self._combo_trajectory.currentData()

        # TODO handle trajectories
        trajectories = []

        sf = SampleFigure(sample, beams, trajectories)

        if self.radio_yz.isChecked():
            sf.perspective = Perspective.YZ
        elif self.radio_xy.isChecked():
            sf.perspective = Perspective.XY
        else:
            sf.perspective = Perspective.XZ

        self._figure.clf()

        ax = self._figure.add_subplot(111)
        sf.draw(ax=ax)

        self._canvas.draw_idle()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    pe = QtPlt()
    pe.show()

    sys.exit(app.exec_())
