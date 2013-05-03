#!/usr/bin/env python
"""
================================================================================
:mod:`main` -- Main program
================================================================================

.. module:: main
   :synopsis: Main program

.. inheritance-diagram:: pymontecarlo.ui.gui.main

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

##################################################################
# Write stdout and stderr to file if main is frozen
import os, sys, imp

#os.chdir('/home/ppinard/tmp')

if hasattr(sys, "frozen") or hasattr(sys, "importers") or imp.is_frozen("__main__"):
    filepath = os.path.join(os.path.expanduser('~'), '.pymontecarlo', "stdout.log")
    sys.stdout = open(filepath, "w")
    print "stdout saved in %s" % filepath

    filepath = os.path.join(os.path.expanduser('~'), '.pymontecarlo', "stderr.log")
    sys.stderr = open(filepath, "w")
    print "stderr saved in %s" % filepath
##################################################################

# Standard library modules.
import logging

# Third party modules.
import wx
from wx.lib.pubsub import Publisher as pub

# Local modules.
from pymontecarlo.ui.gui.controller import controller
from pymontecarlo.ui.gui.output.result import ResultPanelManager, UnknownResultPanel
from pymontecarlo.ui.gui.configure import ConfigureDialog
from pymontecarlo.ui.gui.art import ArtProvider

from wxtools2.tree import PyTreeCtrl
from wxtools2.menu import popupmenu
from wxtools2.display import center_on_primary_screen

# Globals and constants variables.
from pymontecarlo.ui.gui.art import ART_CLOSE, ART_PREFERENCES, ICON_APP_LOGO

class MainFrame(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title='pyMonteCarlo')

        # Controls
        ## Menu
        menubar = wx.MenuBar()
        self.SetMenuBar(menubar)

        menu_file = wx.Menu()
        menubar.Append(menu_file, 'File')

        item = wx.MenuItem(menu_file, wx.ID_NEW, "New simulation(s)")
        item.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_MENU))
        menu_file.AppendItem(item)

        item = wx.MenuItem(menu_file, wx.ID_OPEN, "Open options and/or results")
        item.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU))
        menu_file.AppendItem(item)

        menu_file.AppendSeparator()

        item = wx.MenuItem(menu_file, wx.ID_CLOSE, "Close")
        item.SetBitmap(wx.ArtProvider.GetBitmap(ART_CLOSE, wx.ART_MENU))
        menu_file.AppendItem(item)

        item = wx.MenuItem(menu_file, wx.ID_CLOSE_ALL, "Close all")
        menu_file.AppendItem(item)

        menu_file.AppendSeparator()

        item = wx.MenuItem(menu_file, wx.ID_PREFERENCES, "Configuration")
        item.SetBitmap(wx.ArtProvider.GetBitmap(ART_PREFERENCES, wx.ART_MENU))
        menu_file.AppendItem(item)

        item = wx.MenuItem(menu_file, wx.ID_EXIT, "Quit")
        item.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_MENU))
        menu_file.AppendItem(item)

        menubar.Enable(wx.ID_CLOSE, False)
        menubar.Enable(wx.ID_CLOSE_ALL, False)

        ## Toolbar
        toolbar = wx.ToolBar(self)
        self.SetToolBar(toolbar)

        bitmap = wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(wx.ID_NEW, bitmap, "New simulation(s)")

        bitmap = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(wx.ID_OPEN, bitmap, "Open options and/or results")

        toolbar.AddSeparator()

        bitmap = wx.ArtProvider.GetBitmap(ART_CLOSE, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(wx.ID_CLOSE, bitmap, "Close")

        toolbar.Realize()

        toolbar.EnableTool(wx.ID_CLOSE, False)

        ## Splitter
        self._splitter = wx.SplitterWindow(self)
        self._tree = PyTreeCtrl(self._splitter)
        self._panel = wx.Panel(self._splitter)

        self._splitter.SplitVertically(self._tree, self._panel, 300)

        # Sizer
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        mainsizer.Add(self._splitter, 1, wx.EXPAND)
        self.SetSizer(mainsizer)

        # Bind
        pub.subscribe(self.OnAddSimulation, 'controller.simulation.add')
        pub.subscribe(self.OnRemoveSimulation, 'controller.simulation.remove')
        pub.subscribe(self.OnClearSimulation, 'controller.simulation.clear')
        pub.subscribe(self.OnChangedSimulation, 'controller.simulation')

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnChangedSimulation, self._tree)

        self.Bind(wx.EVT_MENU, lambda event: controller.create(self), id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, lambda event: controller.open(self), id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, lambda event: controller.remove(self._tree.selection.sim), id=wx.ID_CLOSE)
        self.Bind(wx.EVT_MENU, lambda event: controller.clear(), id=wx.ID_CLOSE_ALL)
        self.Bind(wx.EVT_MENU, self.OnConfiguration, id=wx.ID_PREFERENCES)
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)

        self.Bind(wx.EVT_CLOSE, self.OnExit)

    def OnExit(self, event=None):
        controller.close()
        wx.Exit()

    def OnConfiguration(self, event):
        dialog = ConfigureDialog(self)
        dialog.ShowModal()
        dialog.Destroy()

    def OnAddSimulation(self, message):
        sim = message.data

        text = sim.options.name
        node = self._tree.add(text)
        node.sim = sim
        node.bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnRightClickSimulation)

        for key in sorted(sim.results.keys()):
            result = sim.results[key]

            text = '%s [%s]' % (key, result.__class__.__name__)
            subnode = node.add(text)
            subnode.bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnLeftClickResult)

            try:
                panel_class = ResultPanelManager.get(result.__class__, True)
            except KeyError:
                panel_class = UnknownResultPanel

            panel = panel_class(self._splitter, sim.options, key, result)

            subnode.panel = panel
            subnode.panel.Hide()

    def OnRemoveSimulation(self, message):
        sim = message.data

        for node in self._tree:
            if node.sim == sim:
                node.remove()
                self.change_window(wx.Panel(self._splitter))
                break

    def OnClearSimulation(self, message):
        self._tree.clear()
        self.change_window(wx.Panel(self._splitter))

    def OnChangedSimulation(self, message):
        menubar = self.GetMenuBar()
        toolbar = self.GetToolBar()

        selection = self._tree.selection
        enabled = selection is not None and hasattr(selection, 'sim')
        menubar.Enable(wx.ID_CLOSE, enabled)
        toolbar.EnableTool(wx.ID_CLOSE, enabled)

        enabled = len(controller) > 0
        menubar.Enable(wx.ID_CLOSE_ALL, enabled)
        toolbar.EnableTool(wx.ID_CLOSE_ALL, enabled)

    def OnRightClickSimulation(self, event):
        answer = popupmenu(self, ['Close'])

        if answer == 'Close':
            wx.CallAfter(controller.remove, event.node.sim)

    def OnLeftClickResult(self, event):
        panel = getattr(event.node, 'panel', None)
        if panel is None:
            return

        self.change_window(panel)

    def change_window(self, panel):
        self.Freeze()

        oldpanel = self._panel
        oldpanel.Hide()

        self._splitter.ReplaceWindow(oldpanel, panel)

        panel.Show()
        self._panel = panel

        self.Thaw()

def run():
    logging.getLogger().setLevel(logging.DEBUG)

    app = wx.PySimpleApp()

    wx.ArtProvider.Push(ArtProvider())

    mainframe = MainFrame(parent=None)
    mainframe.SetIcon(ICON_APP_LOGO.GetIcon())
    mainframe.SetSizeWH(1000, 600)
    center_on_primary_screen(mainframe)

    mainframe.Show()

    logging.debug("Main display shown")

    app.MainLoop()

if __name__ == '__main__':
    run()
