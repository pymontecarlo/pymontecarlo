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
import warnings
from operator import attrgetter
from itertools import product

# Third party modules.
import wx

from pyxray.transition import get_transitions

# Local modules.
from pymontecarlo.input.limit import ShowersLimit, TimeLimit, UncertaintyLimit

from pymontecarlo.util.manager import ClassManager
from pymontecarlo.util.human import camelcase_to_words

from pymontecarlo.ui.gui.input.wizardpage import WizardPage

from wxtools2.combobox import PyComboBox
from wxtools2.list import \
    PyListCtrl, StaticColumn, PyListCtrlValidator, EVT_LIST_ROW_ACTIVATED
from wxtools2.checklistbox import PyCheckListBox, PyCheckListBoxValidator
from wxtools2.validator import form_validate
from wxtools2.dialog import show_exclamation_dialog
from wxtools2.floatspin import FloatSpin
from wxtools2.exception import catch_all

# Globals and constants variables.
from pymontecarlo.ui.gui.art import \
    ART_LIST_REMOVE, ART_LIST_CLEAR, ART_LIST_EDIT

LimitDialogManager = ClassManager()

class LimitWizardPage(WizardPage):

    def __init__(self, wizard):
        WizardPage.__init__(self, wizard, 'Limit(s) definition')

        # Controls
        ## Type
        lbltype = wx.StaticText(self, label='Type')
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD)
        lbltype.SetFont(font)
        getter = lambda t: camelcase_to_words(t.__name__)[:-5]
        self._cbtype = PyComboBox(self, getter)
        btnadd = wx.Button(self, label='Add')

        ## List
        c2 = lambda r: camelcase_to_words(r.__class__.__name__)[:-5]
        columns = [StaticColumn('Limit', c2, width= -3)]
        self._lstlimits = PyListCtrl(self, columns, name="limits")
        self._lstlimits.SetValidator(PyListCtrlValidator(allow_empty=False))

        ## Action buttons
        toolbar = wx.ToolBar(self)

        self._TOOL_REMOVE = wx.NewId()
        bitmap = wx.ArtProvider_GetBitmap(ART_LIST_REMOVE, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(self._TOOL_REMOVE, bitmap,
                              "Remove selected limit")

        self._TOOL_CLEAR = wx.NewId()
        bitmap = wx.ArtProvider_GetBitmap(ART_LIST_CLEAR, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(self._TOOL_CLEAR, bitmap, "Remove all limits")

        self._TOOL_EDIT = wx.NewId()
        bitmap = wx.ArtProvider_GetBitmap(ART_LIST_EDIT, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(self._TOOL_EDIT, bitmap, "Edit limit")

        toolbar.Realize()

        # Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        szr_type = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(szr_type, 0, wx.EXPAND | wx.ALL, 5)
        szr_type.Add(lbltype, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        szr_type.Add(self._cbtype, 1, wx.GROW | wx.RIGHT, 5)
        szr_type.Add(btnadd, 0)

        sizer.Add(self._lstlimits, 1, wx.EXPAND | wx.ALL, 5)

        sizer.Add(toolbar, 0, wx.ALIGN_RIGHT)

        self.SetSizer(sizer)

        # Bind
        self.Bind(wx.EVT_BUTTON, self.OnAdd, btnadd)
        self.Bind(wx.EVT_TOOL, self.OnRemove, id=self._TOOL_REMOVE)
        self.Bind(wx.EVT_TOOL, self.OnClear, id=self._TOOL_CLEAR)
        self.Bind(wx.EVT_TOOL, self.OnEdit, id=self._TOOL_EDIT)
        self.Bind(EVT_LIST_ROW_ACTIVATED, self.OnEdit, self._lstlimits)

        # Add types
        for clasz in sorted(wizard.available_limits, key=attrgetter('__name__')):
            try:
                LimitDialogManager.get(clasz)
            except KeyError:
                warnings.warn("No dialog for limit %s" % clasz.__name__)
                continue
            self._cbtype.append(clasz)

        if not self._cbtype:
            raise RuntimeError, "No limit available"

        self._cbtype.selection = self._cbtype[0]

    def OnAdd(self, event):
        clasz = self._cbtype.selection
        if clasz is None:
            return

        dialog_class = LimitDialogManager.get(clasz)

        dialog = dialog_class(self)
        if dialog.ShowModal() == wx.ID_OK:
            limit = dialog.GetLimit()
            self._lstlimits.append(limit)

        dialog.Destroy()

        self.OnValueChanged()

    def OnRemove(self, event):
        if not self._lstlimits: # No limits
            return

        if not self._lstlimits.selection:
            show_exclamation_dialog(self, "Please select a limit to delete")
            return

        limit = self._lstlimits.selection

        del self._lstlimits[self._lstlimits.index(limit)]

        self.OnValueChanged()

    def OnClear(self, event):
        self._lstlimits.clear()
        self.OnValueChanged()

    def OnEdit(self, event):
        if not self._lstlimits: # No limits
            return

        if not self._lstlimits.selection:
            show_exclamation_dialog(self, "Please select a limit to edit")
            return

        oldlimit = self._lstlimits.selection
        row = self._lstlimits.index(oldlimit)
        dialog_class = LimitDialogManager.get(oldlimit.__class__)

        dialog = dialog_class(self, oldlimit)
        if dialog.ShowModal() == wx.ID_OK:
            newlimit = dialog.GetLimit()
            self._lstlimits[row] = newlimit

        dialog.Destroy()

        self.OnValueChanged()

    def get_options(self):
        if not self._lstlimits:
            return [[]]

        groups = {}
        for limit in self._lstlimits:
            groups.setdefault(limit.__class__, []).append(limit)
        
        combs = []
        for limits in product(*groups.values()):
            combs.append(set(limits))

        return combs

class _LimitDialog(wx.Dialog):

    def __init__(self, parent, limit=None):
        wx.Dialog.__init__(self, parent)
        self.SetTitle(camelcase_to_words(self.__class__.__name__)[:-6])

        # Variables
        self._limit = limit

        # Controls
        btnok = wx.Button(self, wx.ID_OK)
        btnok.SetDefault()
        btncancel = wx.Button(self, wx.ID_CANCEL)

        # Sizer
        mainsizer = wx.BoxSizer(wx.VERTICAL)

        sizer = wx.GridBagSizer(5, 5)
        mainsizer.Add(sizer, 1, wx.EXPAND | wx.ALL, 5)
        sizer.AddGrowableCol(1)

        self._setup_layout(sizer, 0)

        szr_buttons = wx.StdDialogButtonSizer()
        mainsizer.Add(szr_buttons, 0, wx.GROW | wx.ALIGN_RIGHT)
        szr_buttons.AddButton(btnok)
        szr_buttons.AddButton(btncancel)
        szr_buttons.SetAffirmativeButton(btnok)
        szr_buttons.SetCancelButton(btncancel)
        szr_buttons.Realize()

        self.SetSizerAndFit(mainsizer)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_BUTTON, self.OnOk, id=wx.ID_OK)

        if limit is not None:
            self._load_limit(limit)

    def _setup_layout(self, sizer, row):
        return row

    def _load_limit(self, limit):
        pass

    def _create_limit(self):
        raise NotImplementedError

    def _modify_limit(self):
        pass

    def get_options(self):
        wizardpage = self.GetParent()
        wizard = wizardpage.GetParent()
        return wizard.get_options()

    def Validate(self):
        return form_validate(self)

    def OnClose(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnOk(self, event):
        if not self.Validate():
            event.StopPropagation()
        else:
            with catch_all(self) as success:
                if self._limit is None:
                    self._limit = self._create_limit()
                else:
                    self._modify_limit()

            if success:
                self.EndModal(wx.ID_OK)

    def GetLimit(self):
        return self._limit

class TimeLimitDialog(_LimitDialog):

    def _setup_layout(self, sizer, row):
        row = _LimitDialog._setup_layout(self, sizer, row)

        # Controls
        lbltime = wx.StaticText(self, label='Time')

        lblhour = wx.StaticText(self, label='h')
        self._txthour = FloatSpin(self, name='hour',
                                  value=0, min_val=0, increment=1, digits=0)

        lblminute = wx.StaticText(self, label='m')
        self._txtminute = FloatSpin(self, name='minute',
                                    value=0, min_val=0, increment=1, digits=0)

        lblsecond = wx.StaticText(self, label='s')
        self._txtsecond = FloatSpin(self, name='second',
                                    value=0, min_val=0, increment=1, digits=0)

        # Sizer
        sizer.Add(lbltime, pos=(row, 0), flag=wx.ALIGN_CENTER_VERTICAL)

        szr_time = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(szr_time, pos=(row, 1), flag=wx.GROW)
        szr_time.Add(self._txthour, 1, wx.GROW | wx.RIGHT, 2)
        szr_time.Add(lblhour, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 2)
        szr_time.Add(self._txtminute, 1, wx.GROW | wx.RIGHT, 2)
        szr_time.Add(lblminute, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 2)
        szr_time.Add(self._txtsecond, 1, wx.GROW | wx.RIGHT, 2)
        szr_time.Add(lblsecond, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 2)

        return row + 1

    def _load_limit(self, limit):
        time_s = limit.time_s
        hours = int(time_s) / 3600
        minutes = int(time_s) / 60 - hours * 60
        seconds = int(time_s) - minutes * 60 - hours * 3600

        self._txthour.SetValue(hours)
        self._txtminute.SetValue(minutes)
        self._txtsecond.SetValue(seconds)

    def _create_limit(self):
        time_s = self._txthour.GetValue() * 3600 + \
                    self._txtminute.GetValue() * 60 + \
                    self._txtsecond.GetValue()
        return TimeLimit(time_s)

    def _modify_limit(self):
        time_s = self._txthour.GetValue() * 3600 + \
                    self._txtminute.GetValue() * 60 + \
                    self._txtsecond.GetValue()
        self._limit.time_s = time_s

LimitDialogManager.register(TimeLimit, TimeLimitDialog)

class ShowersLimitDialog(_LimitDialog):

    def _setup_layout(self, sizer, row):
        row = _LimitDialog._setup_layout(self, sizer, row)

        # Controls
        lblshowers = wx.StaticText(self, label='# of trajectories')
        self._txtshowers = FloatSpin(self, name='trajectories',
                                     value=1000, min_val=1, increment=100, digits=0)

        # Sizer
        sizer.Add(lblshowers, pos=(row, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._txtshowers, pos=(row, 1), flag=wx.GROW)

        return row + 1

    def _load_limit(self, limit):
        showers = limit.showers
        self._txtshowers.SetValue(showers)

    def _create_limit(self):
        showers = self._txtshowers.GetValue()
        return ShowersLimit(showers)

    def _modify_limit(self):
        showers = self._txtshowers.GetValue()
        self._limit.showers = showers

LimitDialogManager.register(ShowersLimit, ShowersLimitDialog)

class UncertaintyLimitDialog(_LimitDialog):

    def _setup_layout(self, sizer, row):
        row = _LimitDialog._setup_layout(self, sizer, row)

        # Controls
        lbltransitions = wx.StaticText(self, label='Transitions')
        self._lsttransitions = PyCheckListBox(self, unicode, name='transitions')
        self._lsttransitions.SetValidator(PyCheckListBoxValidator(allow_empty=False))

        energyhigh_eV = max(map(attrgetter('beam.energy_eV'), self.get_options()))

        transitions = set()
        for geometry in map(attrgetter('geometry'), self.get_options()):
            materials = geometry.get_materials()
            for material in materials:
                energylow_eV = material.absorption_energy_electron_eV
                for z in material.composition.iterkeys():
                    transitions.update(get_transitions(z, energylow_eV, energyhigh_eV))

        transitions = sorted(transitions, key=attrgetter('probability'), reverse=True)
        self._lsttransitions.extend(transitions)

        lbluncertainty = wx.StaticText(self, label='Uncertainty limit (%)')
        self._txtuncertainty = \
            FloatSpin(self, name="uncertainty",
                      value=1, min_val=0.01, max_val=100.0, increment=1, digits=1)

        # Sizer
        sizer.Add(lbltransitions, pos=(row, 0), span=(1, 2))
        sizer.Add(self._lsttransitions, pos=(row + 1, 0), span=(1, 2), flag=wx.GROW)

        sizer.Add(lbluncertainty, pos=(row + 2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._txtuncertainty, pos=(row + 2, 1), flag=wx.GROW)

        return row + 3

    def _load_limit(self, limit):
        transitions = [t for t in limit.transitions if t in self._lsttransitions]
        self._lsttransitions.selection = transitions
        self._txtuncertainty.SetValue(limit.uncertainty * 100.0)

    def _create_limit(self):
        transitions = self._lsttransitions.selection
        uncertainty = self._txtuncertainty.GetValue() / 100.0
        return UncertaintyLimit(transitions, uncertainty)

    def _modify_limit(self):
        self._limit.transitions.clear()
        self._limit.transitions.update(self._lsttransitions.selection)
        self._limit.uncertainty = self._txtuncertainty.GetValue() / 100.0

LimitDialogManager.register(UncertaintyLimit, UncertaintyLimitDialog)
