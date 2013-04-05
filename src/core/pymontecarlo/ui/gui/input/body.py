#!/usr/bin/env python
"""
================================================================================
:mod:`body` -- Layer list control and dialog
================================================================================

.. module:: body
   :synopsis: Layer list control and dialog

.. inheritance-diagram:: pymontecarlo.ui.gui.input.body

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from operator import attrgetter

# Third party modules.
import wx

# Local modules.
from wxtools2.list import \
    PyListCtrl, StaticColumn, PyListCtrlValidator, EVT_LIST_ROW_ACTIVATED
from wxtools2.floattext import FloatRangeTextCtrl, FloatRangeTextValidator
from wxtools2.dialog import show_exclamation_dialog
from wxtools2.validator import form_validate

from pymontecarlo.ui.gui.input.material import MaterialListCtrl

# Globals and constants variables.
from pymontecarlo.ui.gui.art import \
    ART_LIST_ADD, ART_LIST_REMOVE, ART_LIST_CLEAR, ART_LIST_EDIT

class LayerDialog(wx.Dialog):

    def __init__(self, parent, layer=None):
        """
        Creates a new layer dialog to create/edit layer.
        
        :arg parent: parent window
        :arg layer: layer to edit. ``None`` to create new.
        """
        wx.Dialog.__init__(self, parent, title='Layer')
        self.SetSizeHints(500, 250)

        # Variables
        self._layer = layer

        # Control
        self._lstmaterials = MaterialListCtrl(self)

        lblthickness = wx.StaticText(self, label='Thickness (nm)')
        lblthickness.SetForegroundColour(wx.BLUE)
        self._txtthickness = FloatRangeTextCtrl(self, name='thickness')
        validator = FloatRangeTextValidator(range=(0.0001, float('inf')))
        self._txtthickness.SetValidator(validator)
        self._txtthickness.SetValues([10.0])

        btnok = wx.Button(self, wx.ID_OK)
        btnok.SetDefault()
        btncancel = wx.Button(self, wx.ID_CANCEL)

        # Sizer
        sizer = wx.GridBagSizer(5, 5)
        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(0)

        sizer.Add(self._lstmaterials, pos=(0, 0), span=(1, 2), flag=wx.EXPAND)
        sizer.Add(lblthickness, pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._txtthickness, pos=(1, 1), flag=wx.GROW)

        szr_buttons = wx.StdDialogButtonSizer()
        sizer.Add(szr_buttons, pos=(2, 0), span=(1, 2), flag=wx.GROW)
        szr_buttons.AddButton(btnok)
        szr_buttons.AddButton(btncancel)
        szr_buttons.SetAffirmativeButton(btnok)
        szr_buttons.SetCancelButton(btncancel)
        szr_buttons.Realize()

        self.SetSizer(sizer)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_BUTTON, self.OnOk, id=wx.ID_OK)

        # Load layer
        if layer is not None:
            self._load_layer(layer)

    def _load_layer(self, layer):
        self._lstmaterials.SetMaterials(layer[0])
        self._txtthickness.SetValues(layer[1])

    def Validate(self):
        return form_validate(self)

    def OnClose(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnOk(self, event):
        if not self.Validate():
            event.StopPropagation()
        else:
            materials = self._lstmaterials.GetMaterials()
            thicknesses = self._txtthickness.GetValues()

            if self._layer is None:
                self._layer = [materials, thicknesses]
            else:
                self._layer[0] = materials
                self._layer[1] = thicknesses

            self.EndModal(wx.ID_OK)

    def GetLayer(self):
        """
        Returns the successfully created layer or the edited layer.
        """
        return self._layer

wxEVT_LIST_LAYER_DELETING = wx.NewEventType()
EVT_LIST_LAYER_DELETING = wx.PyEventBinder(wxEVT_LIST_LAYER_DELETING, 1)

wxEVT_LIST_LAYER_DELETED = wx.NewEventType()
EVT_LIST_LAYER_DELETED = wx.PyEventBinder(wxEVT_LIST_LAYER_DELETED, 1)

wxEVT_LIST_LAYER_ADDING = wx.NewEventType()
EVT_LIST_LAYER_ADDING = wx.PyEventBinder(wxEVT_LIST_LAYER_ADDING, 1)

wxEVT_LIST_LAYER_ADDED = wx.NewEventType()
EVT_LIST_LAYER_ADDED = wx.PyEventBinder(wxEVT_LIST_LAYER_ADDED, 1)

wxEVT_LIST_LAYER_MODIFYING = wx.NewEventType()
EVT_LIST_LAYER_MODIFYING = wx.PyEventBinder(wxEVT_LIST_LAYER_MODIFYING, 1)

wxEVT_LIST_LAYER_MODIFIED = wx.NewEventType()
EVT_LIST_LAYER_MODIFIED = wx.PyEventBinder(wxEVT_LIST_LAYER_MODIFIED, 1)

class LayerEvent(wx.PyCommandEvent):

    def __init__(self, eventType=wx.wxEVT_NULL, id=0, layer=None):
        wx.PyCommandEvent.__init__(self, eventType, id)
        self.Layer = layer

    def GetLayer(self):
        return self.Layer

class NotifyLayerEvent(LayerEvent, wx.NotifyEvent):

    def __init__(self, eventType=wx.wxEVT_NULL, id=0, layer=None):
        LayerEvent.__init__(self, eventType, id, layer)
        wx.NotifyEvent.__init__(self, eventType, id)

class LayersListCtrl(wx.Panel):

    def __init__(self, parent, allow_empty=False):
        wx.Panel.__init__(self, parent)

        # Controls
        ## List control
        fmaterial = lambda row: ', '.join(map(attrgetter('name'), row[0]))
        fthickness = lambda row: ', '.join(map(str, row[1]))
        columns = [StaticColumn('Material(s)', fmaterial, width=250),
                   StaticColumn('Thickness(es)', fthickness, width= -3)]
        self._lst = PyListCtrl(self, columns, name='layers')
        self._lst.SetValidator(PyListCtrlValidator(allow_empty))

        ## Action buttons
        toolbar = wx.ToolBar(self)

        self._TOOL_ADD = wx.NewId()
        bitmap = wx.ArtProvider_GetBitmap(ART_LIST_ADD, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(self._TOOL_ADD, bitmap, "Add material")

        self._TOOL_REMOVE = wx.NewId()
        bitmap = wx.ArtProvider_GetBitmap(ART_LIST_REMOVE, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(self._TOOL_REMOVE, bitmap,
                              "Remove selected material")

        self._TOOL_CLEAR = wx.NewId()
        bitmap = wx.ArtProvider_GetBitmap(ART_LIST_CLEAR, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(self._TOOL_CLEAR, bitmap, "Remove all materials")

        self._TOOL_EDIT = wx.NewId()
        bitmap = wx.ArtProvider_GetBitmap(ART_LIST_EDIT, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(self._TOOL_EDIT, bitmap, "Edit material")

        toolbar.Realize()

        # Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(self._lst, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(toolbar, 0, wx.ALIGN_RIGHT)

        self.SetSizer(sizer)

        # Bind
        self.Bind(wx.EVT_TOOL, self.OnAdd, id=self._TOOL_ADD)
        self.Bind(wx.EVT_TOOL, self.OnRemove, id=self._TOOL_REMOVE)
        self.Bind(wx.EVT_TOOL, self.OnClear, id=self._TOOL_CLEAR)
        self.Bind(wx.EVT_TOOL, self.OnEdit, id=self._TOOL_EDIT)
        self.Bind(EVT_LIST_ROW_ACTIVATED, self.OnEdit, self._lst)

    def OnAdd(self, event):
        dialog = LayerDialog(self.GetParent())

        if dialog.ShowModal() == wx.ID_OK:
            layer = dialog.GetLayer()

            event = NotifyLayerEvent(wxEVT_LIST_LAYER_ADDING,
                                     self.GetId(), layer)
            if self.GetEventHandler().ProcessEvent(event) and \
                    not event.IsAllowed():
                dialog.Destroy()
                return # Veto

            index = 0
            if self._lst.selection is not None:
                index = self._lst.index(self._lst.selection)
            self._lst.insert(index, layer)

            event = LayerEvent(wxEVT_LIST_LAYER_ADDED, self.GetId(), layer)
            self.GetEventHandler().ProcessEvent(event)

        dialog.Destroy()

    def _dellayer(self, layer):
        event = NotifyLayerEvent(wxEVT_LIST_LAYER_DELETING, self.GetId(),
                                 layer)
        if self.GetEventHandler().ProcessEvent(event) and not event.IsAllowed():
            return # Veto

        del self._lst[self._lst.index(layer)]

        event = LayerEvent(wxEVT_LIST_LAYER_DELETED, self.GetId(), layer)
        self.GetEventHandler().ProcessEvent(event)

    def OnRemove(self, event):
        if not self._lst: # No layers
            return

        if not self._lst.selection:
            show_exclamation_dialog(self, "Please select a layer to delete")
            return

        self._dellayer(self._lst.selection)

    def OnClear(self, event):
        for layer in list(self._lst):
            self._dellayer(layer)

    def OnEdit(self, event):
        if not self._lst: # No layers
            return

        if not self._lst.selection:
            show_exclamation_dialog(self, "Please select a layer to edit")
            return

        layer = self._lst.selection

        event = NotifyLayerEvent(wxEVT_LIST_LAYER_MODIFYING, self.GetId(),
                                 layer)
        if self.GetEventHandler().ProcessEvent(event) and not event.IsAllowed():
            return # Veto

        dialog = LayerDialog(self.GetParent(), layer)

        if dialog.ShowModal() == wx.ID_OK:
            layer = dialog.GetLayer()
            self._lst[self._lst.index(layer)] = layer # update

        dialog.Destroy()

        event = LayerEvent(wxEVT_LIST_LAYER_MODIFIED, self.GetId(), layer)
        self.GetEventHandler().ProcessEvent(event)

    def GetLayers(self):
        return list(self._lst) # copy
