#!/usr/bin/env python
"""
================================================================================
:mod:`result` -- Panels for results
================================================================================

.. module:: result
   :synopsis: Panels for results

.. inheritance-diagram:: pymontecarlo.ui.gui.output.result

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import csv
import re
from operator import itemgetter
import bisect

# Third party modules.
import wx
from wx.lib.embeddedimage import PyEmbeddedImage
from wx.grid import Grid

from OpenGL import GL
from OpenGL import GLUT

import numpy as np

import xlwt

from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg

# Local modules.
from pymontecarlo.output.result import \
    (PhotonIntensityResult, TrajectoryResult, TimeResult, ElectronFractionResult,
     PhotonSpectrumResult)
from pymontecarlo.ui.gui.input.geometry import GeometryGLManager
from pymontecarlo.ui.gui.output.manager import ResultPanelManager
import pymontecarlo.util.physics as physics
from pymontecarlo.util.human import human_time

from wxtools2.wxopengl import GLCanvas, GLCanvasToolbar
from wxtools2.floatspin import FloatSpin
from wxtools2.combobox import PyComboBox
from wxtools2.dialog import show_save_filedialog
from wxtools2.wxmatplotlib import NavigationToolbarWx, StatusBarWx

# Globals and constants variables.
from pymontecarlo.output.result import \
    EXIT_STATE_ABSORBED, EXIT_STATE_BACKSCATTERED, EXIT_STATE_TRANSMITTED
from pymontecarlo.input.collision import \
    (HARD_ELASTIC, HARD_INELASTIC, HARD_BREMSSTRAHLUNG_EMISSION,
     INNERSHELL_IMPACT_IONISATION)

_REGEX_CAMEL_CASE = re.compile('([a-z0-9])([A-Z])')

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

_ICON_SAVE = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlw"
    "SFlzAAACXwAAAl8BvoUoWgAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoA"
    "AAPcSURBVEjHtVbNax1VFP+dc+/kq0mapEVrW6UopWirRWkiFkGwoOAH6MIKxS5040b82IlY"
    "lfoXCC4El0VFFDe66E6oi6JkUbWkVWxrpTE1TdrYNPa9zDnn52Lee5nGJijqwGVm7sycc38f"
    "554Rkvg/jwwAA/vf2AvgLoIqkI0EqqwEAUbrXdZGLLsnAAoQJH8AEKJ6eP7QwbPS/8yBd0ju"
    "pEdDwKGXrnw5umPbGpBADZyQAVIAEp1psnoP1ZK+PhN4X+6+JIAU/X3zqSgeygDGdvYn3bp+"
    "3S2fnJyc6usbjMG1N0qVgEIRgCQgIFjNt/GAVVIBGETP5Aw3C+Tx0e29X4yfTBdUX8ggu7Zv"
    "umH45b0Pb/n01Xdn5594caFnx23m5lqaq5mJmambS+mubqYWgfCAh1dnD3gYxhunZXhyKr+y"
    "79GeoxOnbdoxnAnI58fP/PzVxHtznnIoBOEh7i7ujlNTF9KvM3OJpJChCEdQwIgWjQ6S2DDU"
    "TxXiu+nLV7c9+2aDuUD3+hFkADIXevWSs1SRESHFPMSC4uFyZPz7rh+/PZ7btLTVbwvRVmRs"
    "96irIKhKkyJEVQEwgxQGC5CJKllEWqs3CQ95as/uZvnAaGmlaxku4Y6IipYIg0cgnBAQkyfO"
    "CaQSq25TJaMAmUBkYYi7ibvDw+XDw0d6Jo4dTx03dYy1hAIA7rt/l6kgAEHtATMIQbAgmURR"
    "QLTNv7i57Bm7s7znjlsjAhIM0APBaGkQiAgygMHegrNnZypL1Qutsh4Lkkoi/9Fs6sUrDZqZ"
    "hrvklGR4TR+DZEWNV7SQaNMVHlh0hwWlqrcKbZsiYUQBUqO08qMjxxZASpAJoEZQK7+jTk6n"
    "CllTP0CAncpvaUAIyQxSEYbfpmcvkchgZAYzlmP+53sRBREFCQWYSCYEE/nvg4MtkUlmEgpS"
    "wU7w/2Y3JdCuAyWoIBQAUrhKxN9DIIClwv8yuVRoUSynY6s0Bu/ddbs2Gk2x5iIoQM6ZJCvn"
    "1MZPp37RE2lkZqV+INfjuru7Sx575EF+/MFn6Zuj4wkA9j/3dLnp5o1hZQkzg5mhLEtMX5wL"
    "LFxn/QB1NeTmDsaS68wcbgZ3h5nDWtdYpSuumsDNELWPrw1snWus0nVXTCACmhkYtQTm1wR2"
    "twrlKhlUVIoVEbgjaoVZIVgKbGbwFRCIqkLQzKL6Vs/agbcbv8/nZUUiZoaNmzfQzF0U6O3r"
    "YT1wmzLp9P1K2lQU2j00cFZTOiAk0b/v9dcY8TxJa281N12+sG6wK+Ugq5bcOi8bJCmLzUWc"
    "37BlEiLV34XqOU3pyflDBxf+BCkUDvQPQayTAAAAAElFTkSuQmCC")

_ICON_COPY = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlw"
    "SFlzAAAG7AAABuwBHnU4NQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoA"
    "AAAPdEVYdFRpdGxlAEVkaXQgQ29weaFFjiAAAAAWdEVYdEF1dGhvcgBBbmRyZWFzIE5pbHNz"
    "b24r7+SjAAAAGHRFWHRDcmVhdGlvbiBUaW1lADIwMDUtMTAtMTUNlAdXAAAASXRFWHRDb3B5"
    "cmlnaHQAUHVibGljIERvbWFpbiBodHRwOi8vY3JlYXRpdmVjb21tb25zLm9yZy9saWNlbnNl"
    "cy9wdWJsaWNkb21haW4vWcP+ygAAAsNJREFUSImdlj1v01AUht9jX7d2BQy10zQL4mNA3Ri7"
    "AUvFQMU/oGJiKgIkBsSMGNg6MYHKP+AnsKEiBkANatUyNqWJ2yRu0/jrHgbH13YaN6RXim6O"
    "7vH7nPfc6w9ae79WnTHMRRARJh3M3Av7X1efrP4tSxEzhrm48ujx7TiOJtbXdYH1Tx8B4HMp"
    "AEQUxxH6/f7EANM0Mc65NrHqYDAzmAFAnpsnJhcGAM7m8/WLgGazCdd1VdzxOs9vXr8xPepC"
    "Ig1HbeDunXty989OOLy+u7PTXVq6f7UAqFQqqFQqKnZdd9q2bXOcqws7cBz7QqJJ+0YA8g6Y"
    "GYeHhxcQ50J8xkGr1VKJc3OFdv2XsGVZsCwL4BEAx3Fg2w7SU9JuH6m1OI5LhAsRpOSCC5Em"
    "MTMODppw3ZY64/PzcypR1/XSqrN7InHAzKmB1EFCdRwbjmMrYLfbGekgKzADZCAurAlAKsFm"
    "s4VWq6kEarXqGQdZtQxmGgglTwvbns3BEoJgCUgpwcywbXuQlAh4nqcAUZQ6yAOGZ1ZxGAYy"
    "tweZi7zl/H9NI9UeIoCZkD7m0hzXdWFZFkzTRBTFrADpzucBmqbl+s2IY1la/XBhU1NTiJML"
    "UoAs2BNCwDAMJB1KD4AzFmAYBoQQEEJAygFAxlH7568fx8ySwcmWMTM00rhWq3G6qcNV5mdd"
    "11VRKaDTbWtv372p0PCtnR/1+qZbrVZny9qhaZoS/PZ9Q7k4Pvawtb3lP1t9YZ77PgjCUBaP"
    "ZTYPVxwGIS5fuoJOp4O9xj4T0Re1B2UjCgM5XHXajjyAiOAHPgLXRaOxh7Z3tLn84OHyWEAQ"
    "BlLXdTAziAhCCOi6rn5CCASBD8/rorG/x73e6anv99cZ/HTh1kI0FlD/Xf+wtb19jZCcfSIN"
    "RGAigmQJKSVkLBFGoXnSO/H9IFh59fJ14fPkH+Ui+1O1qExzAAAAAElFTkSuQmCC")

class _ResultPanel(wx.Panel):

    def __init__(self, parent, options, key, result):
        wx.Panel.__init__(self, parent)

        # Variables
        self._options = options
        self._key = key
        self._result = result

        # Controls and sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        lbl_key = wx.StaticText(self, label=key)
        lbl_key.SetFont(font)

        font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL)
        label = self.result.__class__.__name__[:-6]
        label = _REGEX_CAMEL_CASE.sub(r'\1 \2', label)
        lbl_class = wx.StaticText(self, label=label)
        lbl_class.SetFont(font)

        szr_title = wx.BoxSizer(wx.HORIZONTAL)
        szr_title.Add(lbl_key, 0)
        szr_title.AddStretchSpacer()
        szr_title.Add(lbl_class, 0, wx.ALIGN_RIGHT)
        sizer.Add(szr_title, 0, wx.GROW | wx.ALL, 5)

        self._init_panel(sizer)

        self._init_toolbar(sizer)

        self.SetSizer(sizer)

    def _init_panel(self, sizer):
        raise NotImplementedError

    def _init_toolbar(self, sizer):
        pass

    @property
    def options(self):
        return self._options

    @property
    def key(self):
        return self._key

    @property
    def result(self):
        return self._result

class UnknownResultPanel(_ResultPanel):

    def _init_panel(self, sizer):
        # Controls
        label = wx.StaticText(self, label='No viewer for this result')

        # Sizer
        sizer.Add(label, 0, wx.LEFT, 10)

class _SaveableResultPanel(_ResultPanel):

    def __init__(self, parent, options, key, result):
        _ResultPanel.__init__(self, parent, options, key, result)

        self._save_filetypes = []
        self._save_methods = {}

        self._register_save_method('csv', 'CSV file', self._save_csv)
        self._register_save_method('xls', 'Excel file', self._save_xls)
        self._register_save_method('ods', 'Open document file', self._save_xls)

    def _init_toolbar(self, sizer):
        # Controls
        toolbar = wx.ToolBar(self)

        self._TB_COPY = wx.NewId()
        toolbar.AddSimpleTool(self._TB_COPY, _ICON_COPY.GetBitmap(),
                              "Copy results to clipboard")

        self._TB_SAVE = wx.NewId()
        toolbar.AddSimpleTool(self._TB_SAVE, _ICON_SAVE.GetBitmap(),
                              "Save results to file")

        toolbar.Realize()

        # Sizer
        sizer.Add(toolbar, 0, wx.GROW)

        # Bind
        self.Bind(wx.EVT_TOOL, self.copy, id=self._TB_COPY)
        self.Bind(wx.EVT_TOOL, self.save, id=self._TB_SAVE)

        return toolbar

    def _register_save_method(self, ext, ext_name, method):
        filetype = ('%s (*.%s)' % (ext_name, ext), ext)
        self._save_filetypes.append(filetype)
        self._save_methods[ext] = method

    def dump(self):
        """
        Dumps the result in a tabular format.
        Returns a :class:`list` of :class`list`.
        """
        raise NotImplementedError

    def copy(self, *args):
        text = ''
        for row in self.dump():
            text += '\t'.join([str(item) for item in row]) + os.linesep

        clipdata = wx.TextDataObject()
        clipdata.SetText(text)
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipdata)
        wx.TheClipboard.Close()

    def save(self, *args):
        filepath = show_save_filedialog(self, self._save_filetypes)
        if not filepath:
            return

        ext = os.path.splitext(filepath)[1][1:]
        method = self._save_methods.get(ext)
        print method
        if method is not None:
            method(filepath)

    def _save_csv(self, filepath):
        with open(filepath, 'w') as fp:
            writer = csv.writer(fp)
            writer.writerows(self.dump())

    def _save_xls(self, filepath):
        book = xlwt.Workbook(encoding='utf-8')
        sheet = book.add_sheet(self.key)

        for irow, row in enumerate(self.dump()):
            for icol, value in enumerate(row):
                sheet.write(irow, icol, value)

        book.save(filepath)

class _TrajectoryResultParameters(object):

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

        self.show_trajectories = True
        self.show_geometry = True
        self.show_scalebar = True

class _TrajectoryResultDialog(wx.Dialog):

    def __init__(self, parent, params):
        wx.Dialog.__init__(self, parent, title='Setup display options')

        # Controls
        ## Trajectories
        lbl_trajectories = wx.StaticText(self, label='Number of trajectories')

        self._sld_trajectories = wx.Slider(self)
        self._txt_trajectories = wx.StaticText(self)

        ## Visibility
        box_visibility = wx.StaticBox(self, label='Visibility')

        self._chk_show_trajectories = wx.CheckBox(self, label='Trajectories')
        self._chk_show_geometry = wx.CheckBox(self, label='Geometry')
        self._chk_show_scalebar = wx.CheckBox(self, label='Scale bar')

        ## Primary
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

        ## Secondary
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

        ## Collisions
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

        ## Buttons
        btn_ok = wx.Button(self, wx.ID_OK)
        btn_cancel = wx.Button(self, wx.ID_CANCEL)
        btn_default = wx.Button(self, wx.ID_DEFAULT, label='Default')

        # Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        ## Number of trajectories
        szr_ntrajectories = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(szr_ntrajectories, 0, wx.GROW | wx.ALL, 5)

        szr_ntrajectories.Add(lbl_trajectories, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        szr_ntrajectories.Add(self._sld_trajectories, 1, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        szr_ntrajectories.Add(self._txt_trajectories, 0, wx.ALIGN_CENTER_VERTICAL)

        ## Visiblity
        szr_visibilty = wx.StaticBoxSizer(box_visibility, wx.HORIZONTAL)
        sizer.Add(szr_visibilty, 0, wx.GROW | wx.ALL, 5)

        szr_visibilty.Add(self._chk_show_trajectories, 0, wx.ALL, 5)
        szr_visibilty.Add(self._chk_show_geometry, 0, wx.ALL, 5)
        szr_visibilty.Add(self._chk_show_scalebar, 0, wx.ALL, 5)

        ## Trajectories
        szr_trajectories = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(szr_trajectories, 0, wx.GROW)

        ## Primary
        szr_primary = wx.StaticBoxSizer(box_primary, wx.VERTICAL)
        szr_trajectories.Add(szr_primary, 1, wx.GROW | wx.ALL, 5)

        szr_primary2 = wx.GridBagSizer(5, 5)
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

        ## Secondary
        szr_secondary = wx.StaticBoxSizer(box_secondary, wx.VERTICAL)
        szr_trajectories.Add(szr_secondary, 1, wx.GROW | wx.ALL, 5)

        szr_secondary2 = wx.GridBagSizer(5, 5)
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

        ## Collisions
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

        ## Buttons
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(btn_default, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        sizer2.AddStretchSpacer()

        sizer3 = wx.StdDialogButtonSizer()
        sizer3.AddButton(btn_ok)
        sizer3.AddButton(btn_cancel)
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
        params = _TrajectoryResultParameters(self._sld_trajectories.GetMax())
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

        self._chk_show_trajectories.SetValue(params.show_trajectories)
        self._chk_show_geometry.SetValue(params.show_geometry)
        self._chk_show_scalebar.SetValue(params.show_scalebar)

    def GetParameters(self):
        def _c(color):
            r, g, b = color.Get(False)
            return r / 255.0, g / 255.0, b / 255.0

        params = _TrajectoryResultParameters(self._sld_trajectories.GetMax())

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

        params.show_trajectories = self._chk_show_trajectories.GetValue()
        params.show_geometry = self._chk_show_geometry.GetValue()
        params.show_scalebar = self._chk_show_scalebar.GetValue()

        return params

def _calculate_scale_bar(value, unit, length,
                            preferred_values=[1, 2, 5, 10, 20, 50, 100, 200, 500]):
    """
    
    """
    UNITS = {'ym': 1e-24, 'zm': 1e-21, 'am': 1e-18, 'fm': 1e-15, 'pm': 1e-12,
             'nm': 1e-9, 'um': 1e-6, 'mm': 1e-3, 'm': 1.0, 'km': 1e3, 'Mm': 1e6,
             'Gm': 1e9, 'Tm': 1e12, 'Pm': 1e15, 'Em': 1e18, 'Zm': 1e21, 'Ym': 1e24}

    if unit not in UNITS:
        raise ValueError, 'Unknown unit %s' % unit

    # Convert to meters
    value_m = value * UNITS[unit]

    # Find best units and adjust value
    unit2, factor = \
        sorted([(unit, mag) for unit, mag in UNITS.iteritems() if mag <= value_m],
               key=itemgetter(1))[-1]
    value2 = value_m / factor

    # Find preferred units and adjust value
    index = bisect.bisect_right(preferred_values, value2) - 1
    value3 = float(preferred_values[index])

    # New length
    length2 = value3 / value2 * length

    return value3, unit2, length2

class _TrajectoryResultGLCanvas(GLCanvas):

    def __init__(self, parent, options, result):
        GLCanvas.__init__(self, parent)

        # Variables
        self._result = result
        self._params = _TrajectoryResultParameters(len(result)) # default
        self._geometrygl = GeometryGLManager.get(options.geometry.__class__)(options.geometry)
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
        GLUT.glutInit()
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

        # Create trajectory lists
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
        # Trajectories
        if self._params.show_trajectories:
            for ilist in self._glists:
                GL.glCallList(ilist)

        # Geometry
        if self._params.show_geometry:
            self._geometrygl.drawgl()

        # Scale bar
        if self._params.show_scalebar:
            length = 3.0
            scale = length / self.GetScaling() # um
            new_scale, new_unit, new_length = _calculate_scale_bar(scale, 'um', length)

            width, height = self.GetClientSizeTuple()
            x0 = -6.0 * width / height + 0.5
            y0 = -6.0 + 0.5

            GL.glPushMatrix()
            GL.glLoadIdentity()

            GL.glColor(0.0, 0.0, 0.0)
            GL.glRectd(x0, y0 + 0.5, x0 + new_length, y0 + 0.6)

            GL.glRasterPos2f(x0, y0);
            GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18,
                                  '%s %s' % (new_scale, new_unit))

            GL.glPopMatrix()

    def ResetGL(self):
        self.SetScaling(25.0, False)
        self.SetTranslation(0.0, 0.0, 0.5, False)
        self.SetRotation(-90.1, 0.0, 0.1, False)

class TrajectoryResultPanel(_ResultPanel):

    def _init_panel(self, sizer):
        # Controls
        self._canvas = _TrajectoryResultGLCanvas(self, self.options, self.result)
        self._canvas.SetSensitivityRotation(2.5)

        # Sizer
        sizer.Add(self._canvas, 1, wx.EXPAND)

    def _init_toolbar(self, sizer):
        # Controls
        toolbar = GLCanvasToolbar(self._canvas)

        toolbar.AddSeparator()

        item_options = toolbar.AddSimpleTool(-1, _ICON_OPTIONS.GetBitmap(),
                                             'Setup display options')
        toolbar.Realize()

        # Sizer
        sizer.Add(toolbar, 0, wx.GROW)

        # Bind
        self.Bind(wx.EVT_TOOL, self.OnOptions, item_options)

    def OnOptions(self, event):
        params = self._canvas.GetParameters()
        dialog = _TrajectoryResultDialog(self, params)

        if dialog.ShowModal() == wx.ID_OK:
            self._canvas.SetParameters(dialog.GetParameters())

        dialog.Destroy()

ResultPanelManager.register(TrajectoryResult, TrajectoryResultPanel)

class _PhotonIntensityResultParameters(object):

    def __init__(self):
        self.units = 'counts / (sr.electron)'

        self.generated_nofluorescence = True
        self.generated_characteristic_fluorescence = True
        self.generated_bremsstrahlung_fluorescence = True
        self.generated_total = True

        self.emitted_nofluorescence = True
        self.emitted_characteristic_fluorescence = True
        self.emitted_bremsstrahlung_fluorescence = True
        self.emitted_total = True

        self.uncertainty = True

class _PhotonIntensityResultDialog(wx.Dialog):

    def __init__(self, parent, params):
        wx.Dialog.__init__(self, parent, title='Setup display options')

        # Controls
        ## Units
        lbl_units = wx.StaticText(self, label='Units')
        self._cb_units = PyComboBox(self)
        self._cb_units.append('counts / (sr.electron)')
        self._cb_units.append('counts / (s.A)')
        self._cb_units.append('counts / (s.nA)')

        ## Uncertainties
        self._chk_uncertainty = wx.CheckBox(self, label='Show uncertainties')

        ## Generated
        box_generated = wx.StaticBox(self, label='Generated intensities (no absorption)')

        self._chk_generated_nofluorescence = \
            wx.CheckBox(self, label='No fluorescence')
        self._chk_generated_characteristic_fluorescence = \
            wx.CheckBox(self, label='Characteristic fluorescence')
        self._chk_generated_bremsstrahlung_fluorescence = \
            wx.CheckBox(self, label='Bremsstrahlung fluorescence')
        self._chk_generated_total = wx.CheckBox(self, label='Total')

        ## Emitted
        box_emitted = wx.StaticBox(self, label='Emitted intensities (with absorption)')

        self._chk_emitted_nofluorescence = \
            wx.CheckBox(self, label='No fluorescence')
        self._chk_emitted_characteristic_fluorescence = \
            wx.CheckBox(self, label='Characteristic fluorescence')
        self._chk_emitted_bremsstrahlung_fluorescence = \
            wx.CheckBox(self, label='Bremsstrahlung fluorescence')
        self._chk_emitted_total = wx.CheckBox(self, label='Total')

        ## Buttons
        btn_ok = wx.Button(self, wx.ID_OK)
        btn_cancel = wx.Button(self, wx.ID_CANCEL)
        btn_default = wx.Button(self, wx.ID_DEFAULT, label='Default')

        # Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        ## Units
        szr_top = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(szr_top, 0, wx.GROW | wx.ALL, 5)

        szr_top.Add(lbl_units, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        szr_top.Add(self._cb_units, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        szr_top.AddStretchSpacer()
        szr_top.Add(self._chk_uncertainty, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)

        ## Generated
        szr_generated = wx.StaticBoxSizer(box_generated, wx.VERTICAL)
        sizer.Add(szr_generated, 0, wx.GROW | wx.ALL, 5)

        szr_generated2 = wx.GridBagSizer(5, 5)
        szr_generated.Add(szr_generated2, 1, wx.GROW | wx.ALL, 5)

        szr_generated2.Add(self._chk_generated_nofluorescence, (0, 0))
        szr_generated2.Add(self._chk_generated_total, (1, 0))
        szr_generated2.Add(self._chk_generated_characteristic_fluorescence, (0, 1))
        szr_generated2.Add(self._chk_generated_bremsstrahlung_fluorescence, (1, 1))

        ## Emitted
        szr_emitted = wx.StaticBoxSizer(box_emitted, wx.VERTICAL)
        sizer.Add(szr_emitted, 0, wx.GROW | wx.ALL, 5)

        szr_emitted2 = wx.GridBagSizer(5, 5)
        szr_emitted.Add(szr_emitted2, 1, wx.GROW | wx.ALL, 5)

        szr_emitted2.Add(self._chk_emitted_nofluorescence, (0, 0))
        szr_emitted2.Add(self._chk_emitted_total, (1, 0))
        szr_emitted2.Add(self._chk_emitted_characteristic_fluorescence, (0, 1))
        szr_emitted2.Add(self._chk_emitted_bremsstrahlung_fluorescence, (1, 1))

        ## Buttons
        szr_button = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(szr_button, 0, wx.GROW | wx.ALL, 5)

        szr_button.Add(btn_default, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        szr_button.AddStretchSpacer()

        szr_button2 = wx.StdDialogButtonSizer()
        szr_button.Add(szr_button2, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        szr_button2.AddButton(btn_ok)
        szr_button2.AddButton(btn_cancel)
        szr_button2.SetAffirmativeButton(btn_ok)
        szr_button2.SetCancelButton(btn_cancel)
        szr_button2.Realize()

        self.SetSizer(sizer)
        self.Fit()

        # Bind
        self.Bind(wx.EVT_BUTTON, self.OnDefault, btn_default)

        # Default
        self.SetParameters(params)

    def OnDefault(self, event):
        self.SetParameters(_PhotonIntensityResultParameters())

    def SetParameters(self, params):
        self._cb_units.selection = params.units

        self._chk_generated_nofluorescence.SetValue(params.generated_nofluorescence)
        self._chk_generated_characteristic_fluorescence.SetValue(params.generated_characteristic_fluorescence)
        self._chk_generated_bremsstrahlung_fluorescence.SetValue(params.generated_bremsstrahlung_fluorescence)
        self._chk_generated_total.SetValue(params.generated_total)

        self._chk_emitted_nofluorescence.SetValue(params.emitted_nofluorescence)
        self._chk_emitted_characteristic_fluorescence.SetValue(params.emitted_characteristic_fluorescence)
        self._chk_emitted_bremsstrahlung_fluorescence.SetValue(params.emitted_bremsstrahlung_fluorescence)
        self._chk_emitted_total.SetValue(params.emitted_total)

        self._chk_uncertainty.SetValue(params.uncertainty)

    def GetParameters(self):
        params = _PhotonIntensityResultParameters()

        params.units = self._cb_units.selection

        params.generated_nofluorescence = self._chk_generated_nofluorescence.GetValue()
        params.generated_characteristic_fluorescence = self._chk_generated_characteristic_fluorescence.GetValue()
        params.generated_bremsstrahlung_fluorescence = self._chk_generated_bremsstrahlung_fluorescence.GetValue()
        params.generated_total = self._chk_generated_total.GetValue()

        params.emitted_nofluorescence = self._chk_emitted_nofluorescence.GetValue()
        params.emitted_characteristic_fluorescence = self._chk_emitted_characteristic_fluorescence.GetValue()
        params.emitted_bremsstrahlung_fluorescence = self._chk_emitted_bremsstrahlung_fluorescence.GetValue()
        params.emitted_total = self._chk_emitted_total.GetValue()

        params.uncertainty = self._chk_uncertainty.GetValue()

        return params

class PhotonIntensityResultPanel(_SaveableResultPanel):
    _COLUMNS = ['Gen. No Fluo.', 'Gen. Charac. Fluo.', 'Gen. Bremss. Fluo.', 'Gen. Total',
                'Emi. No Fluo.', 'Emi. Charac. Fluo.', 'Emi. Bremss. Fluo.', 'Emi. Total']

    _COLUMNS_VISIBLE = {'Gen. No Fluo.': lambda params: params.generated_nofluorescence,
                        'Gen. Charac. Fluo.': lambda params: params.generated_characteristic_fluorescence,
                        'Gen. Bremss. Fluo.': lambda params: params.generated_bremsstrahlung_fluorescence,
                        'Gen. Total': lambda params: params.generated_total,
                        'Emi. No Fluo.': lambda params: params.emitted_nofluorescence,
                        'Emi. Charac. Fluo.': lambda params: params.emitted_characteristic_fluorescence,
                        'Emi. Bremss. Fluo.': lambda params: params.emitted_bremsstrahlung_fluorescence,
                        'Emi. Total': lambda params: params.emitted_total}

    _COLUMNS_VALUE = {'Gen. No Fluo.': lambda res, trans: res.intensity(trans, False, False),
                      'Gen. Charac. Fluo.': lambda result, transition: result.characteristic_fluorescence(transition, False),
                      'Gen. Bremss. Fluo.': lambda result, transition: result.bremsstrahlung_fluorescence(transition, False),
                      'Gen. Total': lambda res, trans: res.intensity(trans, False, True),
                      'Emi. No Fluo.': lambda res, trans: res.intensity(trans, True, False),
                      'Emi. Charac. Fluo.': lambda result, transition: result.characteristic_fluorescence(transition, True),
                      'Emi. Bremss. Fluo.': lambda result, transition: result.bremsstrahlung_fluorescence(transition, True),
                      'Emi. Total': lambda res, trans: res.intensity(trans, True, True)}

    def __init__(self, parent, options, key, result):
        self._params = _PhotonIntensityResultParameters() # default
        _SaveableResultPanel.__init__(self, parent, options, key, result)

    def _init_panel(self, sizer):
        # Controls
        self._grid = Grid(self)
        self._grid.CreateGrid(1, 1)
        self._grid.SetDefaultColSize(125)
        self._grid.EnableEditing(False)

        # Sizer
        sizer.Add(self._grid, 1, wx.EXPAND)

        # Default
        self.DrawGrid()

    def _init_toolbar(self, sizer):
        toolbar = _SaveableResultPanel._init_toolbar(self, sizer)
        item_options = \
            toolbar.InsertSimpleTool(toolbar.GetToolPos(self._TB_COPY), -1,
                                     _ICON_OPTIONS.GetBitmap(),
                                     'Setup display options')
        toolbar.InsertSeparator(toolbar.GetToolPos(self._TB_COPY))
        toolbar.Realize()

        # Bind
        self.Bind(wx.EVT_TOOL, self.OnOptions, item_options)

    def GetParameters(self):
        return self._params

    def SetParameters(self, params):
        self._params = params
        self.DrawGrid()

    def DrawGrid(self):
        # Calculate conversion factor
        solidangle_sr = self.options.detectors[self._key].solidangle_sr
        factors = {'counts / (s.A)': solidangle_sr / physics.e,
                   'counts / (s.nA)': solidangle_sr / physics.e / 1e9}
        factor = factors.get(self._params.units, 1.0)

        self._grid.BeginBatch()

        # Clear grid
        self._grid.DeleteRows(0, self._grid.GetNumberRows())
        self._grid.DeleteCols(0, self._grid.GetNumberCols())

        # Create columns
        icol = -1
        columns = []
        for column in self._COLUMNS:
            if not self._COLUMNS_VISIBLE[column](self._params): continue

            icol += 1
            self._grid.AppendCols(1)
            self._grid.SetColLabelValue(icol, column)

            if self._params.uncertainty:
                icol += 1
                self._grid.AppendCols(1)
                self._grid.SetColLabelValue(icol, column + " Unc.")

            columns.append(column)

        # Create rows
        for irow, transition in enumerate(self.result._intensities.iterkeys()):
            self._grid.AppendRows(1)
            self._grid.SetRowLabelValue(irow, unicode(transition))

            icol = -1
            for column in columns:
                val, unc = self._COLUMNS_VALUE[column](self.result, transition)

                val *= factor
                unc *= factor

                icol += 1
                self._grid.SetCellValue(irow, icol, "%e" % val)

                if self._params.uncertainty:
                    icol += 1
                    self._grid.SetCellValue(irow, icol, '%e' % unc)

        self._grid.EndBatch()

    def OnOptions(self, event):
        dialog = _PhotonIntensityResultDialog(self, self.GetParameters())

        if dialog.ShowModal() == wx.ID_OK:
            self.SetParameters(dialog.GetParameters())

        dialog.Destroy()

    def dump(self):
        rows = []

        # Header
        header = ['Transition']
        for icol in range(self._grid.GetNumberCols()):
            header.append(self._grid.GetColLabelValue(icol))
        rows.append(header)

        # Data
        for irow in range(self._grid.GetNumberRows()):
            row = [self._grid.GetRowLabelValue(irow)]

            for icol in range(self._grid.GetNumberCols()):
                row.append(float(self._grid.GetCellValue(irow, icol)))

            rows.append(row)

        return rows

ResultPanelManager.register(PhotonIntensityResult, PhotonIntensityResultPanel)

class TimeResultPanel(_SaveableResultPanel):

    def _init_panel(self, sizer):
        # Controls
        lbl_time = wx.StaticText(self, label='Total time of the simulation')
        txt_time = wx.TextCtrl(self, size=(200, -1),
                               style=wx.TE_READONLY | wx.ALIGN_RIGHT)
        txt_time.SetValue(human_time(self.result.simulation_time_s))

        lbl_speed = wx.StaticText(self, label='Average time of one trajectory')
        txt_speed = wx.TextCtrl(self, size=(200, -1),
                                style=wx.TE_READONLY | wx.ALIGN_RIGHT)
        val, _unc = self.result.simulation_speed_s
        txt_speed.SetValue(human_time(val))

        # Sizer
        sizer.Add(lbl_time, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        sizer.Add(txt_time, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 25)
        sizer.Add(lbl_speed, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        sizer.Add(txt_speed, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 25)

        sizer.AddStretchSpacer()

    def dump(self):
        return [['Simulation time (s)', 'Simulation speed (s)'],
                [self.result.simulation_time_s, self.result.simulation_speed_s[0]]]

ResultPanelManager.register(TimeResult, TimeResultPanel)

class ElectronFractionResultPanel(_SaveableResultPanel):

    def _init_panel(self, sizer):
        # Controls
        lbl_absorbed = wx.StaticText(self, label='Absorbed fraction')
        txt_absorbed_val = wx.TextCtrl(self, size=(100, -1),
                                       style=wx.TE_READONLY | wx.ALIGN_RIGHT)
        txt_absorbed_val.SetValue(str(self.result.absorbed[0]))
        txt_absorbed_unc = wx.TextCtrl(self, size=(100, -1),
                                       style=wx.TE_READONLY | wx.ALIGN_RIGHT)
        txt_absorbed_unc.SetValue(str(self.result.absorbed[1]))

        lbl_backscattered = wx.StaticText(self, label='Backscattered fraction')
        txt_backscattered_val = wx.TextCtrl(self, size=(100, -1),
                                       style=wx.TE_READONLY | wx.ALIGN_RIGHT)
        txt_backscattered_val.SetValue(str(self.result.backscattered[0]))
        txt_backscattered_unc = wx.TextCtrl(self, size=(100, -1),
                                       style=wx.TE_READONLY | wx.ALIGN_RIGHT)
        txt_backscattered_unc.SetValue(str(self.result.backscattered[1]))

        lbl_transmitted = wx.StaticText(self, label='Transmitted fraction')
        txt_transmitted_val = wx.TextCtrl(self, size=(100, -1),
                                       style=wx.TE_READONLY | wx.ALIGN_RIGHT)
        txt_transmitted_val.SetValue(str(self.result.transmitted[0]))
        txt_transmitted_unc = wx.TextCtrl(self, size=(100, -1),
                                       style=wx.TE_READONLY | wx.ALIGN_RIGHT)
        txt_transmitted_unc.SetValue(str(self.result.transmitted[1]))

        # Sizer
        sizer.Add(lbl_absorbed, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        szr_absorbed = wx.BoxSizer(wx.HORIZONTAL)
        szr_absorbed.Add(txt_absorbed_val, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        szr_absorbed.Add(wx.StaticText(self, label=u"\u00b1"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        szr_absorbed.Add(txt_absorbed_unc, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(szr_absorbed, 0, wx.LEFT, 25)

        sizer.Add(lbl_backscattered, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        szr_backscattered = wx.BoxSizer(wx.HORIZONTAL)
        szr_backscattered.Add(txt_backscattered_val, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        szr_backscattered.Add(wx.StaticText(self, label=u"\u00b1"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        szr_backscattered.Add(txt_backscattered_unc, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(szr_backscattered, 0, wx.LEFT, 25)

        sizer.Add(lbl_transmitted, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        szr_transmitted = wx.BoxSizer(wx.HORIZONTAL)
        szr_transmitted.Add(txt_transmitted_val, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        szr_transmitted.Add(wx.StaticText(self, label=u"\u00b1"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        szr_transmitted.Add(txt_transmitted_unc, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(szr_transmitted, 0, wx.LEFT, 25)

        sizer.AddStretchSpacer()

    def dump(self):
        return [['', 'Absorbed', 'Backscattered', 'Transmitted'],
                ['Average', self.result.absorbed[0], self.result.backscattered[0], self.result.transmitted[0]],
                ['Std. Dev.', self.result.absorbed[1], self.result.backscattered[1], self.result.transmitted[1]]]

ResultPanelManager.register(ElectronFractionResult, ElectronFractionResultPanel)

class PhotonSpectrumResultPanel(_SaveableResultPanel):

    def __init__(self, parent, options, key, result):
        _SaveableResultPanel.__init__(self, parent, options, key, result)

        self._register_save_method('emsa', 'Electronic Microscopy Society of America format',
                                   self._save_emsa)

    def _init_panel(self, sizer):
        # Variable
        fig = Figure()
        ax = fig.add_subplot("111")

        energies_eV, intensities, uncs = self.result.get_total()
        ax.errorbar(energies_eV, intensities, uncs,
                    fmt='b-', ecolor='#c0d8ff', elinewidth=1)

        ax.set_xlabel('Energy (eV)')
        ax.set_ylabel('Intensity (counts / (sr.eV.electron))')

        # Controls
        self._canvas = FigureCanvasWxAgg(self, -1, fig)

        # Sizer
        sizer.Add(self._canvas, 1, wx.EXPAND)

    def _init_toolbar(self, sizer):
        # Controls
        statusbar = StatusBarWx(self)

        toolbar = NavigationToolbarWx(self._canvas)
        toolbar.set_status_bar(statusbar)

        toolbar.DeleteTool(toolbar._NTB2_SAVE)

        toolbar.AddSeparator()

        self._TB_COPY = wx.NewId()
        toolbar.AddSimpleTool(self._TB_COPY, _ICON_COPY.GetBitmap(),
                              "Copy results to clipboard")

        self._TB_SAVE = wx.NewId()
        toolbar.AddSimpleTool(self._TB_SAVE, _ICON_SAVE.GetBitmap(),
                              "Save results to file")

        toolbar.Realize()

        # Sizer
        sizer.Add(statusbar, 0, wx.GROW)
        sizer.Add(toolbar, 0, wx.GROW)

        # Bind
        self.Bind(wx.EVT_TOOL, self.copy, id=self._TB_COPY)
        self.Bind(wx.EVT_TOOL, self.save, id=self._TB_SAVE)

        return toolbar

    def dump(self):
        data = np.array(self.result.get_total())
        return np.transpose(data)

    def _save_emsa(self, filepath):
        pass

ResultPanelManager.register(PhotonSpectrumResult, PhotonSpectrumResultPanel)

#if __name__ == '__main__': # pragma: no cover
#    import math
#    from zipfile import ZipFile
#    from pymontecarlo.input.options import Options
#    from pymontecarlo.input.geometry import \
#        Substrate, Inclusion, MultiLayers, GrainBoundaries, Sphere
#    from pymontecarlo.input.material import pure
#    from pymontecarlo.input.detector import PhotonIntensityDetector
#
#    results_zip = os.path.join(os.path.dirname(__file__),
#                               '../../../testdata/results.zip')
#    zipfile = ZipFile(results_zip, 'r')
#
#    options = Options(name="Test")
#    options.detectors['det1'] = PhotonIntensityDetector((0, math.pi / 2), (0, 2 * math.pi))
#
#    options.geometry = Substrate(pure(8))
#
#    options.geometry = Inclusion(pure(5), pure(6), 0.5e-6)
#
#    options.geometry = MultiLayers(pure(5))
#    options.geometry.add_layer(pure(6), 0.55e-6)
#    options.geometry.add_layer(pure(6), 0.1e-6)
#
#    options.geometry = GrainBoundaries(pure(8), pure(9))
#    options.geometry.add_layer(pure(6), 0.55e-6)
#
#    options.geometry = Sphere(pure(10), 0.75e-6)
#
#    options.geometry.tilt_rad = math.radians(30)
#
#    class __MainFrame(wx.Frame):
#
#        def __init__(self, parent):
#            wx.Frame.__init__(self, parent, title='Main frame')
#
##            result = TrajectoryResult.__loadzip__(zipfile, 'det6')
##            self.panel = TrajectoryResultPanel(self, options, 'det6', result)
#
#            result = PhotonIntensityResult.__loadzip__(zipfile, 'det1')
#            self.panel = PhotonIntensityResultPanel(self, options, 'det1', result)
#
#            sizer = wx.BoxSizer(wx.VERTICAL)
#            sizer.Add(self.panel, 1, wx.EXPAND)
#
#            self.SetSizer(sizer)
#
#    app = wx.PySimpleApp()
#
#    mainframe = __MainFrame(None)
#    mainframe.SetSizeWH(400, 400)
#    mainframe.Show()
#
#    app.MainLoop()
