#!/usr/bin/env python
"""
================================================================================
:mod:`beam` -- Wizard page for beam definition
================================================================================

.. module:: beam
   :synopsis: Wizard page for beam definition

.. inheritance-diagram:: pymontecarlo.ui.gui.input.wizard.beam

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
from pymontecarlo.input.parameter import get_list

from pymontecarlo.util.manager import ClassManager
from pymontecarlo.util.human import camelcase_to_words

from pymontecarlo.ui.gui.input.wizard.page import WizardPage

# Globals and constants variables.
from pymontecarlo.input.particle import PARTICLES, ELECTRON

BeamPanelManager = ClassManager()

class BeamWizardPage(WizardPage):

    def __init__(self, wizard, options):
        WizardPage.__init__(self, wizard, 'Beam definition', options)

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
        self.Bind(wx.EVT_COMBOBOX, self.on_type, self._cbtype)

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

    def on_type(self, event):
        beam_class = self._cbtype.selection
        panel_class = BeamPanelManager.get(beam_class)

        oldpanel = self._panel
        panel = panel_class(self, self.options)

        self.Freeze()

        self._sizer.Replace(oldpanel, panel)
        panel.Show()

        oldpanel.Destroy()
        self._panel = panel

        self._sizer.Layout()
        self.Thaw()

class _BeamPanel(wx.Panel):
    
    def __init__(self, parent, options):
        wx.Panel.__init__(self, parent)

        # Variables
        self._options = options
        self._options.beam = self._init_beam(options.beam)
    
    def _init_beam(self, beam):
        return beam

    def on_value_changed(self, event=None):
        self.GetParent().on_value_changed(event)

    @property
    def beam(self):
        return self._options.beam

class PencilBeamPanel(_BeamPanel):

    def __init__(self, parent, options):
        _BeamPanel.__init__(self, parent, options)
        
        # Controls
        ## Particle
        lblparticle = wx.StaticText(self, label='Incident particle')
        self._cbparticle = PyComboBox(self)
        self._cbparticle.extend(PARTICLES)

        particle = self.beam.particle if hasattr(self.beam, 'particle') else ELECTRON
        self._cbparticle.selection = particle

        ## Energy
        lblenergy = wx.StaticText(self, label='Incident energy (keV)')
        lblenergy.SetForegroundColour(wx.BLUE)
        validator = FloatRangeTextValidator(range=(0.001, float('inf')))
        self._txtenergy = FloatRangeTextCtrl(self, name='incident energy',
                                             validator=validator)

        values = get_list(self.beam, 'energy_keV')
        self._txtenergy.SetValues(values)

        ## Origin
        boxorigin = wx.StaticBox(self, label="Start position (nm)")

        lblx = wx.StaticText(self, label='x')
        lblx.SetForegroundColour(wx.BLUE)
        self._txtx = FloatRangeTextCtrl(self, name='x position',
                                        validator=FloatRangeTextValidator())

        values = map(attrgetter('x'), get_list(self.beam, 'origin_nm'))
        self._txtx.SetValues(values)

        lbly = wx.StaticText(self, label='y')
        lbly.SetForegroundColour(wx.BLUE)
        self._txty = FloatRangeTextCtrl(self, name='y position',
                                        validator=FloatRangeTextValidator())

        values = map(attrgetter('y'), get_list(self.beam, 'origin_nm'))
        self._txty.SetValues(values)

        lblz = wx.StaticText(self, label='z')
        lblz.SetForegroundColour(wx.BLUE)
        self._txtz = FloatRangeTextCtrl(self, name='z position',
                                        validator=FloatRangeTextValidator())

        values = map(attrgetter('z'), get_list(self.beam, 'origin_nm'))
        self._txtz.SetValues(values)

        ## Direction
        boxdirection = wx.StaticBox(self, label='Direction')

        self._rdbvector = wx.RadioButton(self, label='Vector', style=wx.RB_GROUP)
        self._rdbangle = wx.RadioButton(self, label='Angle')
        self._rdbvector.SetValue(True)

        lblu = wx.StaticText(self, label='u')
        lblu.SetForegroundColour(wx.BLUE)
        self._txtu = FloatRangeTextCtrl(self, name='u direction',
                                        validator=FloatRangeTextValidator())

        values = map(attrgetter('x'), get_list(self.beam, 'direction'))
        self._txtu.SetValues(values)

        lblv = wx.StaticText(self, label='v')
        lblv.SetForegroundColour(wx.BLUE)
        self._txtv = FloatRangeTextCtrl(self, name='v direction',
                                        validator=FloatRangeTextValidator())

        values = map(attrgetter('y'), get_list(self.beam, 'direction'))
        self._txtv.SetValues(values)

        lblw = wx.StaticText(self, label='w')
        lblw.SetForegroundColour(wx.BLUE)
        self._txtw = FloatRangeTextCtrl(self, name='z direction',
                                        validator=FloatRangeTextValidator())

        values = map(attrgetter('z'), get_list(self.beam, 'direction'))
        self._txtw.SetValues(values)

        lblpolar = wx.StaticText(self, label=u'Inclination (\u00b0)')
        lblpolar.SetForegroundColour(wx.BLUE)
        validator = FloatRangeTextValidator(range=(0, 180))
        self._txtpolar = FloatRangeTextCtrl(self, name='inclination',
                                            validator=validator)
        self._txtpolar.Enable(False)

        # FIXME: Read default values
        self._txtpolar.SetValues([180.0])

        lblazimuth = wx.StaticText(self, label=u'Azimuth (\u00b0)')
        lblazimuth.SetForegroundColour(wx.BLUE)
        validator = FloatRangeTextValidator(range=(0, 360))
        self._txtazimuth = FloatRangeTextCtrl(self, name='azimuth',
                                              validator=validator)
        self._txtazimuth.Enable(False)

        # FIXME: Read default values
        self._txtazimuth.SetValues([0.0])

        ## Aperture
        lblaperture = wx.StaticText(self, label=u'Aperture (\u00b0)')
        lblaperture.SetForegroundColour(wx.BLUE)
        validator = FloatRangeTextValidator(range=(0, 90))
        self._txtaperture = FloatRangeTextCtrl(self, name='aperture',
                                               validator=validator)

        values = get_list(self.beam, 'aperture_deg')
        self._txtaperture.SetValues(values)

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
        self.Bind(wx.EVT_TEXT, self.on_value_changed, self._txtenergy)
        self.Bind(wx.EVT_TEXT, self.on_value_changed, self._txtx)
        self.Bind(wx.EVT_TEXT, self.on_value_changed, self._txty)
        self.Bind(wx.EVT_TEXT, self.on_value_changed, self._txtz)
        self.Bind(wx.EVT_TEXT, self.on_value_changed, self._txtu)
        self.Bind(wx.EVT_TEXT, self.on_value_changed, self._txtv)
        self.Bind(wx.EVT_TEXT, self.on_value_changed, self._txtw)
        self.Bind(wx.EVT_TEXT, self.on_value_changed, self._txtpolar)
        self.Bind(wx.EVT_TEXT, self.on_value_changed, self._txtazimuth)
        self.Bind(wx.EVT_TEXT, self.on_value_changed, self._txtaperture)

        self.Bind(wx.EVT_RADIOBUTTON, self.on_direction, self._rdbvector)
        self.Bind(wx.EVT_RADIOBUTTON, self.on_direction, self._rdbangle)

    def _init_beam(self, beam):
        if type(beam) is PencilBeam:
            return beam

        kwargs = {'energy_eV': 1e3}
        if hasattr(beam, 'energy_eV'): kwargs['energy_eV'] = beam.energy_eV
        if hasattr(beam, 'particle'): kwargs['particle'] = beam.particle
        if hasattr(beam, 'origin_m'): kwargs['origin_m'] = beam.origin_m
        if hasattr(beam, 'direction'): kwargs['direction'] = beam.direction
        if hasattr(beam, 'aperture_rad'): kwargs['aperture_rad'] = beam.aperture_rad

        return PencilBeam(**kwargs)

    def on_value_changed(self, event=None):
        # Particle
        self.beam.particle = self._cbparticle.selection

        # Energy
        try:
            self.beam.energy_keV = self._txtenergy.GetValues()
        except:
            pass
        
        # Origin
        try:
            xs = np.array(self._txtx.GetValues())
            ys = np.array(self._txty.GetValues())
            zs = np.array(self._txtz.GetValues())
            self.beam.origin_nm = list(product(xs, ys, zs))
        except:
            pass

        # Direction
        try:
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

            self.beam.direction = directions
        except:
            pass
        
        # Aperture
        try:
            self.beam.aperture_deg = self._txtaperture.GetValues()
        except:
            pass

        _BeamPanel.on_value_changed(self, event)

    def on_direction(self, event):
        self._txtu.Enable(self._rdbvector.GetValue())
        self._txtv.Enable(self._rdbvector.GetValue())
        self._txtw.Enable(self._rdbvector.GetValue())
        self._txtpolar.Enable(self._rdbangle.GetValue())
        self._txtazimuth.Enable(self._rdbangle.GetValue())

BeamPanelManager.register(PencilBeam, PencilBeamPanel)

class GaussianBeamPanel(PencilBeamPanel):

    def __init__(self, parent, options):
        PencilBeamPanel.__init__(self, parent, options)

        # Controls
        lbldiameter = wx.StaticText(self, label='Diameter (nm)')
        lbldiameter.SetForegroundColour(wx.BLUE)
        validator = FloatRangeTextValidator(range=(0.0, float('inf')))
        self._txtdiameter = FloatRangeTextCtrl(self, name='diameter',
                                               validator=validator)
        self._txtdiameter.MoveAfterInTabOrder(self._txtenergy)

        values = get_list(self.beam, 'diameter_nm')
        self._txtdiameter.SetValues(values)

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
        self.Bind(wx.EVT_TEXT, self.on_value_changed, self._txtdiameter)

    def _init_beam(self, beam):
        if type(beam) is GaussianBeam:
            return beam

        kwargs = {'energy_eV': 1e3, 'diameter_m': 10e-9}
        if hasattr(beam, 'energy_eV'): kwargs['energy_eV'] = beam.energy_eV
        if hasattr(beam, 'diameter_m'): kwargs['diameter_m'] = beam.diameter_m
        if hasattr(beam, 'particle'): kwargs['particle'] = beam.particle
        if hasattr(beam, 'origin_m'): kwargs['origin_m'] = beam.origin_m
        if hasattr(beam, 'direction'): kwargs['direction'] = beam.direction
        if hasattr(beam, 'aperture_rad'): kwargs['aperture_rad'] = beam.aperture_rad

        return GaussianBeam(**kwargs)

    def on_value_changed(self, event=None):
        PencilBeamPanel.on_value_changed(self, event)

        # Diameter
        try:
            self.beam.diameter_nm = self._txtdiameter.GetValues()
        except:
            pass

BeamPanelManager.register(GaussianBeam, GaussianBeamPanel)
