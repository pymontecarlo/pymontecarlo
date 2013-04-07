#!/usr/bin/env python
"""
================================================================================
:mod:`verification` -- Wizard page to verify all options
================================================================================

.. module:: verification
   :synopsis: Wizard page to verify all options

.. inheritance-diagram:: pymontecarlo.ui.gui.verification

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import warnings

# Third party modules.
import wx

# Local modules.
from pymontecarlo.ui.gui.input.wizardpage import WizardPage

from wxtools2.list import PyListCtrl, StaticColumn
from wxtools2.dialog import show_error_dialog

# Globals and constants variables.

class VerificationWizardPage(WizardPage):

    def __init__(self, wizard):
        WizardPage.__init__(self, wizard, 'Verification')

        # Controls
        lblexceptions = wx.StaticText(self, label='Exception(s)')
        columns = [StaticColumn('Program', lambda r: r[0].name, width=150),
                   StaticColumn('Exception', lambda r: unicode(r[1]), width= -3)]
        self._lstexceptions = PyListCtrl(self, columns, name='exception')

        lblwarnings = wx.StaticText(self, label='Warning(s)')
        columns = [StaticColumn('Program', lambda r: r[0].name, width=150),
                   StaticColumn('Warning', lambda r: r[1].message, width= -3)]
        self._lstwarnings = PyListCtrl(self, columns, name='warning')

        # Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(lblexceptions, 0, wx.ALL, 5)
        sizer.Add(self._lstexceptions, 1, wx.EXPAND | wx.ALL, 5)

        sizer.Add(lblwarnings, 0, wx.ALL, 5)
        sizer.Add(self._lstwarnings, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(sizer)

    def Show(self, *args, **kwargs):
        self._lstexceptions.clear()
        self._lstwarnings.clear()

        wizard = self.GetParent()
        programs = wizard.programs

        for program in programs:
            converter = program.converter_class()

            for options in wizard.get_options():
                with warnings.catch_warnings(record=True) as ws:
                    warnings.simplefilter('always')

                    try:
                        converter.convert(options)
                    except Exception as ex:
                        self._lstexceptions.append((program, ex))

                for warning in ws:
                    self._lstwarnings.append((program, warning))

        return WizardPage.Show(self, *args, **kwargs)

    def Validate(self):
        if self._lstexceptions:
            show_error_dialog(self, "Please address the exception(s)")
            return False

        return True
