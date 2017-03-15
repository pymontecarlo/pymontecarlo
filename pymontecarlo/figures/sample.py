"""
Figure to draw a sample.
"""

# Standard library modules.
from math import sin, cos, tan
from random import choice as randchoice, randint

# Third party modules.
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
from pymontecarlo.util.color import COLOR_SET_GREY as CS_GREY, COLOR_SET_BROWN as CS_BROWN,\
    COLOR_SET_COLORFUL as CS_CLRFL

# Globals and constant variables.


class SampleFigure(Figure):

    _COLORS_ASSIGNED = {}
    _COLORS_USED = []

    def __init__(self, sample=None, beams=None, trajectories=None):
        super().__init__()

        self.ax_size = 2

        self.sample = sample

        if not beams:
            beams = []
        self.beams = beams

        if not trajectories:
            trajectories = []
        self.trajectories = trajectories

        self.sample_draw_methods = dict()
        self.sample_draw_methods[SubstrateSample] = self._compose_sample_substrate
        self.sample_draw_methods[InclusionSample] = self._compose_sample_inclusion
        self.sample_draw_methods[HorizontalLayerSample] = self._compose_sample_hlayer
        self.sample_draw_methods[VerticalLayerSample] = self._compose_sample_vlayer
        self.sample_draw_methods[SphereSample] = self._compose_sample_sphere

        self.beam_draw_methods = dict()
        self.beam_draw_methods[GaussianBeam] = self._compose_beam_gaussian

    def _get_color(self, color_set, color_used=None):
        """
        :param color_set: list like object that contains colors of a type matplotlib accepts
        :return: a unused color from selection or random color from selection if all are in use
        already
        """

        if color_used:
            for i in range(len(color_set)):
                color = color_set[i]
                if color not in color_used:
                    color_used.append(color)
                    return color

        return randchoice(color_set)

    def _get_material_color(self, key, color_set):
        """
        This method ensures that:
        * colors of different materials differ (at least if enough colors are available in set)
        * materials with same properties have same color

        :param key: Object of type Material
        :param color_set: list like object that contains colors of a type matplotlib accepts
        :return: color of a type matplotlib accepts
        """

        # TODO use Material as key once it's hashable
        key = key.__repr__()

        if key in SampleFigure._COLORS_ASSIGNED:
            return SampleFigure._COLORS_ASSIGNED[key]

        if color_set:
            color = self._get_color(color_set, color_used=SampleFigure._COLORS_USED)
        else:
            color = '#{:02x}{:02x}{:02x}'.format(randint(0, 255), randint(0, 255), randint(0, 255))

        SampleFigure._COLORS_ASSIGNED[key] = color

        return color

    def draw(self, ax, perspective='XZ'):

        self.ax_size = 2.2

        if self.sample:
            self._draw_sample(ax, self.sample, perspective)

        for beam in self.beams:
            self._draw_beam(ax, beam, perspective)

        for trajectory in self.trajectories:
            self._draw_trajectory(ax, trajectory, perspective)

        ax.set_xlim((-self.ax_size / 2., self.ax_size / 2.))
        ax.set_ylim((-self.ax_size / 2., self.ax_size / 2.))
        ax.set_aspect('equal')

    # DRAW SAMPLES

    def _draw_sample(self, ax, sample, perspective='XZ'):
        sample_class = sample.__class__

        if sample_class not in self.sample_draw_methods:
            return

        perspective = perspective.upper()
        method = self.sample_draw_methods[sample_class]

        patches = method(sample, perspective)

        col = PatchCollection(patches, match_original=True)

        # TODO rotate
        if perspective == 'XZ':
            trans = Affine2D().scale(sx=1, sy=1 + tan(abs(sample.tilt_rad))) + ax.transData
            col.set_transform(trans)
        elif perspective == 'YZ':
            trans = Affine2D().rotate_around(0, 0, sample.tilt_rad) + ax.transData
            col.set_transform(trans)
        elif perspective == 'XY':
            trans = Affine2D().scale(sx=1, sy=1 + tan(abs(sample.tilt_rad))) + ax.transData
            col.set_transform(trans)

        ax.add_collection(col)

    def _compose_sample_substrate(self, sample, perspective='XZ'):
        perspective = perspective.upper()

        if perspective == 'XZ' or perspective == 'YZ':
            patches = [Rectangle((-1, 0), 2, -1, color=self._get_material_color(sample.material,
                                                                                CS_GREY))]
        else:
            patches = [Rectangle((-1, 1), 2, -2, color=self._get_material_color(sample.material,
                                                                                CS_GREY))]

        return patches

    def _compose_sample_inclusion(self, sample, perspective='XZ'):
        patches = list()
        perspective = perspective.upper()

        if perspective == 'XZ' or perspective == 'YZ':
            patches.append(Rectangle((-1, 0), 2, -1,
                                     color=self._get_material_color(sample.substrate_material,
                                                                    CS_GREY)))
            patches.append(Wedge((0, 0), sample.inclusion_diameter_m, 180, 0,
                                 color=self._get_material_color(sample.inclusion_material,
                                                                CS_BROWN)))
        else:
            patches.append(Rectangle((-1, 1), 2, -2,
                                     color=self._get_material_color(sample.substrate_material,
                                                                    CS_GREY)))
            patches.append(Circle((0, 0), sample.inclusion_diameter_m,
                                  color=self._get_material_color(sample.inclusion_material,
                                                                 CS_BROWN)))

        return patches

    def _compose_sample_hlayer(self, sample, perspective='XZ'):
        patches = list()
        perspective = perspective.upper()

        if perspective == 'XZ' or perspective == 'YZ':
            depth_m = 0

            patches.append(Rectangle((-1, 0), 2, -1,
                                     color=self._get_material_color(sample.substrate_material,
                                                                    CS_GREY)))

            for layer in sample.layers:
                patches.append(Rectangle((-1, depth_m), 2, -layer.thickness_m,
                                         color=self._get_material_color(layer.material,
                                                                        CS_BROWN)))
                depth_m -= layer.thickness_m
        else:
            if len(sample.layers) == 0:
                patches.append(Rectangle((-1, 1), 2, -2,
                                         color=self._get_material_color(sample.substrate_material,
                                                                        CS_GREY)))
            else:
                patches.append(Rectangle((-1, 1), 2, -2,
                                         color=self._get_material_color(sample.layers[0].material,
                                                                        CS_GREY)))

        return patches

    def _compose_sample_vlayer(self, sample, perspective='XZ'):
        patches = list()
        perspective = perspective.upper()

        if perspective == 'XZ':
            patches.append(Rectangle((0, 0), -1, -1,
                                     color=self._get_material_color(sample.left_material,
                                                                    CS_GREY)))
            patches.append(Rectangle((0, 0), 1, -1,
                                     color=self._get_material_color(sample.right_material,
                                                                    CS_GREY)))

            for layer, pos in zip(sample.layers, sample.layers_xpositions_m):
                patches.append(Rectangle((pos[0], 0), layer.thickness_m, -1,
                                         color=self._get_material_color(layer.material, CS_BROWN)))
        elif perspective == 'YZ':
            for layer, pos in zip(sample.layers, sample.layers_xpositions_m):
                if pos[1] >= 0.0:
                    patches.append(Rectangle((-1, 0), 2, -1,
                                             color=self._get_material_color(layer.material,
                                                                            CS_BROWN)))
                    break
            if len(patches) == 0:
                patches.append(Rectangle((1, 0), 2, -1,
                                         color=self._get_material_color(sample.left_material,
                                                                        CS_GREY)))
        elif perspective == 'XY':
            patches.append(Rectangle((0, 1), -1, -2,
                                     color=self._get_material_color(sample.left_material,
                                                                    CS_GREY)))
            patches.append(Rectangle((0, 1), 1, -2,
                                     color=self._get_material_color(sample.right_material,
                                                                    CS_GREY)))

            for layer, pos in zip(sample.layers, sample.layers_xpositions_m):
                patches.append(Rectangle((pos[0], 1), layer.thickness_m, -2,
                                         color=self._get_material_color(layer.material, CS_BROWN)))

        return patches

    def _compose_sample_sphere(self, sample, perspective='XZ'):
        patches = list()
        perspective = perspective.upper()

        if perspective == 'XZ' or perspective == 'YZ':
            patches.append(Circle((0, sample.diameter_m / -2.), sample.diameter_m / 2.,
                                  color=self._get_material_color(sample.material, CS_BROWN)))
        else:
            patches.append(Circle((0, 0), sample.diameter_m / 2.,
                                  color=self._get_material_color(sample.material, CS_BROWN)))

        return patches

    # DRAW BEAMS

    def _draw_beam(self, ax, beam, perspective='XZ'):
        beam_class = beam.__class__
        if beam_class not in self.beam_draw_methods:
            return

        method = self.beam_draw_methods[beam_class]

        patches = method(beam, perspective)

        col = PatchCollection(patches, match_original=True)

        # TODO rotate
        if perspective == 'XZ':
            pass
        elif perspective == 'YZ':
            pass
        elif perspective == 'XY':
            pass

        ax.add_collection(col)

    def _compose_beam_gaussian(self, beam, perspective='XZ'):
        patches = list()

        if perspective == 'XZ' or perspective == 'YZ':
            patches.append(Rectangle((0 - beam.diameter_m / 2, 0), beam.diameter_m, 1,
                                     color='#00549F'))
        else:
            # FIXME for some reason radius behaves like diameter
            patches.append(Circle((0, 0), radius=beam.diameter_m / 2., color='#FF0000'))

        return patches

    # DRAW TRAJECTORIES

    def _draw_trajectory(self, ax, trajectory, perspective='XZ'):
        raise NotImplementedError


# for testing purpose TODO remove
####################################################################################################
####################################################################################################

import sys
from math import pi

from matplotlib import figure
from matplotlib.backends.backend_qt5agg import FigureCanvas, NavigationToolbar2QT

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QApplication, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox,\
    QSlider, QRadioButton, QButtonGroup, QLabel

class QtPlt (QDialog):

    cos = 0
    sin = 0

    def __init__ (self):
        QDialog.__init__ (self)

        # matplotlib
        self.figure = figure.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        # comboboxes
        self.combo_sample = QComboBox()
        self.combo_sample.addItem('--- choose sample ---', None)
        self.combo_sample.addItem('SubstrateSample', SubstrateSample)
        self.combo_sample.addItem('InclusionSample', InclusionSample)
        self.combo_sample.addItem('HLayerSample', HorizontalLayerSample)
        self.combo_sample.addItem('VLayerSample', VerticalLayerSample)
        self.combo_sample.addItem('SphereSample', SphereSample)
        self.combo_sample.currentIndexChanged.connect(self.plot)

        self.combo_beam = QComboBox()
        self.combo_beam.addItem('--- choose beam ---', None)
        self.combo_beam.addItem('GaussianBeam', GaussianBeam)
        self.combo_beam.currentIndexChanged.connect(self.plot)

        self.combo_trajectory = QComboBox()
        self.combo_trajectory.addItem('--- choose trajectory ---', None)
        self.combo_trajectory.currentIndexChanged.connect(self.plot)

        # slider
        self.slider_tilt_deg = QSlider(Qt.Horizontal)
        self.slider_tilt_deg.setMinimum(-180)
        self.slider_tilt_deg.setMaximum(180)
        self.slider_tilt_deg.setValue(0)
        self.slider_tilt_deg.sliderReleased.connect(self.plot)

        self.slider_rotation_deg = QSlider(Qt.Horizontal)
        self.slider_rotation_deg.setMinimum(-180)
        self.slider_rotation_deg.setMaximum(180)
        self.slider_rotation_deg.setValue(0)
        self.slider_rotation_deg.sliderReleased.connect(self.plot)

        # radio buttons
        self.radio_xz = QRadioButton('XZ')
        self.radio_yz = QRadioButton('YZ')
        self.radio_xy = QRadioButton('XY')
        self.radio_xz.setChecked(True)

        self.radio_perspective = QButtonGroup()
        self.radio_perspective.addButton(self.radio_xz)
        self.radio_perspective.addButton(self.radio_yz)
        self.radio_perspective.addButton(self.radio_xy)
        self.radio_perspective.buttonClicked.connect(self.plot)

        # layout
        sublayout_combo = QHBoxLayout()
        sublayout_combo.addWidget(self.combo_sample)
        sublayout_combo.addWidget(self.combo_beam)
        sublayout_combo.addWidget(self.combo_trajectory)

        sublayout_perspective = QGridLayout()
        sublayout_perspective.addWidget(self.radio_xz, 1, 1)
        sublayout_perspective.addWidget(self.radio_yz, 2, 1)
        sublayout_perspective.addWidget(self.radio_xy, 3, 1)
        sublayout_perspective.addWidget(QLabel('tilt'), 1, 2)
        sublayout_perspective.addWidget(QLabel('rotation'), 2, 2)
        sublayout_perspective.addWidget(self.slider_tilt_deg, 1, 3)
        sublayout_perspective.addWidget(self.slider_rotation_deg, 2, 3)

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addLayout(sublayout_combo)
        layout.addLayout(sublayout_perspective)
        self.setLayout(layout)

        self.plot()

    # def slider_event(self):
    #     pass

    def plot(self):
        deg2rad = lambda a: (a * 2. * pi) / 360.

        ds = Material('Ds', {110: 1.}, 1.)
        rg = Material('Rg', {111: 1.}, 1.)
        au = Material('Au', {79: 1.}, 1.)

        tilt_rad = deg2rad(self.slider_tilt_deg.value())
        rotation_rad = deg2rad(self.slider_rotation_deg.value())

        layer = [Layer(Material('Re', {75: 1.}, 1.), .1), Layer(Material('Os', {76: 1.}, 1.), .15),
                 Layer(Material('Ir', {77: 1.}, 1.), .2), Layer(Material('Pt', {78: 1.}, 1.), .05)]

        sample_cls = self.combo_sample.currentData()

        if sample_cls == SubstrateSample:
            sample = SubstrateSample(ds, tilt_rad=tilt_rad, rotation_rad=rotation_rad)
        elif sample_cls == InclusionSample:
            sample = InclusionSample(ds, au, 0.5, tilt_rad=tilt_rad, rotation_rad=rotation_rad)
        elif sample_cls == HorizontalLayerSample:
            sample = HorizontalLayerSample(ds, layer, tilt_rad=tilt_rad, rotation_rad=rotation_rad)
        elif sample_cls == VerticalLayerSample:
            sample = VerticalLayerSample(ds, rg, layer, tilt_rad=tilt_rad,
                                         rotation_rad=rotation_rad)
        elif sample_cls == SphereSample:
            sample = SphereSample(au, 0.5, tilt_rad=tilt_rad, rotation_rad=rotation_rad)
        else:
            sample = None

        beam_cls = self.combo_beam.currentData()

        if beam_cls == GaussianBeam:
            beams = [GaussianBeam(42., 0.05)]
        else:
            beams = []

        trajectory_cls = beam_cls = self.combo_trajectory.currentData()

        # TODO handle trajectories
        trajectories = []

        if self.radio_yz.isChecked():
            perspective = 'YZ'
        elif self.radio_xy.isChecked():
            perspective = 'XY'
        else:
            perspective = 'XZ'

        sf = SampleFigure(sample, beams, trajectories)

        self.figure.clf()

        ax = self.figure.add_subplot(111)
        sf.draw(ax=ax, perspective=perspective)

        self.canvas.draw_idle()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    pe = QtPlt()
    pe.show()

    sys.exit(app.exec_())