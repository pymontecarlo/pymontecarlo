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
from wx.lib.embeddedimage import PyEmbeddedImage
from wx.lib.pubsub import Publisher as pub

# Local modules.
from pymontecarlo.ui.gui.controller import controller
from pymontecarlo.ui.gui.output.manager import ResultPanelManager
from pymontecarlo.ui.gui.configure import ConfigureDialog
import pymontecarlo.ui.gui.output.result #@UnusedImport

from wxtools2.tree import PyTreeCtrl
from wxtools2.menu import popupmenu

# Globals and constants variables.

_ICON_APP = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlw"
    "SFlzAAAN1wAADdcBQiibeAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoA"
    "AAAUdEVYdFRpdGxlAFNpeCBTaWRlZCBEaWNlcXL2rQAAACV0RVh0QXV0aG9yAEJyaWFuIEJ1"
    "cmdlci9XaXJlbGl6YXJkIERlc2lnbgWEk6cAAAAndEVYdERlc2NyaXB0aW9uAFNpbXBsZSBz"
    "aXgtc2lkZWQgZGljZSAoZDYpLqlJ67cAAABJdEVYdENvcHlyaWdodABQdWJsaWMgRG9tYWlu"
    "IGh0dHA6Ly9jcmVhdGl2ZWNvbW1vbnMub3JnL2xpY2Vuc2VzL3B1YmxpY2RvbWFpbi9Zw/7K"
    "AAAFxklEQVRYha3XeYxV9RUH8M/v8dhB1mGZAhGBgk5lcYpSBZsCsghKbCIEkQZswLb+QQma"
    "NlryfA1JtU0MCVolpISyhBbsUKKtpYQYyADDMlBIoQIlKCXD6DAgQnGmzsztH/e94c0CMuhJ"
    "bnLvPdv3nnN+55wboijyVSiEdAL3Yyw2RFHqfIv0bwdACOmumIxpmIqeGVYF5kVR6q9fO4AQ"
    "0gUZh9PwIJI3EI2wHD+PotT/bhtACOl2+J7rX3nXLSG9TqWYHUWpUzcTSjTjuEMI6c2oxF/w"
    "RwzB3VjfAgCFOBRCeu7NhBpEIIT0CFxEbxShP+ZHUWpNht8eH6NzC4DAOvwkilJXvwxAGj/G"
    "TBzHZjyMf+K0OA33ttB5lk6JU1Ka+7JxCgqRh+2YjQlYgW9hxm04r8YG/BZtsSeE9OIQ0uFm"
    "AIgrfDlW42eYh6oWOoc/RVHq6ShKPYfB+ANew7shpPMaAAgh3Rd9GhmYi2K8j3H4TwsBPBFC"
    "+sUQ0gPQA9lj+ag4KtdrIIT0dLxzA0MXxHVxDJvw3RYCydIH2Ji5LiORm4LCZlVi6imuizmY"
    "KK6LW6Wz+DVG4TviKL6BMuTldrMmAAYO7Kq6ulZZ2RVoJc5fIRbgIFaiXTNOK8SR2oh/YDpe"
    "Fje0NhmZT3GsCYAZM4YaO3aAAwfKPPXUvQYM6GL16sNef31/Vm4O7sH3xQNoi7hffJa534hd"
    "eATP4XF0bAbk3ihK1SUghHQf5ENhYb4XXtiusvKafv3ucOHCNSUl57z00rhc5VGZCHTN3E/K"
    "6K/Hk+LwbhUf5Y7JZMKUKYO9+urEXBvFXD8FhdC3bycffvgp2LHjjGee2apt21YuXvzczp0f"
    "mTmzINdAD/xNXEzjxI1qO36IriHw0EP9vfHGo8rKlnjvvTkKCnrl6u9uAiCKaN06IQSmT/+m"
    "06cvmjt3i27d2ikuPmvYsJ4a0UfohqXi9m348N5eeWWiM2d+aufO+QYN6m7Jkm1KSs45evTj"
    "rN4X2N8EQHn5Vfn5na1a9bgFC+6zbdtc/fvfobT0vGQyoba2rjGAEjyQfSgqmuXIkR+ZMGGg"
    "5ctL9Ov3milT1lu37qjBg7s7cqQ8K3ooilKfc32m35flLFu2y9q1T5g1620dO7ZWVDTLW28d"
    "VFVV47HHhtq06ZhTpy5mxfdhTPZh/PiBFi58x6pVhxqgzM/vrGfPDrkRKM7eJEJI90K/+th8"
    "UefYsQpVVTUuXaoydeoGkycPtmjRGLNnv+3ZZ7+da3uf+Gy7886uunRpa8+eps1yxIjeqqpq"
    "nDxZmX21O3uTxMjGCslknJnFi8c4f/6qefP+XM+rqPivRCKoq4uqcRSjiXNfXV3rxInKxuaM"
    "GNHH8eMVamvrJ289gAT24u+5Clu3fmDRoge8+eZB8+eP9PzzD9bzOnVqo64ugsPiRaVzFsDx"
    "4xVqaprUiZEj+zhypD78J6Mo9Un9x0ZR6koI6Wni4bAADh8ul0gES5c+bNSovqKINm1aKSr6"
    "lytX6te8BvkfPrx3bo4bRaC3lSvr14DdubwkRFGqBgtDSJ/GrxBKS8+7dKlKMplQXHzWgQNl"
    "ZswYasWKfVndEnG3qwewcuXBJs7bt08aMqRHswVIM0tpCOknsVbzPT6X7sK7uKd9+6SrV180"
    "adI6O3acaSA0enS+/fsXyMv7jQsXrsGwKEqdyPKbLKVRlNqM8eKBciP6RLw73g0FBb0kEqHZ"
    "FFy+XG3Zsl1Z5xdynTcLIANirzi/J5rji/N/PwJxjsvLr6qouNZE8OTJSkuXvh9hh3iQNaCb"
    "/piEkO4mnnCNF5BfZMD/EvLyOhg0qLuSknONTfwbv8faKEqdbdbHl/0ZhZBug9/h6ZzXj2Cx"
    "eLVqTJ+Jd4E1UZTa3Qy/ZQBygLyMFOrQXTz9emTYdeIQr8GWbJ+/Jbst+TkNIf0D8ZfPxMnM"
    "tQbroijVJP5fO4AMiLbi0fuNTLF+Jfo/o3cLsVEiyfEAAAAASUVORK5CYII=")

class ToolBar(wx.ToolBar):

    def __init__(self, parent):
        wx.ToolBar.__init__(self, parent)

        # Controls
        bitmap = wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR)
        self.AddSimpleTool(wx.ID_NEW, bitmap, "New simulation(s)")

        bitmap = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR)
        self.AddSimpleTool(wx.ID_OPEN, bitmap, "Open options and/or results")

        self.AddSeparator()

        bitmap = wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_TOOLBAR)
        self.AddSimpleTool(wx.ID_CLOSE, bitmap, "Close simulation")

        self.Realize()

class MainFrame(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title='pyMonteCarlo')

        # Controls
        ## Menu
        menubar = wx.MenuBar()
        self.SetMenuBar(menubar)

        menu_file = wx.Menu()
        menubar.Append(menu_file, 'File')

        menu_file.Append(wx.ID_NEW, "New simulation(s)")
        menu_file.Append(wx.ID_OPEN, "Open options and/or results")

        menu_file.AppendSeparator()

        menu_file.Append(wx.ID_CLOSE, "Close").Enable(False)
        menu_file.Append(wx.ID_CLOSE_ALL, "Close all").Enable(False)

        menu_file.AppendSeparator()

        menu_file.Append(wx.ID_PREFERENCES, "Configuration")

        menu_file.Append(wx.ID_EXIT, "Quit")

        ## Toolbar
        toolbar = ToolBar(self)
        self.SetToolBar(toolbar)

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

    def OnExit(self, event=None):
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
                panel = wx.Panel(self._splitter)
                sizer = wx.BoxSizer(wx.VERTICAL)
                sizer.Add(wx.StaticText(panel, label='No viewer for this result'))
                panel.SetSizer(sizer)
            else:
                panel = panel_class(self._splitter, sim.options, key, result)

            subnode.panel = panel
            subnode.panel.Hide()

    def OnRemoveSimulation(self, message):
        sim = message.data

        for node in self._tree:
            if node.sim == sim:
                node.remove()
                break

    def OnClearSimulation(self, message):
        self._tree.clear()

    def OnChangedSimulation(self, message):
        menubar = self.GetMenuBar()
        toolbar = self.GetToolBar()

        enabled = self._tree.selection is not None
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

    mainframe = MainFrame(parent=None)
    mainframe.SetIcon(_ICON_APP.GetIcon())

    mainframe.SetSizeWH(1000, 600)

    mainframe.Show()

    logging.debug("Main display shown")

    app.MainLoop()

if __name__ == '__main__':
    run()
