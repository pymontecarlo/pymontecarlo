#!/usr/bin/env python
"""
================================================================================
:mod:`wizard` -- New simulation(s) wizard
================================================================================

.. module:: wizard
   :synopsis: New simulation(s) wizard

.. inheritance-diagram:: pymontecarlo.ui.gui.input.wizard

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.
import wx

# Local modules.
from wxtools2.wizard import Wizard

from pymontecarlo.ui.gui.input.beam import BeamWizardPage

# Globals and constants variables.

class NewSimulationWizard(Wizard):

    def __init__(self, parent):
        Wizard.__init__(self, parent, 'New simulation(s)')
        self.SetSizeHints(500, 700)

        # Controls
        self._lblcount = wx.StaticText(self, label='1 simulation defined')
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.ITALIC, wx.FONTWEIGHT_NORMAL)
        self._lblcount.SetFont(font)

        # Sizer
        self._szr_buttons.Insert(0, self._lblcount, flag=wx.ALIGN_CENTER_VERTICAL)

        # Pages
        self.pages.append(BeamWizardPage(self))

    def SetSimulationCount(self, count):
        if count > 1:
            label = '%i simulations defined' % count
        else:
            label = '%i simulation defined' % count
        self._lblcount.SetLabel(label)

if __name__ == '__main__': #pragma: no cover
    app = wx.PySimpleApp()

    wiz = NewSimulationWizard(None)

    print wiz.ShowModal()

    wiz.Destroy()

    app.MainLoop()
