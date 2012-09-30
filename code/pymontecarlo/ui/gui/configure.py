#!/usr/bin/env python
"""
================================================================================
:mod:`configure` -- Dialog to configure settings
================================================================================

.. module:: configure
   :synopsis: Dialog to configure settings

.. inheritance-diagram:: pymontecarlo.ui.gui.configure

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
from operator import attrgetter

# Third party modules.
import wx

# Local modules.
from pymontecarlo import load_settings, load_program, get_program_gui, find_programs
from pymontecarlo.util.config import ConfigParser

from wxtools2.combobox import PyComboBox
from wxtools2.list import PyListCtrl, Column
from wxtools2.exception import catch_all
from wxtools2.dialog import show_exclamation_dialog

# Globals and constants variables.

class ConfigureDialog(wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent=parent, title='Configuration', size=(500, 300))

        # Variables
        self._filepath = os.path.join(os.path.expanduser('~'), '.pymontecarlo', 'settings.cfg')
        if os.path.exists(self._filepath):
            self._settings = load_settings([self._filepath])
        else:
            self._settings = ConfigParser() # Empty settings

        available_programs = sorted(find_programs())
        self._program_panels = {}

        # Controls
        ## Available programs
        lbl_available_programs = wx.StaticText(self, label='Available programs')

        self._cb_available_programs = PyComboBox(self)
        self._cb_available_programs.extend(available_programs)

        btn_activate = wx.Button(self, label='Activate')

        ## Selected programs
        columns = [Column("Selection", attrgetter('name'))]
        self._lst_selected_programs = PyListCtrl(self, columns,
                                                 multiple_selection=False)
        self._selected_panel = wx.Panel(self)

        btn_deactivate = wx.Button(self, label='Deactivate')

        ## Ok/Cancel
        btn_ok = wx.Button(self, label='Ok')
        btn_ok.SetDefault()
        btn_cancel = wx.Button(self, label='Cancel')

        # Sizer
        mainsizer = wx.BoxSizer(wx.VERTICAL)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(lbl_available_programs, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        sizer1.Add(self._cb_available_programs, 1, wx.EXPAND | wx.RIGHT, 10)
        sizer1.Add(btn_activate, 0)
        mainsizer.Add(sizer1, 0, wx.EXPAND | wx.BOTTOM, 10)

        self._szr_selection = wx.BoxSizer(wx.HORIZONTAL)
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        sizer2.Add(self._lst_selected_programs, 1, wx.EXPAND)
        sizer2.Add(btn_deactivate, 0, wx.EXPAND)
        self._szr_selection.Add(sizer2, 0, wx.EXPAND | wx.RIGHT, 5)
        self._szr_selection.Add(self._selected_panel, 1, wx.EXPAND)
        mainsizer.Add(self._szr_selection, 1, wx.EXPAND)

        sizer3 = wx.StdDialogButtonSizer()
        sizer3.AddButton(btn_ok)
        sizer3.AddButton(btn_cancel)
        sizer3.SetAffirmativeButton(btn_ok)
        sizer3.SetCancelButton(btn_cancel)
        sizer3.Realize()
        mainsizer.Add(sizer3, 0, wx.ALIGN_RIGHT)

        self.SetSizer(mainsizer)

        # Bind
        self.Bind(wx.EVT_BUTTON, self.OnActivate, btn_activate)
        self.Bind(wx.EVT_BUTTON, self.OnDeactivate, btn_deactivate)
        self.Bind(wx.EVT_BUTTON, self.OnOk, btn_ok)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, btn_cancel)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelection, self._lst_selected_programs)

        # Load settings
        if 'pymontecarlo' in self._settings:
            program_aliases = getattr(self._settings.pymontecarlo, 'programs', '').split(',')
            for program_alias in sorted(program_aliases):
                self.activate_program(program_alias)

    def activate_program(self, program_alias):
        with catch_all(self) as success:
            program = load_program(program_alias, validate=False)
            gui = get_program_gui(program)
        if not success:
            return

        panel = gui.create_configure_panel(self, self._settings)
        self._program_panels.setdefault(program, panel)

        self._lst_selected_programs.append(program)
        self._cb_available_programs.remove(program_alias)

        self._lst_selected_programs.selection = program

    def deactivate_program(self, program):
        self._lst_selected_programs.remove(program)
        self._program_panels.pop(program)
        self._cb_available_programs.append(program.alias)
        self._cb_available_programs.sort()

        del self._lst_selected_programs.selection
        self._select_panel(None) # Deselect

    def _select_panel(self, panel):
        if panel is None:
            panel = wx.Panel(self)

        self.Freeze()

        oldpanel = self._selected_panel
        oldpanel.Hide()

        self._szr_selection.Replace(oldpanel, panel)

        panel.Show()
        self._selected_panel = panel

        self._szr_selection.Layout()
        self.Thaw()

    def OnActivate(self, event):
        program_alias = self._cb_available_programs.selection
        if program_alias is None:
            return

        self.activate_program(program_alias)

    def OnDeactivate(self, event):
        if not self._lst_selected_programs:
            return

        program = self._lst_selected_programs.selection
        if not program:
            show_exclamation_dialog(self, "Select a program to deactivate", "Deactivate")
            return

        self.deactivate_program(program)

    def OnSelection(self, event):
        program = self._lst_selected_programs.selection
        panel = self._program_panels[program]

        self._select_panel(panel)

    def OnOk(self, event):
        # Save panel values in settings
        selected_programs = []

        for program, panel in self._program_panels.iteritems():
            if not panel.Validate():
                self._lst_selected_programs.selection = program
                return
            panel.save(self._settings)
            selected_programs.append(program.alias)

        # Save settings
        section = self._settings.add_section('pymontecarlo')
        section.programs = ','.join(selected_programs)

        dirname = os.path.dirname(self._filepath)
        if not os.path.exists(dirname):
            os.mkdir(dirname)

        with open(self._filepath, 'w') as fileobj:
            self._settings.write(fileobj)

        message = 'Configuration saved in %s' % self._filepath
        show_exclamation_dialog(self, message, 'Configuration')

        self.EndModal(wx.ID_OK)

    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)

if __name__ == '__main__':
    app = wx.PySimpleApp()

    dialog = ConfigureDialog(None)
    dialog.ShowModal()

    app.MainLoop()


