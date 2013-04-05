#!/usr/bin/env python
"""
================================================================================
:mod:`geometry` -- Controls for geometry
================================================================================

.. module:: geometry
   :synopsis: Controls for geometry

.. inheritance-diagram:: pymontecarlo.ui.gui.input.geometry

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import math
import copy
from itertools import product

# Third party modules.
from OpenGL import GL
from OpenGL import GLU
import wx
import numpy as np

# Local modules.
from wxtools2.combobox import PyComboBox
from wxtools2.floattext import FloatRangeTextCtrl, FloatRangeTextValidator

from pymontecarlo.input.geometry import \
    Substrate, Inclusion, MultiLayers, GrainBoundaries, Sphere
from pymontecarlo.util.manager import ClassManager
from pymontecarlo.util.human import camelcase_to_words

from pymontecarlo.ui.gui.input.material import \
    MaterialListCtrl, EVT_LIST_MATERIAL_ADDED, EVT_LIST_MATERIAL_DELETED
from pymontecarlo.ui.gui.input.wizardpage import WizardPage
from pymontecarlo.ui.gui.input.body import \
    (LayersListCtrl, EVT_LIST_LAYER_ADDED, EVT_LIST_LAYER_DELETED,
     EVT_LIST_LAYER_MODIFIED)

# Globals and constants variables.
from pymontecarlo.ui.gui.color import COLORS

GeometryGLManager = ClassManager()

class _GeometryGL(object):

    def __init__(self, geometry, **kwargs):
        self._geometry = geometry

    @property
    def geometry(self):
        return self._geometry

    def initgl(self):
        raise NotImplementedError

    def drawgl(self):
        GL.glPushMatrix()

        GL.glRotate(math.degrees(self.geometry.tilt_rad), 1.0, 0.0, 0.0)
        GL.glRotate(math.degrees(self.geometry.rotation_rad), 0.0, 0.0, 1.0)

        self._drawgl()

        GL.glPopMatrix()

    def _drawgl(self):
        raise NotImplementedError

    def destroygl(self):
        pass

class SubstrateGL(_GeometryGL):

    def initgl(self):
        # Dimensions
        substrate_radius = 1.0

        # Colors
        color = COLORS[10] + (0.5,)

        # Objects
        self._qobj = GLU.gluNewQuadric()

        self._substrate_top = GL.glGenLists(1)
        GL.glNewList(self._substrate_top, GL.GL_COMPILE)
        GL.glColor(*color)
        GLU.gluDisk(self._qobj, 0, substrate_radius, 36, 1)
        GL.glEndList()

    def _drawgl(self):
        GL.glCallList(self._substrate_top)

    def destroygl(self):
        GLU.gluDeleteQuadric(self._qobj)

GeometryGLManager.register(Substrate, SubstrateGL)

class InclusionGL(_GeometryGL):

    def initgl(self):
        # Dimensions
        substrate_radius = 1.0
        inclusion_radius = self.geometry.inclusion_diameter_m * 1e6 / 2.0

        # Colors
        substrate_color = COLORS[10] + (0.5,)
        inclusion_color = COLORS[11] + (0.5,)

        # Objects
        self._qobj = GLU.gluNewQuadric()

        self._substrate_top = GL.glGenLists(1)
        GL.glNewList(self._substrate_top, GL.GL_COMPILE)
        GL.glColor(*substrate_color)
        GLU.gluDisk(self._qobj, inclusion_radius, substrate_radius, 36, 1)
        GL.glEndList()

        self._inclusion_top = GL.glGenLists(1)
        GL.glNewList(self._inclusion_top, GL.GL_COMPILE)
        GL.glColor(*inclusion_color)
        GLU.gluDisk(self._qobj, 0, inclusion_radius, 36, 1)
        GL.glEndList()

        self._inclusion_sphere = GL.glGenLists(1)
        GL.glNewList(self._inclusion_sphere, GL.GL_COMPILE)
        GL.glColor(*inclusion_color)
        GLU.gluSphere(self._qobj, inclusion_radius, 36, 36)
        GL.glEndList()

    def _drawgl(self):
        GL.glCallList(self._substrate_top)
        GL.glCallList(self._inclusion_top)

        GL.glClipPlane(GL.GL_CLIP_PLANE1, [0, 0, -1.0, 0.0])
        GL.glEnable(GL.GL_CLIP_PLANE1)
        GL.glCallList(self._inclusion_sphere)
        GL.glDisable(GL.GL_CLIP_PLANE1)

    def destroygl(self):
        GLU.gluDeleteQuadric(self._qobj)

GeometryGLManager.register(Inclusion, InclusionGL)

class MultiLayersGL(_GeometryGL):

    def initgl(self):
        # Dimensions
        substrate_radius = 1.0

        # Objects
        self._qobj = GLU.gluNewQuadric()
        self._disk = GL.glGenLists(1)
        GL.glNewList(self._disk, GL.GL_COMPILE)
        GLU.gluDisk(self._qobj, 0, substrate_radius, 36, 1)
        GL.glEndList()

    def _drawgl(self):
        for i, layer in enumerate(self.geometry.layers):
            color = COLORS[10 + (i % 80)] + (0.5,)
            dims = self.geometry.get_dimensions(layer)

            GL.glPushMatrix()
            GL.glTranslate(0.0, 0.0, dims.zmax_m * 1e6)
            GL.glColor(*color)
            GL.glCallList(self._disk)
            GL.glPopMatrix()

        GL.glPushMatrix()
        GL.glTranslate(0.0, 0.0, dims.zmin_m * 1e6)
        color = COLORS[10 + (i + 1 % 80)] + (0.5,)
        GL.glColor(*color)
        GL.glCallList(self._disk)
        GL.glPopMatrix()

    def destroygl(self):
        GLU.gluDeleteQuadric(self._qobj)

GeometryGLManager.register(MultiLayers, MultiLayersGL)

class GrainBoundariesGL(_GeometryGL):

    def initgl(self):
        # Dimensions
        substrate_radius = 1.0

        # Color
        color_substrate = COLORS[10] + (0.5,)

        # Objects
        self._qobj = GLU.gluNewQuadric()

        self._top = GL.glGenLists(1)
        GL.glNewList(self._top, GL.GL_COMPILE)
        GL.glColor(*color_substrate)
        GLU.gluDisk(self._qobj, 0, substrate_radius, 36, 1)
        GL.glEndList()

        self._planes = []
        self._planes.append(self._create_plane(self.geometry.left_body, substrate_radius))

        for layer in self.geometry.layers:
            self._planes.append(self._create_plane(layer, substrate_radius))

    def _create_plane(self, body, radius):
        dims = self.geometry.get_dimensions(body)
        glist = GL.glGenLists(1)

        GL.glNewList(glist, GL.GL_COMPILE)
        GL.glBegin(GL.GL_QUADS)
        GL.glNormal(1.0, 0.0, 0.0)
        GL.glVertex(dims.xmax_m * 1e6, -radius, 0.0)
        GL.glVertex(dims.xmax_m * 1e6, -radius, -radius)
        GL.glVertex(dims.xmax_m * 1e6, radius, -radius)
        GL.glVertex(dims.xmax_m * 1e6, radius, 0.0)
        GL.glEnd()
        GL.glEndList()

        return glist

    def _drawgl(self):
        GL.glCallList(self._top)

        for i, plane in enumerate(self._planes):
            color = COLORS[11 + (i % 80)] + (0.5,)
            GL.glColor(*color)
            GL.glCallList(plane)

    def destroygl(self):
        GLU.gluDeleteQuadric(self._qobj)

GeometryGLManager.register(GrainBoundaries, GrainBoundariesGL)

class SphereGL(_GeometryGL):

    def initgl(self):
        # Dimensions
        radius = self.geometry.diameter_m * 1e6 / 2.0

        # Colors
        color = COLORS[10] + (0.5,)

        # Objects
        self._qobj = GLU.gluNewQuadric()
        self._inclusion_sphere = GL.glGenLists(1)
        GL.glNewList(self._inclusion_sphere, GL.GL_COMPILE)
        GL.glColor(*color)
        GLU.gluSphere(self._qobj, radius, 36, 36)
        GL.glEndList()

    def _drawgl(self):
        GL.glPushMatrix()
        GL.glTranslate(0.0, 0.0, -self.geometry.diameter_m * 1e6 / 2.0)
        GL.glCallList(self._inclusion_sphere)
        GL.glPopMatrix()

    def destroygl(self):
        GLU.gluDeleteQuadric(self._qobj)

GeometryGLManager.register(Sphere, SphereGL)

#------------------------------------------------------------------------------

GeometryPanelManager = ClassManager()

class GeometryWizardPage(WizardPage):

    def __init__(self, wizard):
        WizardPage.__init__(self, wizard, 'Geometry definition')

        # Controls
        ## Type
        lbltype = wx.StaticText(self, label='Type')
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD)
        lbltype.SetFont(font)
        getter = lambda t: camelcase_to_words(t.__name__)
        self._cbtype = PyComboBox(self, getter)

        ## Type panel
        self._panel = wx.Panel(self)

        ## Tilt
        lbltilt = wx.StaticText(self, label=u'Tilt (\u00b0)')
        lbltilt.SetForegroundColour(wx.BLUE)
        validator = FloatRangeTextValidator(range=(-180.0, 180.0))
        self._txttilt = FloatRangeTextCtrl(self, name='tilt',
                                           validator=validator)
        self._txttilt.SetValues([0.0])

        ## Rotation
        lblrotation = wx.StaticText(self, label=u'Rotation (\u00b0)')
        lblrotation.SetForegroundColour(wx.BLUE)
        validator = FloatRangeTextValidator(range=(-180.0, 180.0))
        self._txtrotation = FloatRangeTextCtrl(self, name='rotation',
                                               validator=validator)
        self._txtrotation.SetValues([0.0])

        # Sizer
        self._sizer = wx.BoxSizer(wx.VERTICAL)

        szr_type = wx.BoxSizer(wx.HORIZONTAL)
        self._sizer.Add(szr_type, 0, wx.EXPAND | wx.ALL, 5)
        szr_type.Add(lbltype, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        szr_type.Add(self._cbtype, 1, wx.GROW)

        self._sizer.Add(self._panel, 1, wx.EXPAND | wx.ALL, 5)

        szr_extra = wx.GridBagSizer(5, 5)
        self._sizer.Add(szr_extra, 0, wx.GROW | wx.ALL, 5)
        szr_extra.AddGrowableCol(1)
        szr_extra.Add(lbltilt, pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        szr_extra.Add(self._txttilt, pos=(0, 1), flag=wx.GROW)
        szr_extra.Add(lblrotation, pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        szr_extra.Add(self._txtrotation, pos=(1, 1), flag=wx.GROW)

        self.SetSizer(self._sizer)

        # Bind
        self.Bind(wx.EVT_COMBOBOX, self.OnType, self._cbtype)

        self.Bind(wx.EVT_TEXT, self.OnValueChanged, self._txttilt)
        self.Bind(wx.EVT_TEXT, self.OnValueChanged, self._txtrotation)

        # Add types
        for clasz in wizard.available_geometries:
            try:
                GeometryPanelManager.get(clasz)
            except KeyError:
                continue
            self._cbtype.append(clasz)

        if not self._cbtype: # Empty
            raise ValueError, 'No geometry panel found'

        self._cbtype.selection = self._cbtype[0]

    def OnType(self, event):
        clasz = self._cbtype.selection
        panel_class = GeometryPanelManager.get(clasz)

        oldpanel = self._panel
        panel = panel_class(self)

        self.Freeze()

        self._sizer.Replace(oldpanel, panel)
        panel.Show()

        oldpanel.Destroy()
        self._panel = panel

        self._sizer.Layout()
        self.Thaw()

    def get_options(self):
        tilts = np.radians(self._txttilt.GetValues())
        rotations = np.radians(self._txtrotation.GetValues())
        panel_geometries = self._panel.get_geometries()

        geometries = []
        for panel_geometry, tilt, rotation in \
                product(panel_geometries, tilts, rotations):
            geometry = copy.copy(panel_geometry)
            geometry.tilt_rad = tilt
            geometry.rotation_rad = rotation
            geometries.append(geometry)

        return geometries

class _GeometryPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

    def OnValueChanged(self, event):
        self.GetParent().OnValueChanged(event)

    def get_geometries(self):
        return []

class SubstratePanel(_GeometryPanel):

    def __init__(self, parent):
        _GeometryPanel.__init__(self, parent)

        # Controls
        self._lstmaterials = MaterialListCtrl(self)

        # Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._lstmaterials, 1, wx.EXPAND)

        self.SetSizer(sizer)

        # Bind
        self.Bind(EVT_LIST_MATERIAL_ADDED, self.OnValueChanged, self._lstmaterials)
        self.Bind(EVT_LIST_MATERIAL_DELETED, self.OnValueChanged, self._lstmaterials)

    def get_geometries(self):
        geometries = []

        for material in self._lstmaterials.GetMaterials():
            geometry = Substrate(material)
            geometries.append(geometry)

        return geometries

GeometryPanelManager.register(Substrate, SubstratePanel)

class InclusionPanel(_GeometryPanel):

    def __init__(self, parent):
        _GeometryPanel.__init__(self, parent)

        # Controls
        lbldiameter = wx.StaticText(self, label='Inclusion diameter (nm)')
        lbldiameter.SetForegroundColour(wx.BLUE)
        validator = FloatRangeTextValidator(range=(0.0001, float('inf')))
        self._txtdiameter = FloatRangeTextCtrl(self, name='inclusion diameter',
                                               validator=validator)
        self._txtdiameter.SetValues([100.0])

        lblsubstrate = wx.StaticText(self, label='Substrate')
        lblsubstrate.SetForegroundColour(wx.BLUE)
        self._lstsubstrate = MaterialListCtrl(self, name="susbstrate material")

        lblinclusion = wx.StaticText(self, label='Inclusion')
        lblinclusion.SetForegroundColour(wx.BLUE)
        self._lstinclusion = MaterialListCtrl(self, name="inclusion material")

        # Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        szr_diameter = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(szr_diameter, 0, wx.EXPAND)
        szr_diameter.Add(lbldiameter, 0, wx.ALIGN_CENTER_VERTICAL)
        szr_diameter.Add(self._txtdiameter, 1, wx.GROW | wx.LEFT, 5)

        sizer.Add(lblsubstrate, 0, wx.TOP, 20)
        sizer.Add(self._lstsubstrate, 1, wx.EXPAND)
        sizer.Add(lblinclusion, 0, wx.TOP, 20)
        sizer.Add(self._lstinclusion, 1, wx.EXPAND)

        self.SetSizer(sizer)

        # Bind
        self.Bind(wx.EVT_TEXT, self.OnValueChanged, self._txtdiameter)
        self.Bind(EVT_LIST_MATERIAL_ADDED, self.OnValueChanged, self._lstsubstrate)
        self.Bind(EVT_LIST_MATERIAL_DELETED, self.OnValueChanged, self._lstsubstrate)
        self.Bind(EVT_LIST_MATERIAL_ADDED, self.OnValueChanged, self._lstinclusion)
        self.Bind(EVT_LIST_MATERIAL_DELETED, self.OnValueChanged, self._lstinclusion)

    def get_geometries(self):
        diameters = np.array(self._txtdiameter.GetValues()) * 1e-9

        geometries = []

        for substrate, inclusion, diameter in \
                product(self._lstsubstrate.GetMaterials(),
                        self._lstinclusion.GetMaterials(),
                        diameters):
            geometry = Inclusion(substrate, inclusion, diameter)
            geometries.append(geometry)

        return geometries

GeometryPanelManager.register(Inclusion, InclusionPanel)

class MultiLayersPanel(_GeometryPanel):

    def __init__(self, parent):
        _GeometryPanel.__init__(self, parent)

        # Controls
        lbllayers = wx.StaticText(self, label='Layers')
        lbllayers.SetForegroundColour(wx.BLUE)
        self._lstlayers = LayersListCtrl(self, allow_empty=False)

        lblsubstrate = wx.StaticText(self, label='Substrate (optional)')
        lblsubstrate.SetForegroundColour(wx.BLUE)
        self._lstsubstrate = \
            MaterialListCtrl(self, name="substrate", allow_empty=True)

        # Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(lbllayers, 0)
        sizer.Add(self._lstlayers, 2, wx.EXPAND)
        sizer.Add(lblsubstrate, 0, wx.TOP, 20)
        sizer.Add(self._lstsubstrate, 1, wx.EXPAND)

        self.SetSizer(sizer)

        # Bind
        self.Bind(EVT_LIST_MATERIAL_ADDED, self.OnValueChanged, self._lstsubstrate)
        self.Bind(EVT_LIST_MATERIAL_DELETED, self.OnValueChanged, self._lstsubstrate)
        self.Bind(EVT_LIST_LAYER_ADDED, self.OnValueChanged, self._lstlayers)
        self.Bind(EVT_LIST_LAYER_DELETED, self.OnValueChanged, self._lstlayers)
        self.Bind(EVT_LIST_LAYER_MODIFIED, self.OnValueChanged, self._lstlayers)

    def get_geometries(self):
        layers_combs = []
        for materials, thicknesses in self._lstlayers.GetLayers():
            layers_combs.append(list(product(materials, thicknesses)))
        substrates = self._lstsubstrate.GetMaterials()
        if not substrates:
            substrates = [None]

        geometries = []

        for layers, substrate in product(product(*layers_combs), substrates):
            geometry = MultiLayers(substrate)
            for material, thickness in layers:
                geometry.add_layer(material, thickness * 1e-9)
            geometries.append(geometry)

        return geometries

GeometryPanelManager.register(MultiLayers, MultiLayersPanel)

class GrainBoundariesPanel(_GeometryPanel):

    def __init__(self, parent):
        _GeometryPanel.__init__(self, parent)

        # Controls
        lblleftmaterial = wx.StaticText(self, label='Left substrate')
        lblleftmaterial.SetForegroundColour(wx.BLUE)
        self._lstleftmaterial = \
            MaterialListCtrl(self, name="left substrate", allow_empty=False)

        lbllayers = wx.StaticText(self, label='Layers')
        lbllayers.SetForegroundColour(wx.BLUE)
        self._lstlayers = LayersListCtrl(self, allow_empty=True)

        lblrightmaterial = wx.StaticText(self, label='Right substrate')
        lblrightmaterial.SetForegroundColour(wx.BLUE)
        self._lstrightmaterial = \
            MaterialListCtrl(self, name="right substrate", allow_empty=False)

        # Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(lblleftmaterial, 0)
        sizer.Add(self._lstleftmaterial, 1, wx.EXPAND)
        sizer.Add(lbllayers, 0, wx.TOP, 5)
        sizer.Add(self._lstlayers, 1, wx.EXPAND)
        sizer.Add(lblrightmaterial, 0, wx.TOP, 5)
        sizer.Add(self._lstrightmaterial, 1, wx.EXPAND)

        self.SetSizer(sizer)

        # Bind
        self.Bind(EVT_LIST_MATERIAL_ADDED, self.OnValueChanged, self._lstleftmaterial)
        self.Bind(EVT_LIST_MATERIAL_DELETED, self.OnValueChanged, self._lstleftmaterial)
        self.Bind(EVT_LIST_LAYER_ADDED, self.OnValueChanged, self._lstlayers)
        self.Bind(EVT_LIST_LAYER_DELETED, self.OnValueChanged, self._lstlayers)
        self.Bind(EVT_LIST_LAYER_MODIFIED, self.OnValueChanged, self._lstlayers)
        self.Bind(EVT_LIST_MATERIAL_ADDED, self.OnValueChanged, self._lstrightmaterial)
        self.Bind(EVT_LIST_MATERIAL_DELETED, self.OnValueChanged, self._lstrightmaterial)

    def get_geometries(self):
        layers_combs = []
        for materials, thicknesses in self._lstlayers.GetLayers():
            layers_combs.append(list(product(materials, thicknesses)))
        if not layers_combs:
            layers_combs.append([(None, 0.0)])

        leftmaterials = self._lstleftmaterial.GetMaterials()
        rightmaterials = self._lstrightmaterial.GetMaterials()

        geometries = []

        for left_material, layers, right_material in \
                product(leftmaterials, product(*layers_combs), rightmaterials):
            geometry = GrainBoundaries(left_material, right_material)
            for material, thickness in layers:
                if material is None: continue
                geometry.add_layer(material, thickness * 1e-9)
            geometries.append(geometry)

        return geometries

GeometryPanelManager.register(GrainBoundaries, GrainBoundariesPanel)
