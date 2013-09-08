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
import copy
import warnings
from itertools import product
from operator import attrgetter

# Third party modules.
import wx
import numpy as np

# Local modules.
from wxtools2.combobox import PyComboBox
from wxtools2.floattext import FloatRangeTextCtrl, FloatRangeTextValidator

from pymontecarlo.input.geometry import \
    Substrate, Inclusion, MultiLayers, GrainBoundaries #, Sphere, ThinGrainBoundaries
from pymontecarlo.input.material import VACUUM
from pymontecarlo.input.parameter import get_list

from pymontecarlo.util.manager import ClassManager
from pymontecarlo.util.human import camelcase_to_words

from pymontecarlo.ui.gui.input.material import \
    MaterialListCtrl, EVT_LIST_MATERIAL_ADDED, EVT_LIST_MATERIAL_DELETED
from pymontecarlo.ui.gui.input.wizard.page import WizardPage
from pymontecarlo.ui.gui.input.body import \
    (LayersListCtrl, EVT_LIST_LAYER_ADDED, EVT_LIST_LAYER_DELETED,
     EVT_LIST_LAYER_MODIFIED)

# Globals and constants variables.

GeometryPanelManager = ClassManager()

class GeometryWizardPage(WizardPage):

    def __init__(self, wizard, options):
        WizardPage.__init__(self, wizard, 'Geometry definition', options)

        # Variables
        geometry = options.geometry

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

        values = get_list(geometry, 'tilt_deg')
        self._txttilt.SetValues(values)

        ## Rotation
        lblrotation = wx.StaticText(self, label=u'Rotation (\u00b0)')
        lblrotation.SetForegroundColour(wx.BLUE)
        validator = FloatRangeTextValidator(range=(-180.0, 180.0))
        self._txtrotation = FloatRangeTextCtrl(self, name='rotation',
                                               validator=validator)

        values = get_list(geometry, 'rotation_deg')
        self._txtrotation.SetValues(values)

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
        self.Bind(wx.EVT_COMBOBOX, self.on_type, self._cbtype)

        self.Bind(wx.EVT_TEXT, self.on_value_changed, self._txttilt)
        self.Bind(wx.EVT_TEXT, self.on_value_changed, self._txtrotation)

        # Add types
        for clasz in sorted(wizard.available_geometries, key=attrgetter('__name__')):
            try:
                GeometryPanelManager.get(clasz)
            except KeyError:
                warnings.warn("No panel for geometry %s" % clasz.__name__)
                continue
            self._cbtype.append(clasz)

        if not self._cbtype: # Empty
            raise ValueError, 'No geometry panel found'

        self._cbtype.selection = self._cbtype[0]

    def on_type(self, event):
        clasz = self._cbtype.selection
        panel_class = GeometryPanelManager.get(clasz)

        oldpanel = self._panel
        panel = panel_class(self, self.options)

        self.Freeze()

        self._sizer.Replace(oldpanel, panel)
        panel.Show()

        oldpanel.Destroy()
        self._panel = panel

        self._sizer.Layout()
        self.Thaw()

    def on_value_changed(self, event=None):
        geometry = self.options.geometry

        try:
            geometry.tilt_deg = self._txttilt.GetValues()
        except:
            pass

        try:
            geometry.rotation_deg = self._txtrotation.GetValues()
        except:
            pass

        WizardPage.on_value_changed(self, event)

class _GeometryPanel(wx.Panel):

    def __init__(self, parent, options):
        wx.Panel.__init__(self, parent)

        # Variables
        self._options = options
        self._options.geometry = self._init_geometry(options.geometry)

    def _init_geometry(self, geometry):
        return geometry

    def on_value_changed(self, event=None):
        self.GetParent().on_value_changed(event)

    @property
    def geometry(self):
        return self._options.geometry

class SubstratePanel(_GeometryPanel):

    def __init__(self, parent, options):
        _GeometryPanel.__init__(self, parent, options)

        # Controls
        self._lstmaterials = MaterialListCtrl(self)

        values = get_list(options.geometry, 'material')
        print values
        self._lstmaterials.materials = values

        # Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._lstmaterials, 1, wx.EXPAND)

        self.SetSizer(sizer)

        # Bind
        self.Bind(EVT_LIST_MATERIAL_ADDED, self.on_value_changed, self._lstmaterials)
        self.Bind(EVT_LIST_MATERIAL_DELETED, self.on_value_changed, self._lstmaterials)

    def _init_geometry(self, geometry):
        if type(geometry) is Substrate:
            return geometry

        return Substrate(VACUUM)

    def on_value_changed(self, event=None):
        self.geometry.material = self._lstmaterials.materials

        _GeometryPanel.on_value_changed(self, event)

GeometryPanelManager.register(Substrate, SubstratePanel)

#class InclusionPanel(_GeometryPanel):
#
#    def __init__(self, parent):
#        _GeometryPanel.__init__(self, parent)
#
#        # Controls
#        lbldiameter = wx.StaticText(self, label='Inclusion diameter (nm)')
#        lbldiameter.SetForegroundColour(wx.BLUE)
#        validator = FloatRangeTextValidator(range=(0.0001, float('inf')))
#        self._txtdiameter = FloatRangeTextCtrl(self, name='inclusion diameter',
#                                               validator=validator)
#        self._txtdiameter.SetValues([100.0])
#
#        lblsubstrate = wx.StaticText(self, label='Substrate')
#        lblsubstrate.SetForegroundColour(wx.BLUE)
#        self._lstsubstrate = MaterialListCtrl(self, name="susbstrate material")
#
#        lblinclusion = wx.StaticText(self, label='Inclusion')
#        lblinclusion.SetForegroundColour(wx.BLUE)
#        self._lstinclusion = MaterialListCtrl(self, name="inclusion material")
#
#        # Sizer
#        sizer = wx.BoxSizer(wx.VERTICAL)
#
#        szr_diameter = wx.BoxSizer(wx.HORIZONTAL)
#        sizer.Add(szr_diameter, 0, wx.EXPAND)
#        szr_diameter.Add(lbldiameter, 0, wx.ALIGN_CENTER_VERTICAL)
#        szr_diameter.Add(self._txtdiameter, 1, wx.GROW | wx.LEFT, 5)
#
#        sizer.Add(lblsubstrate, 0, wx.TOP, 20)
#        sizer.Add(self._lstsubstrate, 1, wx.EXPAND)
#        sizer.Add(lblinclusion, 0, wx.TOP, 20)
#        sizer.Add(self._lstinclusion, 1, wx.EXPAND)
#
#        self.SetSizer(sizer)
#
#        # Bind
#        self.Bind(wx.EVT_TEXT, self.OnValueChanged, self._txtdiameter)
#        self.Bind(EVT_LIST_MATERIAL_ADDED, self.OnValueChanged, self._lstsubstrate)
#        self.Bind(EVT_LIST_MATERIAL_DELETED, self.OnValueChanged, self._lstsubstrate)
#        self.Bind(EVT_LIST_MATERIAL_ADDED, self.OnValueChanged, self._lstinclusion)
#        self.Bind(EVT_LIST_MATERIAL_DELETED, self.OnValueChanged, self._lstinclusion)
#
#    def get_geometries(self):
#        diameters = np.array(self._txtdiameter.GetValues()) * 1e-9
#
#        geometries = []
#
#        for substrate, inclusion, diameter in \
#                product(self._lstsubstrate.GetMaterials(),
#                        self._lstinclusion.GetMaterials(),
#                        diameters):
#            geometry = Inclusion(substrate, inclusion, diameter)
#            geometries.append(geometry)
#
#        return geometries
#
#GeometryPanelManager.register(Inclusion, InclusionPanel)
#
#class MultiLayersPanel(_GeometryPanel):
#
#    def __init__(self, parent):
#        _GeometryPanel.__init__(self, parent)
#
#        # Controls
#        lbllayers = wx.StaticText(self, label='Layers')
#        lbllayers.SetForegroundColour(wx.BLUE)
#        self._lstlayers = LayersListCtrl(self, allow_empty=False)
#
#        lblsubstrate = wx.StaticText(self, label='Substrate (optional)')
#        lblsubstrate.SetForegroundColour(wx.BLUE)
#        self._lstsubstrate = \
#            MaterialListCtrl(self, name="substrate", allow_empty=True)
#
#        # Sizer
#        sizer = wx.BoxSizer(wx.VERTICAL)
#
#        sizer.Add(lbllayers, 0)
#        sizer.Add(self._lstlayers, 2, wx.EXPAND)
#        sizer.Add(lblsubstrate, 0, wx.TOP, 20)
#        sizer.Add(self._lstsubstrate, 1, wx.EXPAND)
#
#        self.SetSizer(sizer)
#
#        # Bind
#        self.Bind(EVT_LIST_MATERIAL_ADDED, self.OnValueChanged, self._lstsubstrate)
#        self.Bind(EVT_LIST_MATERIAL_DELETED, self.OnValueChanged, self._lstsubstrate)
#        self.Bind(EVT_LIST_LAYER_ADDED, self.OnValueChanged, self._lstlayers)
#        self.Bind(EVT_LIST_LAYER_DELETED, self.OnValueChanged, self._lstlayers)
#        self.Bind(EVT_LIST_LAYER_MODIFIED, self.OnValueChanged, self._lstlayers)
#
#    def get_geometries(self):
#        layers_combs = []
#        for materials, thicknesses in self._lstlayers.GetLayers():
#            layers_combs.append(list(product(materials, thicknesses)))
#        substrates = self._lstsubstrate.GetMaterials()
#        if not substrates:
#            substrates = [None]
#
#        geometries = []
#
#        for layers, substrate in product(product(*layers_combs), substrates):
#            geometry = MultiLayers(substrate)
#            for material, thickness in layers:
#                geometry.add_layer(material, thickness * 1e-9)
#            geometries.append(geometry)
#
#        return geometries
#
#GeometryPanelManager.register(MultiLayers, MultiLayersPanel)
#
#class GrainBoundariesPanel(_GeometryPanel):
#
#    def __init__(self, parent):
#        _GeometryPanel.__init__(self, parent)
#
#        # Controls
#        lblleftmaterial = wx.StaticText(self, label='Left substrate')
#        lblleftmaterial.SetForegroundColour(wx.BLUE)
#        self._lstleftmaterial = \
#            MaterialListCtrl(self, name="left substrate", allow_empty=False)
#
#        lbllayers = wx.StaticText(self, label='Layers')
#        lbllayers.SetForegroundColour(wx.BLUE)
#        self._lstlayers = LayersListCtrl(self, allow_empty=True)
#
#        lblrightmaterial = wx.StaticText(self, label='Right substrate')
#        lblrightmaterial.SetForegroundColour(wx.BLUE)
#        self._lstrightmaterial = \
#            MaterialListCtrl(self, name="right substrate", allow_empty=False)
#
#        # Sizer
#        sizer = wx.BoxSizer(wx.VERTICAL)
#
#        sizer.Add(lblleftmaterial, 0)
#        sizer.Add(self._lstleftmaterial, 1, wx.EXPAND)
#        sizer.Add(lbllayers, 0, wx.TOP, 5)
#        sizer.Add(self._lstlayers, 1, wx.EXPAND)
#        sizer.Add(lblrightmaterial, 0, wx.TOP, 5)
#        sizer.Add(self._lstrightmaterial, 1, wx.EXPAND)
#
#        self.SetSizer(sizer)
#
#        # Bind
#        self.Bind(EVT_LIST_MATERIAL_ADDED, self.OnValueChanged, self._lstleftmaterial)
#        self.Bind(EVT_LIST_MATERIAL_DELETED, self.OnValueChanged, self._lstleftmaterial)
#        self.Bind(EVT_LIST_LAYER_ADDED, self.OnValueChanged, self._lstlayers)
#        self.Bind(EVT_LIST_LAYER_DELETED, self.OnValueChanged, self._lstlayers)
#        self.Bind(EVT_LIST_LAYER_MODIFIED, self.OnValueChanged, self._lstlayers)
#        self.Bind(EVT_LIST_MATERIAL_ADDED, self.OnValueChanged, self._lstrightmaterial)
#        self.Bind(EVT_LIST_MATERIAL_DELETED, self.OnValueChanged, self._lstrightmaterial)
#
#    def get_geometries(self):
#        layers_combs = []
#        for materials, thicknesses in self._lstlayers.GetLayers():
#            layers_combs.append(list(product(materials, thicknesses)))
#        if not layers_combs:
#            layers_combs.append([(None, 0.0)])
#
#        leftmaterials = self._lstleftmaterial.GetMaterials()
#        rightmaterials = self._lstrightmaterial.GetMaterials()
#
#        geometries = []
#
#        for left_material, layers, right_material in \
#                product(leftmaterials, product(*layers_combs), rightmaterials):
#            geometry = GrainBoundaries(left_material, right_material)
#            for material, thickness in layers:
#                if material is None: continue
#                geometry.add_layer(material, thickness * 1e-9)
#            geometries.append(geometry)
#
#        return geometries
#
#GeometryPanelManager.register(GrainBoundaries, GrainBoundariesPanel)
