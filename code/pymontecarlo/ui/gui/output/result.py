#!/usr/bin/env python
"""
================================================================================
:mod:`result` -- Panels for results
================================================================================

.. module:: result
   :synopsis: Panels for results

.. inheritance-diagram:: pymontecarlo.ui.gui.panel.result

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
from wx.lib.scrolledpanel import ScrolledPanel
from wx.lib.embeddedimage import PyEmbeddedImage

from OpenGL import GL

import numpy as np

# Local modules.
from pymontecarlo.ui.gui.input.geometry import GeometryGLManager

from wxtools2.opengl import GLCanvas, GLCanvasToolbar
from wxtools2.floatspin import FloatSpin

# Globals and constants variables.
from pymontecarlo.output.result import \
    EXIT_STATE_ABSORBED, EXIT_STATE_BACKSCATTERED, EXIT_STATE_TRANSMITTED
from pymontecarlo.input.collision import \
    (HARD_ELASTIC, HARD_INELASTIC, HARD_BREMSSTRAHLUNG_EMISSION,
     INNERSHELL_IMPACT_IONISATION)

class _ResultPanel(ScrolledPanel):

    def __init__(self, parent, options, result):
        ScrolledPanel.__init__(self, parent)

        # Variables
        self._options = options
        self._result = result

    @property
    def options(self):
        return self._options

    @property
    def result(self):
        return self._result

class _TrajectoryParameters(object):

    def __init__(self, max_trajectories):
        self.max_trajectories = max_trajectories
        self.number_trajectories = max_trajectories

        self.primary_backscattered_enabled = True
        self.primary_backscattered_color = (1.0, 0.0, 0.0)
        self.primary_backscattered_width = 3.0

        self.primary_transmitted_enabled = True
        self.primary_transmitted_color = (0.0, 1.0, 0.0)
        self.primary_transmitted_width = 3.0

        self.primary_absorbed_enabled = True
        self.primary_absorbed_color = (0.0, 0.0, 1.0)
        self.primary_absorbed_width = 3.0

        self.secondary_backscattered_enabled = True
        self.secondary_backscattered_color = (0.0, 0.0, 0.5)
        self.secondary_backscattered_width = 3.0

        self.secondary_transmitted_enabled = True
        self.secondary_transmitted_color = (0.0, 0.0, 0.5)
        self.secondary_transmitted_width = 3.0

        self.secondary_absorbed_enabled = True
        self.secondary_absorbed_color = (0.0, 0.0, 0.5)
        self.secondary_absorbed_width = 3.0

        self.collision_hard_elastic_enabled = False
        self.collision_hard_elastic_color = (0.0, 0.0, 0.0)
        self.collision_hard_elastic_size = 3.0

        self.collision_hard_inelastic_enabled = False
        self.collision_hard_inelastic_color = (0.0, 0.0, 0.0)
        self.collision_hard_inelastic_size = 3.0

        self.collision_bremsstrahlung_enabled = False
        self.collision_bremsstrahlung_color = (0.0, 0.0, 0.0)
        self.collision_bremsstrahlung_size = 3.0

        self.collision_ionisation_enabled = False
        self.collision_ionisation_color = (0.0, 0.0, 0.0)
        self.collision_ionisation_size = 3.0

class _TrajectoryDialog(wx.Dialog):

    def __init__(self, parent, params):
        wx.Dialog.__init__(self, parent, title='Setup display options')

        # Controls
        # # Trajectories
        lbl_trajectories = wx.StaticText(self, label='Number of trajectories')

        self._sld_trajectories = wx.Slider(self)
        self._txt_trajectories = wx.StaticText(self)

        # # Primary
        box_primary = wx.StaticBox(self, label='Primary trajectories')

        self._chk_primary_backscattered = wx.CheckBox(self, label='Backscattered')
        self._btn_primary_backscattered = wx.Button(self, size=(40, -1))
        self._txt_primary_backscattered = FloatSpin(self, size=(40, -1),
                                                    min_val=1, max_val=100,
                                                    increment=1, digits=1)

        self._chk_primary_transmitted = wx.CheckBox(self, label='Transmitted')
        self._btn_primary_transmitted = wx.Button(self, size=(40, -1))
        self._txt_primary_transmitted = FloatSpin(self, size=(40, -1),
                                                  min_val=1, max_val=100,
                                                  increment=1, digits=1)

        self._chk_primary_absorbed = wx.CheckBox(self, label='Absorbed')
        self._btn_primary_absorbed = wx.Button(self, size=(40, -1))
        self._txt_primary_absorbed = FloatSpin(self, size=(40, -1),
                                               min_val=1, max_val=100,
                                               increment=1, digits=1)

        # # Secondary
        box_secondary = wx.StaticBox(self, label='Secondary trajectories')

        self._chk_secondary_backscattered = wx.CheckBox(self, label='Backscattered')
        self._btn_secondary_backscattered = wx.Button(self, size=(40, -1))
        self._txt_secondary_backscattered = FloatSpin(self, size=(40, -1),
                                                    min_val=1, max_val=100,
                                                    increment=1, digits=1)

        self._chk_secondary_transmitted = wx.CheckBox(self, label='Transmitted')
        self._btn_secondary_transmitted = wx.Button(self, size=(40, -1))
        self._txt_secondary_transmitted = FloatSpin(self, size=(40, -1),
                                                  min_val=1, max_val=100,
                                                  increment=1, digits=1)

        self._chk_secondary_absorbed = wx.CheckBox(self, label='Absorbed')
        self._btn_secondary_absorbed = wx.Button(self, size=(40, -1))
        self._txt_secondary_absorbed = FloatSpin(self, size=(40, -1),
                                               min_val=1, max_val=100,
                                               increment=1, digits=1)

        # # Collisions
        box_collision = wx.StaticBox(self, label='Collisions')

        self._chk_hard_elastic = wx.CheckBox(self, label='Hard elastic')
        self._btn_hard_elastic = wx.Button(self, size=(40, -1))
        self._txt_hard_elastic = FloatSpin(self, size=(40, -1),
                                             min_val=1, max_val=100,
                                             increment=1, digits=1)

        self._chk_hard_inelastic = wx.CheckBox(self, label='Hard inelastic')
        self._btn_hard_inelastic = wx.Button(self, size=(40, -1))
        self._txt_hard_inelastic = FloatSpin(self, size=(40, -1),
                                             min_val=1, max_val=100,
                                             increment=1, digits=1)

        self._chk_bremsstrahlung = wx.CheckBox(self, label='Bremsstrahlung emission')
        self._btn_bremsstrahlung = wx.Button(self, size=(40, -1))
        self._txt_bremsstrahlung = FloatSpin(self, size=(40, -1),
                                             min_val=1, max_val=100,
                                             increment=1, digits=1)

        self._chk_ionisation = wx.CheckBox(self, label='Inner shell impact ionisation')
        self._btn_ionisation = wx.Button(self, size=(40, -1))
        self._txt_ionisation = FloatSpin(self, size=(40, -1),
                                             min_val=1, max_val=100,
                                             increment=1, digits=1)

        # # Buttons
        btn_ok = wx.Button(self, wx.ID_OK)
        btn_cancel = wx.Button(self, wx.ID_CANCEL)
        btn_default = wx.Button(self, wx.ID_DEFAULT, label='Default')

        # Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        # # Number of trajectories
        szr_ntrajectories = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(szr_ntrajectories, 0, wx.GROW | wx.ALL, 5)

        szr_ntrajectories.Add(lbl_trajectories, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        szr_ntrajectories.Add(self._sld_trajectories, 1, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        szr_ntrajectories.Add(self._txt_trajectories, 0, wx.ALIGN_CENTER_VERTICAL)

        # # Trajectories
        szr_trajectories = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(szr_trajectories, 0, wx.GROW)

        # # Primary
        szr_primary = wx.StaticBoxSizer(box_primary, wx.VERTICAL)
        szr_trajectories.Add(szr_primary, 1, wx.GROW | wx.ALL, 5)

        szr_primary2 = wx.GridBagSizer(5, 4)
        szr_primary2.AddGrowableCol(0)
        szr_primary.Add(szr_primary2, 1, wx.GROW | wx.ALL, 5)

        szr_primary2.Add(self._chk_primary_backscattered, (0, 0), flag=wx.ALIGN_LEFT)
        szr_primary2.Add(self._btn_primary_backscattered, (0, 1), flag=wx.ALIGN_CENTER_HORIZONTAL)
        szr_primary2.Add(self._txt_primary_backscattered, (0, 2), flag=wx.ALIGN_CENTER_HORIZONTAL)

        szr_primary2.Add(self._chk_primary_transmitted, (1, 0), flag=wx.ALIGN_LEFT)
        szr_primary2.Add(self._btn_primary_transmitted, (1, 1), flag=wx.ALIGN_CENTER_HORIZONTAL)
        szr_primary2.Add(self._txt_primary_transmitted, (1, 2), flag=wx.ALIGN_CENTER_HORIZONTAL)

        szr_primary2.Add(self._chk_primary_absorbed, (2, 0), flag=wx.ALIGN_LEFT)
        szr_primary2.Add(self._btn_primary_absorbed, (2, 1), flag=wx.ALIGN_CENTER_HORIZONTAL)
        szr_primary2.Add(self._txt_primary_absorbed, (2, 2), flag=wx.ALIGN_CENTER_HORIZONTAL)

        # # Secondary
        szr_secondary = wx.StaticBoxSizer(box_secondary, wx.VERTICAL)
        szr_trajectories.Add(szr_secondary, 1, wx.GROW | wx.ALL, 5)

        szr_secondary2 = wx.GridBagSizer(5, 4)
        szr_secondary2.AddGrowableCol(0)
        szr_secondary.Add(szr_secondary2, 1, wx.GROW | wx.ALL, 5)

        szr_secondary2.Add(self._chk_secondary_backscattered, (0, 0), flag=wx.ALIGN_LEFT)
        szr_secondary2.Add(self._btn_secondary_backscattered, (0, 1), flag=wx.ALIGN_CENTER_HORIZONTAL)
        szr_secondary2.Add(self._txt_secondary_backscattered, (0, 2), flag=wx.ALIGN_CENTER_HORIZONTAL)

        szr_secondary2.Add(self._chk_secondary_transmitted, (1, 0), flag=wx.ALIGN_LEFT)
        szr_secondary2.Add(self._btn_secondary_transmitted, (1, 1), flag=wx.ALIGN_CENTER_HORIZONTAL)
        szr_secondary2.Add(self._txt_secondary_transmitted, (1, 2), flag=wx.ALIGN_CENTER_HORIZONTAL)

        szr_secondary2.Add(self._chk_secondary_absorbed, (2, 0), flag=wx.ALIGN_LEFT)
        szr_secondary2.Add(self._btn_secondary_absorbed, (2, 1), flag=wx.ALIGN_CENTER_HORIZONTAL)
        szr_secondary2.Add(self._txt_secondary_absorbed, (2, 2), flag=wx.ALIGN_CENTER_HORIZONTAL)

        # # Collisions
        szr_collision = wx.StaticBoxSizer(box_collision, wx.VERTICAL)
        sizer.Add(szr_collision, 0, wx.GROW | wx.ALL, 5)

        szr_collision2 = wx.GridBagSizer(5, 4)
        szr_collision2.AddGrowableCol(0)
        szr_collision2.AddGrowableCol(3)
        szr_collision.Add(szr_collision2, 0, wx.GROW | wx.ALL, 5)

        szr_collision2.Add(self._chk_hard_elastic, (0, 0), flag=wx.ALIGN_LEFT)
        szr_collision2.Add(self._btn_hard_elastic, (0, 1), flag=wx.ALIGN_CENTER_HORIZONTAL)
        szr_collision2.Add(self._txt_hard_elastic, (0, 2), flag=wx.ALIGN_CENTER_HORIZONTAL)

        szr_collision2.Add(self._chk_bremsstrahlung, (0, 3), flag=wx.ALIGN_LEFT)
        szr_collision2.Add(self._btn_bremsstrahlung, (0, 4), flag=wx.ALIGN_CENTER_HORIZONTAL)
        szr_collision2.Add(self._txt_bremsstrahlung, (0, 5), flag=wx.ALIGN_CENTER_HORIZONTAL)

        szr_collision2.Add(self._chk_hard_inelastic, (1, 0), flag=wx.ALIGN_LEFT)
        szr_collision2.Add(self._btn_hard_inelastic, (1, 1), flag=wx.ALIGN_CENTER_HORIZONTAL)
        szr_collision2.Add(self._txt_hard_inelastic, (1, 2), flag=wx.ALIGN_CENTER_HORIZONTAL)

        szr_collision2.Add(self._chk_ionisation, (1, 3), flag=wx.ALIGN_LEFT)
        szr_collision2.Add(self._btn_ionisation, (1, 4), flag=wx.ALIGN_CENTER_HORIZONTAL)
        szr_collision2.Add(self._txt_ionisation, (1, 5), flag=wx.ALIGN_CENTER_HORIZONTAL)

        # # Buttons
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(btn_default, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        sizer2.AddStretchSpacer()

        sizer3 = wx.StdDialogButtonSizer()
        sizer3.AddButton(btn_ok)
        sizer3.AddButton(btn_cancel)
        sizer3.AddButton(btn_default)
        sizer3.SetAffirmativeButton(btn_ok)
        sizer3.SetCancelButton(btn_cancel)
        sizer3.Realize()
        sizer2.Add(sizer3, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        sizer.Add(sizer2, 0, wx.GROW)

        self.SetSizer(sizer)
        self.Fit()

        # Bind
        self.Bind(wx.EVT_SCROLL, self.OnTrajectories, self._sld_trajectories)

        self.Bind(wx.EVT_BUTTON, self.OnColor, self._btn_primary_backscattered)
        self.Bind(wx.EVT_BUTTON, self.OnColor, self._btn_primary_transmitted)
        self.Bind(wx.EVT_BUTTON, self.OnColor, self._btn_primary_absorbed)

        self.Bind(wx.EVT_BUTTON, self.OnColor, self._btn_secondary_backscattered)
        self.Bind(wx.EVT_BUTTON, self.OnColor, self._btn_secondary_transmitted)
        self.Bind(wx.EVT_BUTTON, self.OnColor, self._btn_secondary_absorbed)

        self.Bind(wx.EVT_BUTTON, self.OnColor, self._btn_hard_elastic)
        self.Bind(wx.EVT_BUTTON, self.OnColor, self._btn_hard_inelastic)
        self.Bind(wx.EVT_BUTTON, self.OnColor, self._btn_bremsstrahlung)
        self.Bind(wx.EVT_BUTTON, self.OnColor, self._btn_ionisation)

        self.Bind(wx.EVT_BUTTON, self.OnDefault, btn_default)

        # Default
        self.SetParameters(params)

    def OnTrajectories(self, event):
        self._txt_trajectories.SetLabel(str(self._sld_trajectories.GetValue()))

    def OnColor(self, event):
        data = wx.ColourData()
        data.SetChooseFull(True)
        data.SetColour(event.GetEventObject().GetBackgroundColour())

        dialog = wx.ColourDialog(self, data)

        if dialog.ShowModal() == wx.ID_OK:
            color = dialog.GetColourData().GetColour()
            event.GetEventObject().SetBackgroundColour(color)

        dialog.Destroy()

    def OnDefault(self, event):
        params = _TrajectoryParameters(self._sld_trajectories.GetMax())
        self.SetParameters(params)

    def SetParameters(self, params):
        def _c(color):
            return wx.Color(color[0] * 255, color[1] * 255, color[2] * 255)

        self._sld_trajectories.SetRange(0, params.max_trajectories)
        self._sld_trajectories.SetValue(params.number_trajectories)
        self._txt_trajectories.SetLabel(str(params.number_trajectories))

        self._chk_primary_backscattered.SetValue(params.primary_backscattered_enabled)
        self._btn_primary_backscattered.SetBackgroundColour(_c(params.primary_backscattered_color))
        self._txt_primary_backscattered.SetValue(params.primary_backscattered_width)

        self._chk_primary_transmitted.SetValue(params.primary_transmitted_enabled)
        self._btn_primary_transmitted.SetBackgroundColour(_c(params.primary_transmitted_color))
        self._txt_primary_transmitted.SetValue(params.primary_transmitted_width)

        self._chk_primary_absorbed.SetValue(params.primary_absorbed_enabled)
        self._btn_primary_absorbed.SetBackgroundColour(_c(params.primary_absorbed_color))
        self._txt_primary_absorbed.SetValue(params.primary_absorbed_width)

        self._chk_secondary_backscattered.SetValue(params.secondary_backscattered_enabled)
        self._btn_secondary_backscattered.SetBackgroundColour(_c(params.secondary_backscattered_color))
        self._txt_secondary_backscattered.SetValue(params.secondary_backscattered_width)

        self._chk_secondary_transmitted.SetValue(params.secondary_transmitted_enabled)
        self._btn_secondary_transmitted.SetBackgroundColour(_c(params.secondary_transmitted_color))
        self._txt_secondary_transmitted.SetValue(params.secondary_transmitted_width)

        self._chk_secondary_absorbed.SetValue(params.secondary_absorbed_enabled)
        self._btn_secondary_absorbed.SetBackgroundColour(_c(params.secondary_absorbed_color))
        self._txt_secondary_absorbed.SetValue(params.secondary_absorbed_width)

        self._chk_hard_elastic.SetValue(params.collision_hard_elastic_enabled)
        self._btn_hard_elastic.SetBackgroundColour(_c(params.collision_hard_elastic_color))
        self._txt_hard_elastic.SetValue(params.collision_hard_elastic_size)

        self._chk_hard_inelastic.SetValue(params.collision_hard_inelastic_enabled)
        self._btn_hard_inelastic.SetBackgroundColour(_c(params.collision_hard_inelastic_color))
        self._txt_hard_inelastic.SetValue(params.collision_hard_inelastic_size)

        self._chk_bremsstrahlung.SetValue(params.collision_bremsstrahlung_enabled)
        self._btn_bremsstrahlung.SetBackgroundColour(_c(params.collision_bremsstrahlung_color))
        self._txt_bremsstrahlung.SetValue(params.collision_bremsstrahlung_size)

        self._chk_ionisation.SetValue(params.collision_ionisation_enabled)
        self._btn_ionisation.SetBackgroundColour(_c(params.collision_ionisation_color))
        self._txt_ionisation.SetValue(params.collision_ionisation_size)

    def GetParameters(self):
        def _c(color):
            r, g, b = color.Get(False)
            return r / 255.0, g / 255.0, b / 255.0

        params = _TrajectoryParameters(self._sld_trajectories.GetMax())

        params.number_trajectories = self._sld_trajectories.GetValue()

        params.primary_backscattered_enabled = self._chk_primary_backscattered.GetValue()
        params.primary_backscattered_color = _c(self._btn_primary_backscattered.GetBackgroundColour())
        params.primary_backscattered_width = float(self._txt_primary_backscattered.GetValue())

        params.primary_transmitted_enabled = self._chk_primary_transmitted.GetValue()
        params.primary_transmitted_color = _c(self._btn_primary_transmitted.GetBackgroundColour())
        params.primary_transmitted_width = float(self._txt_primary_transmitted.GetValue())

        params.primary_absorbed_enabled = self._chk_primary_absorbed.GetValue()
        params.primary_absorbed_color = _c(self._btn_primary_absorbed.GetBackgroundColour())
        params.primary_absorbed_width = float(self._txt_primary_absorbed.GetValue())

        params.secondary_backscattered_enabled = self._chk_secondary_backscattered.GetValue()
        params.secondary_backscattered_color = _c(self._btn_secondary_backscattered.GetBackgroundColour())
        params.secondary_backscattered_width = float(self._txt_secondary_backscattered.GetValue())

        params.secondary_transmitted_enabled = self._chk_secondary_transmitted.GetValue()
        params.secondary_transmitted_color = _c(self._btn_secondary_transmitted.GetBackgroundColour())
        params.secondary_transmitted_width = float(self._txt_secondary_transmitted.GetValue())

        params.secondary_absorbed_enabled = self._chk_secondary_absorbed.GetValue()
        params.secondary_absorbed_color = _c(self._btn_secondary_absorbed.GetBackgroundColour())
        params.secondary_absorbed_width = float(self._txt_secondary_absorbed.GetValue())

        params.collision_hard_elastic_enabled = self._chk_hard_elastic.GetValue()
        params.collision_hard_elastic_color = _c(self._btn_hard_elastic.GetBackgroundColour())
        params.collision_hard_elastic_size = float(self._txt_hard_elastic.GetValue())

        params.collision_hard_inelastic_enabled = self._chk_hard_inelastic.GetValue()
        params.collision_hard_inelastic_color = _c(self._btn_hard_inelastic.GetBackgroundColour())
        params.collision_hard_inelastic_size = float(self._txt_hard_inelastic.GetValue())

        params.collision_bremsstrahlung_enabled = self._chk_bremsstrahlung.GetValue()
        params.collision_bremsstrahlung_color = _c(self._btn_bremsstrahlung.GetBackgroundColour())
        params.collision_bremsstrahlung_size = float(self._txt_bremsstrahlung.GetValue())

        params.collision_ionisation_enabled = self._chk_ionisation.GetValue()
        params.collision_ionisation_color = _c(self._btn_ionisation.GetBackgroundColour())
        params.collision_ionisation_size = float(self._txt_ionisation.GetValue())

        return params

_ICON_OPTIONS = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlw"
    "SFlzAAABCgAAAQoBFqS8ywAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoA"
    "AAMFSURBVEiJrZVBSBxnFMd/365J1x2IGItIBhMQXUhrrcUUJFKZQy/xEuwhOaSQQI4BKYQc"
    "2ksuttBLofVSSE6SYnLKQgxiQqmJJCb2oMu23Q2io5mqg9i1TZOd7q7u66HflMnEuK7tgwfz"
    "3vu+//99//fNjBIR/keLA/lgIrJXJMdxDo2PjyenpqYuAKTT6ZMjIyNzMzMzA8F1NXslqK+v"
    "31xcXLSAY2trax9sbGy8t7S0dKizs7P0XwkiQHl1dbUhGo2+WF5eNl3XPe0Xs9nsuVgs9jyX"
    "y7V1dXV9qaqdwfT09OX5+fkzpVJJbNtOAMRiMZRSeJ4HQDQaRUTo7++/VPUJyuXyZi6Xa1xf"
    "X68DaG1t/cWyrIFCoRCbmJj4xnGclq2tLfr6+q60t7d/XfWQu7u7P7cs6ws/Nk3zlmma37e0"
    "tNxubm6+4+dra2sfAaU9DVlE3vSfPc97B9gPKM/zEn7etu0z8Xg8veMMlFKHgcNASkT+BJid"
    "nf10bGxssFgsRvQaEonET0qpSDabfQvAMIxyoVCI9PT0fFuJ4AZwCjgrIsMACwsLbXNzc4N1"
    "dXW/plKpj13XbQzuaWho+KO3t3fAMIxnxWLx55oQ4AXgvoiklVJvAF26dBwYVkop4ARwVUTu"
    "5vP5iOu6nzQ1NW0YhpG3bds0TTPV0dExHNQTfYqTgAAF4Drwm459fwI80M8vgIOTk5PfDQ0N"
    "Pc9kMpaIRJPJ5L3R0dGMiET/xQ0Q1AAPQ6Cv88/0vn2O41g+xsrKyhEROeDHLxFoksEQUBlY"
    "2YbgeHDfTh4EPwCsBUAeA0cBBXwI/B6o3QU6gH0VCYA2YEl3G+yyL7Twq21O8rQSQQSoBZp0"
    "p0HLh+JnodjT8u1sgQG/q0H97u4AB3W9DXADtR8AVdUMNNDVkAQe8OM28p3f7ZDDH7v9oTgG"
    "HNtGvo8qShOUSHffH+gww6sD/Qu4BRR13FPtNY0D14ATOn6bf66qAI+ARp1/H7hY9Xvwmjt8"
    "WRMM7hYw7JX+BzeBTSC5a81D9jedwJ/5I/IkFQAAAABJRU5ErkJggg==")

class _TrajectoryToolbar(GLCanvasToolbar):

    def __init__(self, canvas):
        GLCanvasToolbar.__init__(self, canvas)

        # Controls
        self._TOOL_OPTIONS = wx.NewId()
        self.AddSimpleTool(self._TOOL_OPTIONS, _ICON_OPTIONS.GetBitmap(),
                           'Setup display options')

        self.Realize()

        # Bind
        self.Bind(wx.EVT_TOOL, self.OnOptions, id=self._TOOL_OPTIONS)

    def OnOptions(self, event):
        params = self.canvas.GetParameters()
        dialog = _TrajectoryDialog(self.canvas.GetParent(), params)

        if dialog.ShowModal() == wx.ID_OK:
            self.canvas.SetParameters(dialog.GetParameters())

        dialog.Destroy()

class _TrajectoryGLCanvas(GLCanvas):

    def __init__(self, parent, options, result):
        GLCanvas.__init__(self, parent)

        # Variables
        self._result = result
        self._params = _TrajectoryParameters(len(result))  # default
        self._geometrygl = GeometryGLManager.get(options.geometry)
        self._glists = []

        # Customization
        self.SetBackgroundColour(wx.WHITE)

    def GetParameters(self):
        return self._params

    def SetParameters(self, params):
        self._params = params
        self.ResetGLBuffer()
        self.Refresh(False)

    def SetupGLView(self, width, height):
        GL.glViewport(0, 0, width, height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        ar = float(width) / height
        GL.glOrtho(-6.0 * ar, 6.0 * ar, -6.0, 6.0, -1e6, 1e6)

    def InitGL(self):
        GLCanvas.InitGL(self)

        GL.glEnable(GL.GL_BLEND);
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA);

        self._geometrygl.initgl()
        self.ResetGLBuffer()

    def ResetGLBuffer(self):
        # Clear existing lists
        for ilist in self._glists:
            GL.glDeleteLists(ilist, 1)

        self._glists = []

        # Create new lists
        for i, trajectory in enumerate(self._result):
            if i > self._params.number_trajectories: break

            # Trajectory
            color = None
            width = 0

            exit_state = trajectory.exit_state
            interactions = trajectory.interactions

            if trajectory.is_primary():
                if exit_state == EXIT_STATE_BACKSCATTERED and \
                        self._params.primary_backscattered_enabled:
                    color = self._params.primary_backscattered_color
                    width = self._params.primary_backscattered_width
                elif exit_state == EXIT_STATE_TRANSMITTED and \
                        self._params.primary_transmitted_enabled:
                    color = self._params.primary_transmitted_color
                    width = self._params.primary_transmitted_width
                elif exit_state == EXIT_STATE_ABSORBED and \
                        self._params.primary_absorbed_enabled:
                    color = self._params.primary_absorbed_color
                    width = self._params.primary_absorbed_width
            else:
                if exit_state == EXIT_STATE_BACKSCATTERED and \
                        self._params.secondary_backscattered_enabled:
                    color = self._params.secondary_backscattered_color
                    width = self._params.secondary_backscattered_width
                elif exit_state == EXIT_STATE_TRANSMITTED and \
                        self._params.secondary_transmitted_enabled:
                    color = self._params.secondary_transmitted_color
                    width = self._params.secondary_transmitted_width
                elif exit_state == EXIT_STATE_ABSORBED and \
                        self._params.secondary_absorbed_enabled:
                    color = self._params.secondary_absorbed_color
                    width = self._params.secondary_absorbed_width

            if color is None:
                continue

            ilist = self._CreateTrajectoryList(color, width, interactions)
            self._glists.append(ilist)

            # Collision
            if self._params.collision_hard_elastic_enabled:
                color = self._params.collision_hard_elastic_color
                size = self._params.collision_hard_elastic_size
                collision = HARD_ELASTIC
                ilist = self._CreateCollisionList(color, size, collision, interactions)
                self._glists.append(ilist)
            if self._params.collision_hard_inelastic_enabled:
                color = self._params.collision_hard_inelastic_color
                size = self._params.collision_hard_inelastic_size
                collision = HARD_INELASTIC
                ilist = self._CreateCollisionList(color, size, collision, interactions)
                self._glists.append(ilist)
            if self._params.collision_bremsstrahlung_enabled:
                color = self._params.collision_bremsstrahlung_color
                size = self._params.collision_bremsstrahlung_size
                collision = HARD_BREMSSTRAHLUNG_EMISSION
                ilist = self._CreateCollisionList(color, size, collision, interactions)
                self._glists.append(ilist)
            if self._params.collision_ionisation_enabled:
                color = self._params.collision_ionisation_color
                size = self._params.collision_ionisation_size
                collision = INNERSHELL_IMPACT_IONISATION
                ilist = self._CreateCollisionList(color, size, collision, interactions)
                self._glists.append(ilist)

    def _CreateTrajectoryList(self, color, width, interactions):
        ilist = GL.glGenLists(1)
        GL.glNewList(ilist, GL.GL_COMPILE)
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)

        GL.glColor(*color)
        GL.glLineWidth(width)

        vertices = np.ravel(interactions[1:, 0:3]) * 1e6
        GL.glVertexPointer(3, GL.GL_FLOAT, 0, vertices)
        GL.glDrawArrays(GL.GL_LINE_STRIP, 0, len(vertices) / 3)

        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEndList()

        return ilist

    def _CreateCollisionList(self, color, size, collision, interactions):
        cols = interactions[:, 4] == int(collision)
        vertices = np.ravel(interactions[cols][:, 0:3]) * 1e6

        ilist = GL.glGenLists(1)
        GL.glNewList(ilist, GL.GL_COMPILE)
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)

        GL.glColor(*color)
        GL.glPointSize(size)

        GL.glVertexPointer(3, GL.GL_FLOAT, 0, vertices)
        GL.glDrawArrays(GL.GL_POINTS, 0, len(vertices) / 3)

        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEndList()

        return ilist

    def DrawGLObjects(self):
        for ilist in self._glists:
            GL.glCallList(ilist)

        self._geometrygl.drawgl()

    def ResetGL(self):
        GLCanvas.ResetGL(self)
        GL.glScale(6, 6, 6)
        GL.glTranslate(0.0, 0.0, 0.5)
        GL.glRotate(5.0, 1.0, 0.0, 0.0)

class TrajectoryResultPanel(_ResultPanel):

    def __init__(self, parent, options, result):
        _ResultPanel.__init__(self, parent, options, result)

        # Controls
        self._canvas = _TrajectoryGLCanvas(self, options, result)
        self._canvas.SetSensitivityRotation(2.5)

        bottom_toolbar = _TrajectoryToolbar(self._canvas)

        # Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._canvas, 1, wx.EXPAND)
        sizer.Add(bottom_toolbar, 0, wx.GROW)

        self.SetSizer(sizer)

if __name__ == '__main__':  # pragma: no cover
    import math
    import DrixUtilities.Files as Files
    from zipfile import ZipFile
    from pymontecarlo.input.options import Options
    from pymontecarlo.input.geometry import \
        Substrate, Inclusion, MultiLayers, GrainBoundaries, Sphere
    from pymontecarlo.input.material import pure
    from pymontecarlo.output.result import TrajectoryResult

    results_zip = \
            Files.getCurrentModulePath(__file__, '../../../testdata/results.zip')
    zipfile = ZipFile(results_zip, 'r')
    result = TrajectoryResult.__loadzip__(zipfile, 'det6')

    options = Options(name="Test")

    options.geometry = Substrate(pure(8))

    options.geometry = Inclusion(pure(5), pure(6), 0.5e-6)

    options.geometry = MultiLayers(pure(5))
    options.geometry.add_layer(pure(6), 0.55e-6)
    options.geometry.add_layer(pure(6), 0.1e-6)

    options.geometry = GrainBoundaries(pure(8), pure(9))
    options.geometry.add_layer(pure(6), 0.55e-6)

    options.geometry = Sphere(pure(10), 0.75e-6)

    options.geometry.tilt_rad = math.radians(30)

    class __MainFrame(wx.Frame):

        def __init__(self, parent):
            wx.Frame.__init__(self, parent, title='Main frame')

            self.panel = TrajectoryResultPanel(self, options, result)

            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.panel, 1, wx.EXPAND)

            self.SetSizer(sizer)

    app = wx.PySimpleApp()

    mainframe = __MainFrame(None)
    mainframe.SetSizeWH(400, 400)
    mainframe.Show()

    app.MainLoop()
