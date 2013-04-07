#!/usr/bin/env python
"""
================================================================================
:mod:`limit` -- Wizard page for limits
================================================================================

.. module:: limit
   :synopsis: Wizard page for limits

.. inheritance-diagram:: pymontecarlo.ui.gui.input.limit

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from operator import attrgetter
from itertools import product

# Third party modules.
import wx

# Local modules.
from pymontecarlo.ui.gui.input.wizardpage import WizardPage

from wxtools2.combobox import PyComboBox
from wxtools2.list import PyListCtrl, StaticColumn, PyListCtrlValidator
from wxtools2.dialog import show_exclamation_dialog

# Globals and constants variables.
from pymontecarlo.ui.gui.art import ART_LIST_REMOVE, ART_LIST_CLEAR

class ModelWizardPage(WizardPage):

    def __init__(self, wizard):
        WizardPage.__init__(self, wizard, 'Model(s) definition')

        # Variables
        self._available_models = wizard.available_models
        if not self._available_models:
            raise RuntimeError, "No model available"

        # Controls
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD)
        def titleattrgetter(attr):
            return lambda item: attrgetter(attr)(item).title()

        ## Model
        lbltype = wx.StaticText(self, label='Type')
        lbltype.SetFont(font)
        self._cbtype = PyComboBox(self, titleattrgetter('name'))
        self._cbtype.extend(sorted(self._available_models.keys()))
        self._cbtype.selection = self._cbtype[0]

        lblmodel = wx.StaticText(self, label='Model')
        lblmodel.SetFont(font)
        self._cbmodel = PyComboBox(self, attrgetter('name'))
        self._cbmodel.extend(sorted(self._available_models[self._cbtype[0]]))
        self._cbmodel.selection = self._cbmodel[0]

        btnadd = wx.Button(self, label='Add')

        ## List
        columns = [StaticColumn('Type', titleattrgetter('type.name'), width=200),
                   StaticColumn('Model', attrgetter('name'), width= -3)]
        self._lstmodels = PyListCtrl(self, columns, name="models")
        self._lstmodels.SetValidator(PyListCtrlValidator(allow_empty=True))

        ## Action buttons
        toolbar = wx.ToolBar(self)

        self._TOOL_REMOVE = wx.NewId()
        bitmap = wx.ArtProvider_GetBitmap(ART_LIST_REMOVE, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(self._TOOL_REMOVE, bitmap,
                              "Remove selected model")

        self._TOOL_CLEAR = wx.NewId()
        bitmap = wx.ArtProvider_GetBitmap(ART_LIST_CLEAR, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(self._TOOL_CLEAR, bitmap, "Remove all models")

        toolbar.Realize()

        ## Message
        lblmessage = \
            wx.StaticText(self, label='Default models are used if none is defined')
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.NORMAL)
        lblmessage.SetFont(font)

        # Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        szr_type = wx.GridBagSizer(5, 5)
        sizer.Add(szr_type, 0, wx.EXPAND | wx.ALL, 5)
        szr_type.AddGrowableCol(1)
        szr_type.Add(lbltype, pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        szr_type.Add(self._cbtype, pos=(0, 1), flag=wx.GROW)
        szr_type.Add(lblmodel, pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        szr_type.Add(self._cbmodel, pos=(1, 1), flag=wx.GROW)
        szr_type.Add(btnadd, pos=(1, 2))

        sizer.Add(self._lstmodels, 1, wx.EXPAND | wx.ALL, 5)

        sizer.Add(toolbar, 0, wx.ALIGN_RIGHT)

        sizer.Add(lblmessage, 0, wx.GROW | wx.ALL, 5)

        self.SetSizer(sizer)

        # Bind
        self.Bind(wx.EVT_BUTTON, self.OnAdd, btnadd)
        self.Bind(wx.EVT_TOOL, self.OnRemove, id=self._TOOL_REMOVE)
        self.Bind(wx.EVT_TOOL, self.OnClear, id=self._TOOL_CLEAR)
        self.Bind(wx.EVT_COMBOBOX, self.OnType, self._cbtype)

    def OnType(self, event):
        modeltype = self._cbtype.selection
        if modeltype is None:
            return

        models = sorted(self._available_models[modeltype])
        self._cbmodel.clear()
        self._cbmodel.extend(models)

        self._cbmodel.selection = self._cbmodel[0]

    def OnAdd(self, event):
        model = self._cbmodel.selection
        if model is None:
            return

        if model in self._lstmodels:
            show_exclamation_dialog(self, "Model already added", "Duplicate")
            return

        self._lstmodels.append(model)

        self.OnValueChanged()

    def OnRemove(self, event):
        if not self._lstmodels: # No models
            return

        if not self._lstmodels.selection:
            show_exclamation_dialog(self, "Please select a model to delete")
            return

        model = self._lstmodels.selection
        del self._lstmodels[self._lstmodels.index(model)]

        self.OnValueChanged()

    def OnClear(self, event):
        self._lstmodels.clear()
        self.OnValueChanged()

    def get_options(self):
        if not self._lstmodels:
            return [[]]

        groups = {}
        for model in self._lstmodels:
            groups.setdefault(model.type, []).append(model)

        combs = []
        for models in product(*groups.values()):
            combs.append(set(models))

        return combs

