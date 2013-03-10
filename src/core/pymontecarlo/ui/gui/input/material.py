#!/usr/bin/env python
"""
================================================================================
:mod:`material` -- Material dialog
================================================================================

.. module:: material
   :synopsis: Material dialog

.. inheritance-diagram:: pymontecarlo.ui.gui.input.material

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from operator import itemgetter, attrgetter

# Third party modules.
import wx
from wx.lib.embeddedimage import PyEmbeddedImage

# Local modules.
from wxtools2.list import \
    PyListCtrl, StaticColumn, TextCtrlColumn, EVT_LIST_CHANGED, wxEVT_LIST_CHANGED
from wxtools2.menu import popupmenu
from wxtools2.dialog import show_exclamation_dialog, show_error_dialog
from wxtools2.exception import catch_all
from wxtools2.dialog import show_open_filedialog, show_save_filedialog

import pymontecarlo.util.element_properties as ep
from pymontecarlo.input.material import \
    composition_from_formula, Material, _generate_name, _calculate_composition

from pymontecarlo.ui.gui.util.periodictable import PeriodicTableDialog

# Globals and constants variables.
from pymontecarlo.ui.gui.art import \
    ART_LIST_ADD, ART_LIST_REMOVE, ART_LIST_CLEAR, ART_LIST_EDIT

_ICON_CALC = PyEmbeddedImage("iVBORw0KGgoAAAANSUhEUgAAABYAAAAWCAYAAADEtGw7AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAGWAAABlgBH4cC6gAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAAQdEVYdFRpdGxlAENhbGN1bGF0b3IeSkheAAAAFHRFWHRBdXRob3IASmFrdWIgU3RlaW5lcub79y8AAABJdEVYdENvcHlyaWdodABQdWJsaWMgRG9tYWluIGh0dHA6Ly9jcmVhdGl2ZWNvbW1vbnMub3JnL2xpY2Vuc2VzL3B1YmxpY2RvbWFpbi9Zw/7KAAADsElEQVQ4jZ2Vy28bVRSHvzt3PI5nJrZnHBMnJG0S+hKNwqIholRdsoLyP0J33SB1wzILFLFCJJVCK5UmRJXzsseOPH7N614Wqd04NVRwpFnM0bnf/ek3Z84RWmtGsb6+btm27fM/w3Gc5vb2dgogRuCNjQ3vyZPvf7tz905x2qEr9wN6Sg52f989e/Fi98H29vbQHCV939/c3Npa3dnZwZDyPynVaBAGX3390N7Z+WUFeDUGSynF2dk599fv4rqS13/uTYX0un0K9gzDQYSUkplCno31R7w5eEuz2TRGdebVQ1Ec4VcqDAYBnU4wFXzwpo5pSlqtDhftkEePvyCKIxzH4fysLaaCsyyjP+jje/Osra5PBa+u3H9Xq5DSQAgD23aonzSJouG4bgxO05Qkjvnx6TO++/YbFhYWkcbHvc6yjP0/XvPT8595/PDhh2AAK2fRal/ww9NnHwVeDyEEWis1eh+bnaYpwhBsPdikXC5hGBLDMD7+CIFdsLl5YxmdqXEDTige9AfYdoHFapXFapWy59MKmqgsw3ZcBsMhSRKRzxew8nkG/R5ojTAM8jMF1JXGHisefbi3R3+x9OkiC7V5Tk/qFGddbt++Rb8XorOEz+/dI0sihv0eKzeW2fpyk5vLS5iGuKpxUnESJ6RZRqPRQCmFAC4uLlBKkaQpWZpyenpKHMfkCzbFYhHHcXAch1a7jXpv8SRYoZktlmi32whDUP1knqBxTjMI8CtzdMOQZrNJqeyRpCl7e3tYlkWSJPiVuQnFBtei3w1ZXl5ioVajHQS4rsvqygrdsIPKUtbW1hj0e0gzh5mzsB0H23EJe32ujo4JxVop0jRFKYXWmiRJ0HqGLMvI0nTcPUop0jjm9q3P8DyPVqtF/fjknz0GcIsljo9PEAIq1SrtVkDY7eJ5Ht1uj3q9ju04DKMYy7KwLAvTNC/7OHvv8YQVWmui4YDZWRfbtgnDDtIw8D2PXq9HHEeUy2WGgwFaa6SUOI6DnDINP/A4TRJ838f3fZIoolgsUiqV0EqRM01KpRJCCEwzRxRFBEFAHMcImOjjsRVaa6GVJpfPc3h4CIA/N0ej0SBotZh1XcKwy8HhIXnLQkrJ/v4+pmmilKLsVwAt4jjOTYDDMJS5nJnV5mtScLkjlNbYzuy7OaApepWxZZdRRggBWl92hCbrdDruBPjly5e/ztdqz8vl8g0NE7+Rvr6DpuQF6Eaj8ero6OgAruw8ACFEHigC1lTSv0cKhFrrPsDf67q55FA43HwAAAAASUVORK5CYII=")

class _ElementRow(object):
    """
    Internal object for the list control.
    """

    def __init__(self, z, weightfraction, atomicfraction=''):
        self._z = z
        self.weightfraction = weightfraction
        self.atomicfraction = atomicfraction

    def __eq__(self, other):
        return self._z == other.z

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(('ElementRow', self._z))

    @property
    def z(self):
        return self._z

class MaterialDialog(wx.Dialog):

    def __init__(self, parent, material=None):
        """
        Creates a new material dialog to create/edit material.
        
        :arg parent: parent window
        :arg material: material to edit. ``None`` to create new.
        """
        wx.Dialog.__init__(self, parent, title='Material')
        self.SetSizeHints(500, 600)

        # Variables
        self._material = material

        # Controls
        ## Name
        lblname = wx.StaticText(self, label='Name')
        self._txtname = wx.TextCtrl(self)
        self._txtname.Enable(False)
        self._chknameauto = wx.CheckBox(self, label='auto')
        self._chknameauto.SetValue(True)

        ## Density
        lbldensity = wx.StaticText(self, label='Density (g/cm3)')
        self._txtdensity = wx.TextCtrl(self)
        self._txtdensity.Enable(False)
        self._chkdensityuserdefined = wx.CheckBox(self, label='user defined')
        self._chkdensityuserdefined.SetValue(False)

        ## Elements
        columns = [StaticColumn('Element', lambda row: ep.symbol(row.z), width=150),
                   TextCtrlColumn('Weight fraction', lambda row: str(row.weightfraction),
                                  lambda row, val: setattr(row, 'weightfraction', val),
                                  width=150),
                   StaticColumn('Atomic fraction', lambda row: str(row.atomicfraction),
                                width=150)]
        self._lstelements = PyListCtrl(self, columns, multiple_selection=True)

        ## Action buttons
        toolbar = wx.ToolBar(self)

        self._TOOL_ADD = wx.NewId()
        bitmap = wx.ArtProvider_GetBitmap(ART_LIST_ADD, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(self._TOOL_ADD, bitmap,
                              "Add element using the periodic table")

        self._TOOL_REMOVE = wx.NewId()
        bitmap = wx.ArtProvider_GetBitmap(ART_LIST_REMOVE, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(self._TOOL_REMOVE, bitmap,
                              "Remove selected element(s)")

        self._TOOL_CLEAR = wx.NewId()
        bitmap = wx.ArtProvider_GetBitmap(ART_LIST_CLEAR, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(self._TOOL_CLEAR, bitmap, "Remove all elements")

        toolbar.AddSeparator()

        self._TOOL_CALC = wx.NewId()
        bitmap = _ICON_CALC.GetBitmap()
        toolbar.AddSimpleTool(self._TOOL_CALC, bitmap,
                              "Calculate missing fraction, density and name")

        self._TOOL_OPEN = wx.NewId()
        bitmap = wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(self._TOOL_OPEN, bitmap, "Open material")

        self._TOOL_SAVE = wx.NewId()
        bitmap = wx.ArtProvider_GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(self._TOOL_SAVE, bitmap, "Save material")

        toolbar.Realize()

        ## Ok/cancel buttons
        btnok = wx.Button(self, wx.ID_OK)
        btnok.SetDefault()
        btncancel = wx.Button(self, wx.ID_CANCEL)

        # Sizers
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer1 = wx.FlexGridSizer(2, 3, 5, 5)
        sizer.Add(sizer1, 0, wx.GROW | wx.ALL, 5)
        sizer1.AddGrowableCol(1)
        sizer1.Add(lblname, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer1.Add(self._txtname, 0, wx.GROW)
        sizer1.Add(self._chknameauto, 0, wx.GROW)
        sizer1.Add(lbldensity, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer1.Add(self._txtdensity, 0, wx.GROW)
        sizer1.Add(self._chkdensityuserdefined, 0, wx.GROW)

        sizer.Add(self._lstelements, 1, wx.EXPAND | wx.ALL, 5)

        sizer.Add(toolbar, 0, wx.ALIGN_RIGHT)

        szr_buttons = wx.StdDialogButtonSizer()
        sizer.Add(szr_buttons, 0, wx.GROW | wx.ALL, 10)
        szr_buttons.AddButton(btnok)
        szr_buttons.AddButton(btncancel)
        szr_buttons.SetAffirmativeButton(btnok)
        szr_buttons.SetCancelButton(btncancel)
        szr_buttons.Realize()

        self.SetSizer(sizer)

        # Bind
        self.Bind(wx.EVT_TOOL, self.OnAdd, id=self._TOOL_ADD)
        self.Bind(wx.EVT_TOOL, self.OnRemove, id=self._TOOL_REMOVE)
        self.Bind(wx.EVT_TOOL, self.OnClear, id=self._TOOL_CLEAR)
        self.Bind(wx.EVT_TOOL, self.OnCalc, id=self._TOOL_CALC)
        self.Bind(wx.EVT_TOOL, self.OnOpen, id=self._TOOL_OPEN)
        self.Bind(wx.EVT_TOOL, self.OnSave, id=self._TOOL_SAVE)

        self.Bind(wx.EVT_CHECKBOX, self.OnNameAuto, self._chknameauto)
        self.Bind(wx.EVT_CHECKBOX, self.OnDensityUserDefined, self._chkdensityuserdefined)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_BUTTON, self.OnOk, id=wx.ID_OK)

        # Load material
        if material is not None:
            self._load_material(material)

    def _calculate(self):
        """
        Calculates composition, name and density based on the user selection.
        Updates internal material (:var:`_material`) and graphical interface.
        """
        composition = {}
        for row in self._lstelements:
            composition[row.z] = row.weightfraction

        # Replace wildcards
        with catch_all(self) as success:
            composition = _calculate_composition(composition)
        if not success:
            return

        # Name
        if self._chknameauto.IsChecked():
            name = _generate_name(composition)
        else:
            name = self._txtname.GetValue().strip()
            if not name:
                show_error_dialog(self, "Please specify a name")
                return

        # Density
        if self._chkdensityuserdefined.IsChecked():
            try:
                density_kg_m3 = float(self._txtdensity.GetValue())
            except ValueError:
                show_error_dialog(self, "Density is not a number")
                return

            if density_kg_m3 <= 0.0:
                show_error_dialog(self, "Density must be greater than 0.0")
                return
        else:
            density_kg_m3 = None

        # Create material
        with catch_all(self) as success:
            mat = Material(name, composition, density_kg_m3)
        if not success:
            return

        # Update dialog
        self._txtname.SetValue(mat.name)
        self._txtdensity.SetValue(str(mat.density_kg_m3))

        for i, row in enumerate(self._lstelements):
            self._lstelements[i] = \
                _ElementRow(row.z, mat.composition[row.z],
                            mat.composition_atomic[row.z])

        return mat

    def _load_material(self, material):
        self._txtname.SetValue(material.name)
        self._txtname.Enable(True)
        self._chknameauto.SetValue(False)

        if material.has_density_defined():
            self._txtdensity.SetValue(str(material.density_kg_m3))
            self._txtdensity.Enable(True)
            self._chkdensityuserdefined.SetValue(True)
        else:
            self._txtdensity.Clear()
            self._txtdensity.Enable(False)
            self._chkdensityuserdefined.SetValue(False)

        self._lstelements.clear()
        for z, fraction in material.composition.iteritems():
            row = _ElementRow(z, fraction, material.composition_atomic[z])
            self._lstelements.append(row)

    def OnAdd(self, event):
        def _addperiodictable():
            dialog = PeriodicTableDialog(self, multiple_selection=True)

            composition = {}
            if dialog.ShowModal() == wx.ID_OK:
                elements = dialog.selection
                composition = dict(zip(elements, ['?'] * len(elements)))

            dialog.Destroy()
            return composition

        def _addchemicalformula():
            dialog = \
                wx.TextEntryDialog(self, message="Enter chemical formula (e.g. Al2O3)",
                                   caption="Add new element(s)",
                                   style=wx.OK | wx.CANCEL | wx.CENTRE)

            composition = {}
            if dialog.ShowModal() == wx.ID_OK:
                composition = composition_from_formula(dialog.GetValue())

            dialog.Destroy()
            return composition

        # Two add options
        objects = [('Periodic table', _addperiodictable),
                   ('Chemical formula', _addchemicalformula)]
        answer = popupmenu(self, objects, itemgetter(0))
        if answer is None:
            return
        composition = answer[1]()

        # Add rows
        for z, weightfraction in composition.iteritems():
            row = _ElementRow(z, weightfraction)
            if row not in self._lstelements:
                self._lstelements.append(row)

    def OnRemove(self, event):
        if not self._lstelements: # No elements
            return

        if not self._lstelements.selection:
            show_exclamation_dialog(self, "Please select an element to delete")
            return

        del self._lstelements.selection

        if self._chknameauto.IsChecked():
            self._txtname.Clear()

        if not self._chkdensityuserdefined.IsChecked():
            self._txtdensity.Clear()

    def OnClear(self, event):
        self._lstelements.clear()

        if self._chknameauto.IsChecked():
            self._txtname.Clear()

        if not self._chkdensityuserdefined.IsChecked():
            self._txtdensity.Clear()

    def OnCalc(self, event):
        self._calculate()

    def OnOpen(self, event):
        filetypes = [('Material file (*.xml)', 'xml')]
        filepath = show_open_filedialog(self, filetypes, multiple_selection=False)
        if filepath is None:
            return

        with catch_all(self) as success:
            mat = Material.load(filepath)
        if not success:
            return

        self._load_material(mat)

    def OnSave(self, event):
        mat = self._calculate()
        if mat is None:
            return

        filetypes = [('Material file (*.xml)', 'xml')]
        filepath = show_save_filedialog(self, filetypes)
        if filepath is None:
            return

        with catch_all(self) as success:
            mat.save(filepath)
        if not success:
            return

    def OnNameAuto(self, event):
        self._txtname.Enable(not self._chknameauto.IsChecked())

    def OnDensityUserDefined(self, event):
        self._txtdensity.Enable(self._chkdensityuserdefined.IsChecked())

    def OnClose(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnOk(self, event):
        mat = self._calculate()
        if mat is None:
            event.StopPropagation()
        else:
            if self._material is None:
                self._material = mat
            else:
                self._material.name = mat.name
                self._material.composition = mat.composition
                self._material.density_kg_m3 = mat.density_kg_m3
            event.Skip()

    def GetMaterial(self):
        """
        Returns the successfully created material or the edited material.
        """
        return self._material

from wxtools2.list import PyListCtrlValidator

class MaterialListCtrl(wx.Panel):

    def __init__(self, parent):
        """
        List control to add materials.
        """
        wx.Panel.__init__(self, parent)

        # Controls
        ## List control
        columns = [StaticColumn('Material(s)', attrgetter('name'), width= -3)]
        validator = PyListCtrlValidator(False)
        self._lst = PyListCtrl(self, columns, validator=validator,
                               name='materials')

        ## Action buttons
        toolbar = wx.ToolBar(self)

        self._TOOL_ADD = wx.NewId()
        bitmap = wx.ArtProvider_GetBitmap(ART_LIST_ADD, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(self._TOOL_ADD, bitmap, "Add material")

        self._TOOL_REMOVE = wx.NewId()
        bitmap = wx.ArtProvider_GetBitmap(ART_LIST_REMOVE, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(self._TOOL_REMOVE, bitmap,
                              "Remove selected material")

        self._TOOL_CLEAR = wx.NewId()
        bitmap = wx.ArtProvider_GetBitmap(ART_LIST_CLEAR, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(self._TOOL_CLEAR, bitmap, "Remove all materials")

        self._TOOL_EDIT = wx.NewId()
        bitmap = wx.ArtProvider_GetBitmap(ART_LIST_EDIT, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(self._TOOL_EDIT, bitmap, "Edit material")

        toolbar.Realize()

        # Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(self._lst, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(toolbar, 0, wx.ALIGN_RIGHT)

        self.SetSizer(sizer)

        # Bind
        self.Bind(wx.EVT_TOOL, self.OnAdd, id=self._TOOL_ADD)
        self.Bind(wx.EVT_TOOL, self.OnRemove, id=self._TOOL_REMOVE)
        self.Bind(wx.EVT_TOOL, self.OnClear, id=self._TOOL_CLEAR)
        self.Bind(wx.EVT_TOOL, self.OnEdit, id=self._TOOL_EDIT)

        self.Bind(EVT_LIST_CHANGED, self._OnListChanged, self._lst)

    def OnAdd(self, event):
        dialog = MaterialDialog(self.GetParent())

        if dialog.ShowModal() == wx.ID_OK:
            material = dialog.GetMaterial()
            self._lst.append(material)

        dialog.Destroy()

    def OnRemove(self, event):
        if not self._lst: # No materials
            return

        if not self._lst.selection:
            show_exclamation_dialog(self, "Please select a material to delete")
            return

        del self._lst.selection

    def OnClear(self, event):
        self._lst.clear()

    def OnEdit(self, event):
        if not self._lst: # No materials
            return

        if not self._lst.selection:
            show_exclamation_dialog(self, "Please select a material to edit")
            return

        dialog = MaterialDialog(self.GetParent(), self._lst.selection)

        if dialog.ShowModal() == wx.ID_OK:
            material = dialog.GetMaterial()
            self._lst[self._lst.index(material)] = material # update

        dialog.Destroy()

    def _OnListChanged(self, event):
        # Wrapper
        event = wx.PyCommandEvent(wxEVT_LIST_CHANGED, self.GetId())
        self.GetEventHandler().ProcessEvent(event)

    def GetMaterials(self):
        return list(self._lst) # copy

if __name__ == '__main__':
    from pymontecarlo.ui.gui.art import ArtProvider

    class __MainFrame(wx.Frame):
        def __init__(self, parent, title='Main frame'):
            wx.Frame.__init__(self, parent, title=title)

            self.material = None

            self.label = wx.StaticText(self, label='test', pos=(0, 0))

            button = wx.Button(self, label='Launch Material', pos=(0, 50))
            button.Bind(wx.EVT_BUTTON, self._on_click)

        def _on_click(self, event):
            self._dialog = MaterialDialog(self, self.material)
            if self._dialog.ShowModal() == wx.ID_OK:
                print 'ok'
            else:
                print 'cancel'

            self.material = self._dialog.GetMaterial()

            self.label.SetLabel(str(self.material))

            self._dialog.Destroy()

    app = wx.PySimpleApp()

    wx.ArtProvider.Push(ArtProvider())

    mainframe = __MainFrame(parent=None)
    mainframe.Show()

    app.MainLoop()

