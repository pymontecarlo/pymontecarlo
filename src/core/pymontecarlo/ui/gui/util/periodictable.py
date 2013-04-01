#!/usr/bin/env python
"""
================================================================================
:mod:`periodictable` -- Dialog of the periodic table of elements
================================================================================

.. module:: periodictable
   :synopsis: Dialog of the periodic table of elements

.. inheritance-diagram:: pymontecarlo.ui.gui.util.periodictable

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.
import wx.lib.newevent

# Local modules.
import pymontecarlo.util.element_properties as ep

# Globals and constants variables.

COLOR_ALKALI_METALS = '#CC99CC'
COLOR_ALKALI_EARTH_METALS = '#00FFFF'
COLOR_NON_METALS = '#00CC66'
COLOR_TRANSITION_METALS = '#66FF99'
COLOR_OTHER_METALS = '#9933CC'
COLOR_HALOGENS = '#FFCC00'
COLOR_INERT_GAS = '#CC0000'
COLOR_LANTHANIDES = '#6600FF'
COLOR_ACTINIDES = '#6666FF'

# Elements setup
def _setup_elements():
    e = {}
    e[1] = ((0, 0), COLOR_NON_METALS)

    ## Alkali Metals
    for row, z in enumerate([3, 11, 19, 37, 55, 87]):
        e[z] = ((row + 1, 0), COLOR_ALKALI_METALS)

    ## Alkali Earth Metals
    for row, z in enumerate([4, 12, 20, 38, 56, 88]):
        e[z] = ((row + 1, 1), COLOR_ALKALI_EARTH_METALS)

    ## Transition Metals
    transitions = [range(21, 30 + 1), range(39, 48 + 1),
                   range(71, 80 + 1), range(103, 106 + 1)]
    for row, transitions_row in enumerate(transitions):
        for col, z in enumerate(transitions_row):
            e[z] = ((row + 3, col + 3), COLOR_TRANSITION_METALS)

    ## Non Metals
    nonmetals = [range(5, 8 + 1), range(14, 16 + 1), range(33, 34 + 1), [52]]
    for row, nonmetals_row in enumerate(nonmetals):
        for col, z in enumerate(nonmetals_row):
            e[z] = ((row + 1, col + 13 + row), COLOR_NON_METALS)

    ## Other Metals
    othermetals = [[13], range(31, 32 + 1), range(49, 51 + 1), range(81, 84 + 1)]
    for row, othermetals_row in enumerate(othermetals):
        for col, z in enumerate(othermetals_row):
            e[z] = ((row + 2, col + 13), COLOR_OTHER_METALS)

    ## Halogens
    for row, z in enumerate([9, 17, 35, 53, 85]):
        e[z] = ((row + 1, 17), COLOR_HALOGENS)

    ## Inert gas
    for row, z in enumerate([2, 10, 18, 36, 54, 86]):
        e[z] = ((row, 18), COLOR_INERT_GAS)

    ## Lanthanides
    for col, z in enumerate(range(57, 70 + 1)):
        e[z] = ((8, col + 3), COLOR_LANTHANIDES)

    ## Actinides
#    for col, z in enumerate(range(89, 102 + 1)):
    for col, z in enumerate(range(89, 96 + 1)): # Limit range to actual available data
        e[z] = ((9, col + 3), COLOR_ACTINIDES)

    return e

_ELEMENTS = _setup_elements()

# Command
ElementEnterEvent, EVT_ENTER_ELEMENT = wx.lib.newevent.NewCommandEvent()
ElementLeaveEvent, EVT_LEAVE_ELEMENT = wx.lib.newevent.NewCommandEvent()
ElementSelectEvent, EVT_SELECT_ELEMENT = wx.lib.newevent.NewCommandEvent()

class ElementPanel(wx.Panel):
    def __init__(self, parent, z, color):
        minsize = (30, 40)
        wx.Panel.__init__(self, parent, size=minsize)

        self.SetBackgroundColour(color)
        self.SetMinSize(minsize)

        # Variables
        self._z = z
        self._color = color

        # Controls
        font = wx.Font(pointSize=10, family=wx.SWISS, style=wx.NORMAL, weight=wx.BOLD)

        lblz = wx.StaticText(self, label="%i" % z)
        lblsymbol = wx.StaticText(self, label="%s" % ep.symbol(z))
        lblsymbol.SetFont(font)

        # Sizer
        sizer = wx.GridSizer(rows=3, cols=1, hgap=1, vgap=3)

        sizer.Add(lblz, 0, wx.ALIGN_LEFT)
        sizer.Add(lblsymbol, 0, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)

        self.SetSizer(sizer)
        self.Fit()

        # Bind
        self.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        lblz.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        lblsymbol.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeave)

    def OnClick(self, event):
        event = ElementSelectEvent(self.GetId(), z=self._z)
        self.GetEventHandler().ProcessEvent(event)

    def OnEnter(self, event):
        event = ElementEnterEvent(self.GetId(), z=self._z)
        self.GetEventHandler().ProcessEvent(event)

    def OnLeave(self, event):
        event = ElementLeaveEvent(self.GetId(), z=self._z)
        self.GetEventHandler().ProcessEvent(event)

    def Select(self):
        self.SetBackgroundColour(wx.LIGHT_GREY)
        self.Refresh()

    def Unselect(self):
        self.SetBackgroundColour(self._color)
        self.Refresh()

class PeriodicTableDialog(wx.Dialog):
    def __init__(self, parent, multiple_selection=False):
        """
        """
        wx.Dialog.__init__(self, parent, title="Periodic Table")

        # Variables
        self._multiple_selection = multiple_selection
        self._panels = {}
        self._selection = []

        # Controls
        self._lblinfo = wx.StaticText(self, label="")

        for z in _ELEMENTS.iterkeys():
            _pos, color = _ELEMENTS[z]
            self._panels[z] = ElementPanel(self, z, color)

        btnok = wx.Button(self, wx.ID_OK)
        btnok.SetDefault()
        btncancel = wx.Button(self, wx.ID_CANCEL)

        # Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        ## Add elements
        szr_elements = wx.GridBagSizer(1, 1)
        sizer.Add(szr_elements, 1, wx.EXPAND | wx.ALL, 10)

        for z, panel in self._panels.iteritems():
            pos, _color = _ELEMENTS[z]
            szr_elements.Add(panel, pos=pos, flag=wx.EXPAND)

        ## Add info label
        szr_elements.Add(self._lblinfo, pos=(1, 3), span=(2, 9), flag=wx.EXPAND)

        ## Add buttons
        szr_buttons = wx.StdDialogButtonSizer()
        sizer.Add(szr_buttons, 0, wx.GROW | wx.ALL, 10)
        szr_buttons.AddButton(btnok)
        szr_buttons.AddButton(btncancel)
        szr_buttons.SetAffirmativeButton(btnok)
        szr_buttons.SetCancelButton(btncancel)
        szr_buttons.Realize()

        self.SetSizerAndFit(sizer)

        # Bind
        self.Bind(EVT_ENTER_ELEMENT, self.OnEnterElement)
        self.Bind(EVT_LEAVE_ELEMENT, self.OnLeaveElement)
        self.Bind(EVT_SELECT_ELEMENT, self.OnSelectElement)

    def OnEnterElement(self, event):
        z = event.z
        text = u''

        text += 'Common name: %s\n' % ep.name(z)
        text += 'Molar mass: %s g/cm3\n' % (ep.atomic_mass_kg_mol(z) * 1000.0,)
        try:
            text += 'Density: %s g/cm3\n' % (ep.mass_density_kg_m3(z) / 1000.0,)
        except:
            pass

        self._lblinfo.SetLabel(text)

    def OnLeaveElement(self, event):
        self._lblinfo.SetLabel('')

    def OnSelectElement(self, event):
        z = event.z

        if z in self._selection:
            self._selection.remove(z)
            self.Refresh()
            return

        if self._multiple_selection:
            self._selection.append(z)
        else:
            self._selection = [z]

        self.Refresh()

    def Refresh(self):
        wx.Dialog.Refresh(self)

        self.Freeze()

        for panel in self._panels.itervalues():
            panel.Unselect()

        for z in self._selection:
            self._panels[z].Select()

        self.Thaw()

    @property
    def selection(self):
        """
        Returns the atomic number(s) of the selection. 
        If multiple selection is allowed, a :class:`list` is returned, otherwise
        the selected element or ``None``.
        """
        if self._multiple_selection:
            return list(self._selection)
        else:
            if self._selection:
                return self._selection[0]
            else:
                return None

    @selection.setter
    def selection(self, zs):
        if isinstance(zs, int):
            zs = [zs]

        if self._multiple_selection:
            self._selection = list(zs)
        else:
            self._selection = [zs[0]]

        self.Refresh()

    @selection.deleter
    def selection(self):
        self._selection = []
        self.Refresh()

if __name__ == '__main__':
    class __MainFrame(wx.Frame):
        def __init__(self, parent, title='Main frame'):
            wx.Frame.__init__(self, parent, title=title)

            self.label = wx.StaticText(self, label='Pd', pos=(0, 0))

            button = wx.Button(self, label='Launch Periodic Table', pos=(0, 50))
            button.Bind(wx.EVT_BUTTON, self._on_click)

        def _on_click(self, event):
            dialog = PeriodicTableDialog(self, multiple_selection=False)
#
            if dialog.ShowModal() == wx.ID_OK:
                self.label.SetLabel(ep.symbol(dialog.selection))

    app = wx.PySimpleApp()

    mainframe = __MainFrame(parent=None)
    mainframe.Show()

    app.MainLoop()

