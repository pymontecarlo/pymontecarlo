#!/usr/bin/env python
"""
================================================================================
:mod:`options` -- New simulation(s) wizard
================================================================================

.. module:: options
   :synopsis: New simulation(s) wizard

.. inheritance-diagram:: pymontecarlo.ui.gui.input.wizard.options

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

from pymontecarlo.ui.gui.input.wizard.beam import BeamWizardPage
#from pymontecarlo.ui.gui.input.wizard.geometry import GeometryWizardPage
#from pymontecarlo.ui.gui.input.detector import DetectorWizardPage
#from pymontecarlo.ui.gui.input.limit import LimitWizardPage
#from pymontecarlo.ui.gui.input.model import ModelWizardPage
#from pymontecarlo.ui.gui.input.verification import VerificationWizardPage

from pymontecarlo.input.options import Options
from pymontecarlo.input.parameter import expand

# Globals and constants variables.

class OptionsWizard(Wizard):

    def __init__(self, parent, programs, options=None):
        Wizard.__init__(self, parent, 'New simulation(s)')
        self.SetSizeWH(500, 700)
        self.CenterOnParent()

        # Variables
        self._programs = programs

        self._available_beams = self._get_classes(programs, 'BEAMS')
        self._available_geometries = self._get_classes(programs, 'GEOMETRIES')
        self._available_detectors = self._get_classes(programs, 'DETECTORS')
        self._available_limits = self._get_classes(programs, 'LIMITS')

        self._available_models = {}
        for program in programs:
            converter = program.converter_class
            for modeltype, models in converter.MODELS.iteritems():
                self._available_models.setdefault(modeltype, set()).update(models)

        if options is None:
            options = Options()
        self._options = options

        # Controls
        self._lblcount = wx.StaticText(self, label='1 simulation defined')
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.ITALIC, wx.FONTWEIGHT_NORMAL)
        self._lblcount.SetFont(font)

        # Sizer
        self._szr_buttons.Insert(0, self._lblcount, flag=wx.ALIGN_CENTER_VERTICAL)

        # Pages
        self._page_beam = BeamWizardPage(self, options)
        self.pages.append(self._page_beam)

#        self._page_geometry = GeometryWizardPage(self, options)
#        self.pages.append(self._page_geometry)

#        self._page_detector = DetectorWizardPage(self)
#        self.pages.append(self._page_detector)
#
#        self._page_limit = LimitWizardPage(self)
#        self.pages.append(self._page_limit)
#
#        self._page_model = ModelWizardPage(self)
#        self.pages.append(self._page_model)
#
#        self._page_verification = VerificationWizardPage(self)
#        self.pages.append(self._page_verification)

    def _get_classes(self, programs, attr):
        classes = set()
        for program in programs:
            converter = program.converter_class
            classes |= set(getattr(converter, attr))
        return classes

    def OnPrev(self, event):
        Wizard.OnPrev(self, event)
        self.on_value_changed()

    def OnNext(self, event):
        Wizard.OnNext(self, event)
        self.on_value_changed()

    def on_value_changed(self, event=None):
        count = len(expand(self.options))

        if count > 1:
            label = '%i simulations defined' % count
        else:
            label = '%i simulation defined' % count
        self._lblcount.SetLabel(label)

    @property
    def programs(self):
        return self._programs

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

    @property
    def available_models(self):
        return self._available_models

    @property
    def options(self):
        return self._options

if __name__ == '__main__': #pragma: no cover
    from pymontecarlo.ui.gui.art import ArtProvider
    from pymontecarlo.program.nistmonte.config import program as nistmonte
    from pymontecarlo.program.penepma.config import program as penepma
    from pymontecarlo.program.casino2.config import program as casino2

    app = wx.PySimpleApp()
    wx.ArtProvider.Push(ArtProvider())

    programs = [nistmonte, penepma, casino2]
    wiz = OptionsWizard(None, programs)

    wiz.ShowModal()

    wiz.Destroy()

    app.MainLoop()