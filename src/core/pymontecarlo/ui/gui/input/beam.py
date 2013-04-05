#!/usr/bin/env python
"""
================================================================================
:mod:`beam` -- Wizard page for beam definition
================================================================================

.. module:: beam
   :synopsis: Wizard page for beam definition

.. inheritance-diagram:: pymontecarlo.ui.gui.input.beam

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import warnings
from itertools import product
from operator import attrgetter

# Third party modules.
import wx
import numpy as np

# Local modules.
from wxtools2.combobox import PyComboBox
from wxtools2.floattext import FloatRangeTextCtrl, FloatRangeTextValidator

from pymontecarlo.input.beam import PencilBeam, GaussianBeam

from pymontecarlo.util.manager import ClassManager
from pymontecarlo.util.human import camelcase_to_words

from pymontecarlo.ui.gui.input.wizardpage import WizardPage

# Globals and constants variables.
from pymontecarlo.input.particle import PARTICLES, ELECTRON

BeamPanelManager = ClassManager()

class BeamWizardPage(WizardPage):

    def __init__(self, wizard):
        WizardPage.__init__(self, wizard, 'Beam definition')

        # Controls
        lbltype = wx.StaticText(self, label='Type')
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD)
        lbltype.SetFont(font)
        getter = lambda t: camelcase_to_words(t.__name__[:-4])
        self._cbtype = PyComboBox(self, getter)

        self._panel = wx.Panel(self)

        # Sizer
        self._sizer = wx.BoxSizer(wx.VERTICAL)

        szr_type = wx.BoxSizer(wx.HORIZONTAL)
        self._sizer.Add(szr_type, 0, wx.EXPAND | wx.ALL, 5)
        szr_type.Add(lbltype, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        szr_type.Add(self._cbtype, 1, wx.GROW)

        self._sizer.Add(self._panel, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(self._sizer)

        # Bind
        self.Bind(wx.EVT_COMBOBOX, self.OnType, self._cbtype)

        # Add types
        for clasz in sorted(wizard.available_beams, key=attrgetter('__name__')):
            try:
                BeamPanelManager.get(clasz)
            except KeyError:
                warnings.warn("No panel for beam %s" % clasz.__name__)
                continue
            self._cbtype.append(clasz)

        if not self._cbtype: # Empty
            raise ValueError, 'No beam panel found'

        self._cbtype.selection = self._cbtype[0]

    def OnType(self, event):
        beam_class = self._cbtype.selection
        panel_class = BeamPanelManager.get(beam_class)

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
        return self._panel.get_beams()

class PencilBeamPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Controls
        ## Particle
        lblparticle = wx.StaticText(self, label='Incident particle')
        self._cbparticle = PyComboBox(self)
        self._cbparticle.extend(PARTICLES)
        self._cbparticle.selection = ELECTRON

        ## Energy
        lblenergy = wx.StaticText(self, label='Incident energy (keV)')
        lblenergy.SetForegroundColour(wx.BLUE)
        validator = FloatRangeTextValidator(range=(0.001, float('inf')))
        self._txtenergy = FloatRangeTextCtrl(self, name='incident energy',
                                             validator=validator)
        self._txtenergy.SetValues([15.0])

        ## Origin
        boxorigin = wx.StaticBox(self, label="Start position (nm)")

        lblx = wx.StaticText(self, label='x')
        lblx.SetForegroundColour(wx.BLUE)
        self._txtx = FloatRangeTextCtrl(self, name='x position',
                                        validator=FloatRangeTextValidator())
        self._txtx.SetValues([0.0])

        lbly = wx.StaticText(self, label='y')
        lbly.SetForegroundColour(wx.BLUE)
        self._txty = FloatRangeTextCtrl(self, name='y position',
                                        validator=FloatRangeTextValidator())
        self._txty.SetValues([0.0])

        lblz = wx.StaticText(self, label='z')
        lblz.SetForegroundColour(wx.BLUE)
        self._txtz = FloatRangeTextCtrl(self, name='z position',
                                        validator=FloatRangeTextValidator())
        self._txtz.SetValues([1e9])

        ## Direction
        boxdirection = wx.StaticBox(self, label='Direction')

        self._rdbvector = wx.RadioButton(self, label='Vector', style=wx.RB_GROUP)
        self._rdbangle = wx.RadioButton(self, label='Angle')
        self._rdbvector.SetValue(True)

        lblu = wx.StaticText(self, label='u')
        lblu.SetForegroundColour(wx.BLUE)
        self._txtu = FloatRangeTextCtrl(self, name='u direction',
                                        validator=FloatRangeTextValidator())
        self._txtu.SetValues([0.0])

        lblv = wx.StaticText(self, label='v')
        lblv.SetForegroundColour(wx.BLUE)
        self._txtv = FloatRangeTextCtrl(self, name='v direction',
                                        validator=FloatRangeTextValidator())
        self._txtv.SetValues([0.0])

        lblw = wx.StaticText(self, label='w')
        lblw.SetForegroundColour(wx.BLUE)
        self._txtw = FloatRangeTextCtrl(self, name='z direction',
                                        validator=FloatRangeTextValidator())
        self._txtw.SetValues([-1])

        lblpolar = wx.StaticText(self, label=u'Inclination (\u00b0)')
        lblpolar.SetForegroundColour(wx.BLUE)
        validator = FloatRangeTextValidator(range=(0, 180))
        self._txtpolar = FloatRangeTextCtrl(self, name='inclination',
                                            validator=validator)
        self._txtpolar.SetValues([180.0])
        self._txtpolar.Enable(False)

        lblazimuth = wx.StaticText(self, label=u'Azimuth (\u00b0)')
        lblazimuth.SetForegroundColour(wx.BLUE)
        validator = FloatRangeTextValidator(range=(0, 360))
        self._txtazimuth = FloatRangeTextCtrl(self, name='azimuth',
                                              validator=validator)
        self._txtazimuth.SetValues([0.0])
        self._txtazimuth.Enable(False)

        ## Aperture
        lblaperture = wx.StaticText(self, label=u'Aperture (\u00b0)')
        lblaperture.SetForegroundColour(wx.BLUE)
        validator = FloatRangeTextValidator(range=(0, 90))
        self._txtaperture = FloatRangeTextCtrl(self, name='aperture',
                                               validator=validator)
        self._txtaperture.SetValues([0.0])

        # Sizer
        sizer = wx.GridBagSizer(5, 5)
        sizer.AddGrowableCol(1)

        sizer.Add(lblparticle, pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._cbparticle, pos=(0, 1), flag=wx.GROW)

        sizer.Add(lblenergy, pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._txtenergy, pos=(1, 1), flag=wx.GROW)

        szr_origin = wx.StaticBoxSizer(boxorigin, wx.HORIZONTAL)
        sizer.Add(szr_origin, pos=(2, 0), span=(1, 2), flag=wx.GROW)
        szr_origin.Add(lblx, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        szr_origin.Add(self._txtx, 1, wx.GROW | wx.TOP | wx.BOTTOM | wx.RIGHT, 5)
        szr_origin.Add(lbly, 0, wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.BOTTOM | wx.RIGHT, 5)
        szr_origin.Add(self._txty, 1, wx.GROW | wx.TOP | wx.BOTTOM | wx.RIGHT, 5)
        szr_origin.Add(lblz, 0, wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.BOTTOM | wx.RIGHT, 5)
        szr_origin.Add(self._txtz, 1, wx.GROW | wx.TOP | wx.BOTTOM | wx.RIGHT, 5)

        szr_direction = wx.StaticBoxSizer(boxdirection, wx.VERTICAL)
        sizer.Add(szr_direction, pos=(3, 0), span=(1, 2), flag=wx.GROW)

        szr_direction_radio = wx.BoxSizer(wx.HORIZONTAL)
        szr_direction.Add(szr_direction_radio, 0, wx.GROW)
        szr_direction.Add(self._rdbvector, 0)
        szr_direction.Add(self._rdbangle, 0)

        szr_direction_vector = wx.BoxSizer(wx.HORIZONTAL)
        szr_direction.Add(szr_direction_vector, 0, wx.GROW)
        szr_direction_vector.Add(lblu, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        szr_direction_vector.Add(self._txtu, 1, wx.GROW | wx.TOP | wx.BOTTOM | wx.RIGHT, 5)
        szr_direction_vector.Add(lblv, 0, wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.BOTTOM | wx.RIGHT, 5)
        szr_direction_vector.Add(self._txtv, 1, wx.GROW | wx.TOP | wx.BOTTOM | wx.RIGHT, 5)
        szr_direction_vector.Add(lblw, 0, wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.BOTTOM | wx.RIGHT, 5)
        szr_direction_vector.Add(self._txtw, 1, wx.GROW | wx.TOP | wx.BOTTOM | wx.RIGHT, 5)

        szr_direction_angle = wx.BoxSizer(wx.HORIZONTAL)
        szr_direction.Add(szr_direction_angle, 0, wx.GROW)
        szr_direction_angle.Add(lblpolar, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        szr_direction_angle.Add(self._txtpolar, 1, wx.GROW | wx.TOP | wx.BOTTOM | wx.RIGHT, 5)
        szr_direction_angle.Add(lblazimuth, 0, wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.BOTTOM | wx.RIGHT, 5)
        szr_direction_angle.Add(self._txtazimuth, 1, wx.GROW | wx.TOP | wx.BOTTOM | wx.RIGHT, 5)

        sizer.Add(lblaperture, pos=(4, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._txtaperture, pos=(4, 1), flag=wx.GROW)

        self.SetSizer(sizer)

        # Bind
        self.Bind(wx.EVT_TEXT, self.OnValueChanged, self._txtenergy)
        self.Bind(wx.EVT_TEXT, self.OnValueChanged, self._txtx)
        self.Bind(wx.EVT_TEXT, self.OnValueChanged, self._txty)
        self.Bind(wx.EVT_TEXT, self.OnValueChanged, self._txtz)
        self.Bind(wx.EVT_TEXT, self.OnValueChanged, self._txtu)
        self.Bind(wx.EVT_TEXT, self.OnValueChanged, self._txtv)
        self.Bind(wx.EVT_TEXT, self.OnValueChanged, self._txtw)
        self.Bind(wx.EVT_TEXT, self.OnValueChanged, self._txtpolar)
        self.Bind(wx.EVT_TEXT, self.OnValueChanged, self._txtazimuth)
        self.Bind(wx.EVT_TEXT, self.OnValueChanged, self._txtaperture)

        self.Bind(wx.EVT_RADIOBUTTON, self.OnDirection, self._rdbvector)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnDirection, self._rdbangle)

    def OnValueChanged(self, event):
        self.GetParent().OnValueChanged(event)

    def OnDirection(self, event):
        self._txtu.Enable(self._rdbvector.GetValue())
        self._txtv.Enable(self._rdbvector.GetValue())
        self._txtw.Enable(self._rdbvector.GetValue())
        self._txtpolar.Enable(self._rdbangle.GetValue())
        self._txtazimuth.Enable(self._rdbangle.GetValue())

    def get_beams(self):
        particle = self._cbparticle.selection
        energies = np.array(self._txtenergy.GetValues()) * 1e3
        xs = np.array(self._txtx.GetValues()) * 1e-9
        ys = np.array(self._txty.GetValues()) * 1e-9
        zs = np.array(self._txtz.GetValues()) * 1e-9

        if self._rdbvector.GetValue():
            us = self._txtu.GetValues()
            vs = self._txtv.GetValues()
            ws = self._txtw.GetValues()
            directions = list(product(us, vs, ws))
        else:
            polars = np.radians(self._txtpolar.GetValues())
            azimuths = np.radians(self._txtazimuth.GetValues())

            directions = []
            for polar, azimuth in product(polars, azimuths):
                u = np.sin(polar) * np.cos(azimuth)
                v = np.sin(polar) * np.sin(azimuth)
                w = np.cos(polar)
                directions.append((u, v, w))

        apertures = np.radians(self._txtaperture.GetValues())

        beams = []
        for energy, x, y, z, direction, aperture in \
                product(energies, xs, ys, zs, directions, apertures):
            beam = PencilBeam(energy, particle, (x , y , z), direction, aperture)
            beams.append(beam)

        return beams

BeamPanelManager.register(PencilBeam, PencilBeamPanel)

class GaussianBeamPanel(PencilBeamPanel):

    def __init__(self, parent):
        PencilBeamPanel.__init__(self, parent)

        # Controls
        lbldiameter = wx.StaticText(self, label='Diameter (nm)')
        lbldiameter.SetForegroundColour(wx.BLUE)
        validator = FloatRangeTextValidator(range=(0.0, float('inf')))
        self._txtdiameter = FloatRangeTextCtrl(self, name='diameter',
                                               validator=validator)
        self._txtdiameter.SetValues([10.0])
        self._txtdiameter.MoveAfterInTabOrder(self._txtenergy)

        # Sizer
        sizer = self.GetSizer()

        ## Shift everything after energy down 1
        for child in reversed(sizer.GetChildren()):
            pos = child.GetPos()
            if pos.GetRow() >= 2:
                pos.SetRow(pos.GetRow() + 1)
            child.SetPos(pos)

        sizer.Add(lbldiameter, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._txtdiameter, pos=(2, 1), flag=wx.GROW)

        # Bind
        self.Bind(wx.EVT_TEXT, self.OnValueChanged, self._txtdiameter)

    def get_beams(self):
        particle = self._cbparticle.selection
        energies = np.array(self._txtenergy.GetValues()) * 1e3
        diameters = np.array(self._txtdiameter.GetValues()) * 1e-9
        xs = np.array(self._txtx.GetValues()) * 1e-9
        ys = np.array(self._txty.GetValues()) * 1e-9
        zs = np.array(self._txtz.GetValues()) * 1e-9

        if self._rdbvector.GetValue():
            us = self._txtu.GetValues()
            vs = self._txtv.GetValues()
            ws = self._txtw.GetValues()
            directions = list(product(us, vs, ws))
        else:
            polars = np.radians(self._txtpolar.GetValues())
            azimuths = np.radians(self._txtazimuth.GetValues())

            directions = []
            for polar, azimuth in product(polars, azimuths):
                u = np.sin(polar) * np.cos(azimuth)
                v = np.sin(polar) * np.sin(azimuth)
                w = np.cos(polar)
                directions.append((u, v, w))

        apertures = np.radians(self._txtaperture.GetValues())

        beams = []
        for energy, diameter, x, y, z, direction, aperture in \
                product(energies, diameters, xs, ys, zs, directions, apertures):
            beam = GaussianBeam(energy, diameter, particle, (x , y , z),
                                direction, aperture)
            beams.append(beam)

        return beams

BeamPanelManager.register(GaussianBeam, GaussianBeamPanel)
