"""
Figure to draw a sample.
"""

# Standard library modules.
from random import randint, choice as randchoice

# Third party modules.
from matplotlib.patches import Wedge, Rectangle, Circle

# Local modules.
from pymontecarlo.figures.base import Figure
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import SubstrateSample, InclusionSample, HorizontalLayerSample, \
    VerticalLayerSample, SphereSample
from pymontecarlo.options.sample.base import Layer

# Globals and constant variables.
_ASSIGNED_COLORS = {}
_USED_COLORS = []

CLR_SELECTION_GREY = ('#282828',
                      '#323232',
                      '#3C3C3C',
                      '#464646',
                      '#505050',
                      '#5A5A5A',
                      '#646464')
CLR_SELECTION_BROWN = ('#CD853F',
                       '#6B4423',
                       '#EDC9AF',
                       '#C3B091',
                       '#826644',
                       '#80461B',
                       '#832A0D',
                       '#D2B48C',
                       '#C19A6B')
CLR_SELECTION_COLORFUL = ('#FFB300', # Vivid Yellow
                          '#803E75', # Strong Purple
                          '#FF6800', # Vivid Orange
                          '#A6BDD7', # Very Light Blue
                          '#C10020', # Vivid Red
                          '#CEA262', # Grayish Yellow
                          '#817066', # Medium Gray

                          # The following don't work well for people with defective color vision
                          '#007D34', # Vivid Green
                          '#F6768E', # Strong Purplish Pink
                          '#00538A', # Strong Blue
                          '#FF7A5C', # Strong Yellowish Pink
                          '#53377A', # Strong Violet
                          '#FF8E00', # Vivid Orange Yellow
                          '#B32851', # Strong Purplish Red
                          '#F4C800', # Vivid Greenish Yellow
                          '#93AA00', # Vivid Yellowish Green
                          '#F13A13', # Vivid Reddish Orange
                          '#232C16')

def get_color(clr_selection):
    """
    :param clr_selection: list like object that contains colors of a type matplotlib accepts
    :return: a unused color from selection or random color from selection if all are used already
    """
    for i in range(len(clr_selection)):
        color = clr_selection[i]
        if color not in _USED_COLORS:
            _USED_COLORS.append(color)
            return color
    return randchoice(clr_selection)

def get_material_color(material, clr_selection):
    """
    This method ensures that:
    * colors of different materials differ (at least if enough colors are available)
    * materials with same properties have same color

    :param material: Object of type Material
    :param clr_selection: list like object that contains colors of a type matplotlib accepts
    :return: color of a type matplotlib accepts
    """
    material_str = str(material)

    if material_str in _ASSIGNED_COLORS:
        return _ASSIGNED_COLORS[material_str]

    color = get_color(clr_selection)
    _ASSIGNED_COLORS[material_str] = color

    return color

class SampleFigure(Figure):

    def __init__(self, sample=None, beams=None, trajectories=None):
        super().__init__()

        self.sample = sample

        if not beams:
            self.beams = []
        else:
            self.beams = beams

        if not trajectories:
            self.trajectories = []
        else:
            self.trajectories = trajectories

        self.sample_draw_methods = {}
        self.sample_draw_methods[SubstrateSample] = self._draw_sample_substrate
        self.sample_draw_methods[InclusionSample] = self._draw_sample_inclusion
        self.sample_draw_methods[HorizontalLayerSample] = self._draw_sample_hlayer
        self.sample_draw_methods[VerticalLayerSample] = self._draw_sample_vlayer
        self.sample_draw_methods[SphereSample] = self._draw_sample_sphere

        self.beam_draw_methods = {}
        self.beam_draw_methods[GaussianBeam] = self._draw_beam_gaussian

    def draw(self, ax, x_y_z='xy'):
        # TODO consider perspective
        if self.sample:
            self._draw_sample(ax, self.sample)

        for beam in self.beams:
            self._draw_beam(ax, beam)

        for trajectory in self.trajectories:
            self._draw_trajectory(ax, trajectory)

    # DRAW SAMPLES

    # TODO: _draw_sample, _draw_beam and _draw_trajectory may be merged
    def _draw_sample(self, ax, sample):
        sample_class = sample.__class__

        if sample_class not in self.sample_draw_methods:
            return

        method = self.sample_draw_methods[sample_class]
        method(ax, sample)

    def _draw_sample_substrate(self, ax, sample):
        ax.add_patch(Rectangle((-1, 0), 2, -1, color=get_material_color(sample.material,
                                                                        CLR_SELECTION_GREY)))

    def _draw_sample_inclusion(self, ax, sample):
        ax.add_patch(Rectangle((-1, 0), 2, -1, color=get_material_color(sample.substrate_material,
                                                                        CLR_SELECTION_GREY)))
        ax.add_patch(Wedge((0, 0), sample.inclusion_diameter_m, 180, 0,
                     color=get_material_color(sample.inclusion_material, CLR_SELECTION_BROWN)))

    def _draw_sample_hlayer(self, ax, sample):
        ax.add_patch(Rectangle((-1, 0), 2, -1, color=get_material_color(sample.substrate_material,
                                                                        CLR_SELECTION_GREY)))

        depth_m = 0

        for layer in sample.layers:
            ax.add_patch(Rectangle((-1, depth_m), 2, -layer.thickness_m,
                                   color=get_material_color(layer.material, CLR_SELECTION_BROWN)))
            depth_m -= layer.thickness_m

    def _draw_sample_vlayer(self, ax, sample):
        depth_m = min(sample.depth_m, 1)

        ax.add_patch(Rectangle((0, 0), -1, -1, color=get_material_color(sample.left_material,
                                                                        CLR_SELECTION_GREY)))
        ax.add_patch(Rectangle((0, 0), 1, -1, color=get_material_color(sample.right_material,
                                                                       CLR_SELECTION_GREY)))

        for layer, pos in zip(sample.layers, sample.layers_xpositions_m):
            ax.add_patch(Rectangle((pos[0], 0), layer.thickness_m, -1,
                                   color=get_material_color(layer.material, CLR_SELECTION_BROWN)))

    def _draw_sample_sphere(self, ax, sample):
        ax.add_patch(Circle((0, sample.diameter_m / -2.), sample.diameter_m / 2.,
                     color=get_material_color(sample.material, CLR_SELECTION_BROWN)))

    # DRAW BEAMS

    def _draw_beam(self, ax, beam):
        beam_class = beam.__class__
        if beam_class not in self.beam_draw_methods:
            return

        method = self.beam_draw_methods[beam_class]
        method(ax, beam)

    def _draw_beam_gaussian(self, ax, beam):
        # TODO use color gradient to represent intensity
        ax.add_patch(Rectangle((0 - beam.diameter_m / 2, 0), beam.diameter_m, 1, color='#DD00FF'))

    # DRAW TRAJECTORIES

    def _draw_trajectory(self, ax, trajectory):
        raise NotImplementedError

# for testing purpose TODO remove
import sys

from matplotlib import figure
from matplotlib.backends.backend_qt5agg import FigureCanvas, NavigationToolbar2QT

from PyQt5.QtCore import QVariant
from PyQt5.QtWidgets import QDialog, QApplication, QVBoxLayout, QHBoxLayout, QComboBox

class QtPlt (QDialog):

    cos = 0
    sin = 0

    def __init__ (self):
        QDialog.__init__ (self)

        self.figure = figure.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        self.combo_sample = QComboBox()
        self.combo_sample.addItem('--- choose sample ---', QVariant(None))
        self.combo_sample.addItem('SubstrateSample', QVariant(SubstrateSample))
        self.combo_sample.addItem('InclusionSample', QVariant(InclusionSample))
        self.combo_sample.addItem('HLayerSample', QVariant(HorizontalLayerSample))
        self.combo_sample.addItem('VLayerSample', QVariant(VerticalLayerSample))
        self.combo_sample.addItem('SphereSample', QVariant(SphereSample))
        self.combo_sample.currentIndexChanged.connect(self.plot)

        self.combo_beam = QComboBox()
        self.combo_beam.addItem('--- choose beam ---', QVariant(None))
        self.combo_beam.addItem('GaussianBeam', QVariant(GaussianBeam))
        self.combo_beam.currentIndexChanged.connect(self.plot)

        self.combo_trajectory = QComboBox()
        self.combo_trajectory.addItem('--- choose trajectory ---', QVariant(None))
        self.combo_trajectory.currentIndexChanged.connect(self.plot)

        # set the layout
        sublayout = QHBoxLayout()
        sublayout.addWidget(self.combo_sample)
        sublayout.addWidget(self.combo_beam)
        sublayout.addWidget(self.combo_trajectory)

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addLayout(sublayout)
        self.setLayout(layout)

        self.plot()

    # def slider_event(self):
    #     pass

    def plot(self):
        ds = Material('Ds', {110: 1.}, 1.)
        rg = Material('Rg', {111: 1.}, 1.)
        au = Material('Au', {79: 1.}, 1.)

        layer = [Layer(Material('Re', {75: 1.}, 1.), .1), Layer(Material('Os', {76: 1.}, 1.), .15),
                 Layer(Material('Ir', {77: 1.}, 1.), .2), Layer(Material('Pt', {78: 1.}, 1.), .05)]

        sample_cls = self.combo_sample.currentData()

        if sample_cls == SubstrateSample:
            sample = SubstrateSample(ds)
        elif sample_cls == InclusionSample:
            sample = InclusionSample(ds, au, 0.5)
        elif sample_cls == HorizontalLayerSample:
            sample = HorizontalLayerSample(ds, layer)
        elif sample_cls == VerticalLayerSample:
            sample = VerticalLayerSample(ds, rg, layer)
        elif sample_cls == SphereSample:
            sample = SphereSample(au, 0.5)
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

        sf = SampleFigure(sample, beams, trajectories)

        self.figure.clf()

        ax = self.figure.add_subplot(111)
        sf.draw(ax)

        # TODO autodetect dimensions of setup
        ax.set_xlim((-1.1, 1.1))
        ax.set_ylim((-1.1, 1.1))
        ax.set_aspect('equal')

        self.canvas.draw_idle()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    pe = QtPlt()
    pe.show()

    sys.exit(app.exec_())