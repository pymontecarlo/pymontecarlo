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

    def __init__(self, parent, programs):
        Wizard.__init__(self, parent, 'New simulation(s)')
        self.SetSizeHints(500, 700)

        # Variables
        self._available_beams = self._get_classes(programs, 'BEAMS')
        self._available_geometries = self._get_classes(programs, 'GEOMETRIES')
        self._available_detectors = self._get_classes(programs, 'DETECTORS')
        self._available_limits = self._get_classes(programs, 'LIMITS')

        # Controls
        self._lblcount = wx.StaticText(self, label='1 simulation defined')
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.ITALIC, wx.FONTWEIGHT_NORMAL)
        self._lblcount.SetFont(font)

        # Sizer
        self._szr_buttons.Insert(0, self._lblcount, flag=wx.ALIGN_CENTER_VERTICAL)

        # Pages
        self.pages.append(BeamWizardPage(self))

    def _get_classes(self, programs, attr):
        classes = set()

        for program in programs:
            converter = program.converter_class
            classes |= set(getattr(converter, attr))

        if not classes:
            raise ValueError, 'No %s classes found' % attr

        return classes

    @property
    def available_beams(self):
        return self._available_beams

    @property
    def available_geometries(self):
        return self._available_geometries

    @property
    def available_detectors(self):
        return self._available_detectors

    @property
    def available_limits(self):
        return self._available_limits

    def SetSimulationCount(self, count):
        if count > 1:
            label = '%i simulations defined' % count
        else:
            label = '%i simulation defined' % count
        self._lblcount.SetLabel(label)

if __name__ == '__main__': #pragma: no cover
    from pymontecarlo.program.nistmonte.config import program as nistmonte

    app = wx.PySimpleApp()

    programs = [nistmonte]
    wiz = NewSimulationWizard(None, programs)

    wiz.ShowModal()

    wiz.Destroy()

    app.MainLoop()
