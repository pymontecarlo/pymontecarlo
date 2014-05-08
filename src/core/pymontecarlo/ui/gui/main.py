#!/usr/bin/env python
"""
================================================================================
:mod:`main` -- Main window
================================================================================

.. module:: main
   :synopsis: Main window

.. inheritance-diagram:: pymontecarlo.ui.gui.main

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import sys
import logging
import platform

# Third party modules.
from PySide.QtGui import \
    (QMainWindow, QMdiArea, QTreeWidget, QAction, QKeySequence, QDockWidget,
     QProgressDialog, QApplication, QTreeWidgetItem, QMenu, QMdiSubWindow,
     QScrollArea, QFileDialog, QMessageBox)
from PySide.QtCore import Qt

import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4'] = 'PySide'

# Local modules.
from pymontecarlo.ui.gui.controller import Controller
from pymontecarlo.ui.gui.options.wizard.wizard import OptionsWizard
from pymontecarlo.ui.gui.options.beam import \
    get_widget_class as get_beam_widget_class
from pymontecarlo.ui.gui.options.geometry import \
    get_widget_class as get_geometry_widget_class
from pymontecarlo.ui.gui.options.detector import DetectorsWidget
from pymontecarlo.ui.gui.options.limit import LimitsWidget
from pymontecarlo.ui.gui.options.model import ModelTableWidget

from pymontecarlo.ui.gui.util.tango import getIcon
import pymontecarlo.ui.gui.util.messagebox as messagebox

# Globals and constants variables.

#--- Tree items

class _ActionTreeItem(QTreeWidgetItem):

    def __init__(self, controller, parent):
        QTreeWidgetItem.__init__(self, parent)

        # Variables
        self._controller = controller
        self._menu = QMenu()

    def controller(self):
        return self._controller

    def addAction(self, action):
        self._menu.addAction(action)

    def insertAction(self, index, action):
        self._menu.insertAction(index, action)

    def setDefaultAction(self, action):
        self._menu.setDefaultAction(action)

    def popupMenu(self):
        return self._menu

class _BaseTreeItem(_ActionTreeItem):

    def __init__(self, uid, controller, parent):
        _ActionTreeItem.__init__(self, controller, parent)

        # Variables
        self._uid = uid

        # Actions
        self._act_save = QAction("Save", self.treeWidget())
        self._act_save.setEnabled(self.canSave())
        self.addAction(self._act_save)

        self._act_saveas = QAction("Save As", self.treeWidget())
        self._act_saveas.setEnabled(self.canSaveAs())
        self.addAction(self._act_saveas)

        self._act_close = QAction("Close", self.treeWidget())
        self._act_close.setEnabled(self.canClose())
        self.addAction(self._act_close)

        # Signals
        self._act_save.triggered.connect(self.requestSave)
        self._act_saveas.triggered.connect(self.requestSaveAs)
        self._act_close.triggered.connect(self.requestClose)

    def uid(self):
        return self._uid

    def canSave(self):
        raise NotImplementedError

    def requestSave(self):
        raise NotImplementedError

    def canSaveAs(self):
        raise NotImplementedError

    def requestSaveAs(self):
        raise NotImplementedError

    def canClose(self):
        raise NotImplementedError

    def requestClose(self):
        raise NotImplementedError

class _BaseOptionsTreeItem(_BaseTreeItem):

    def __init__(self, uid, controller, parent):
        _BaseTreeItem.__init__(self, uid, controller, parent)

        # Signals
        self.controller().optionsModified.connect(self._onOptionsModified)

    def _onOptionsModified(self, uid, options):
        self._act_save.setEnabled(self.canSave())
        self._act_saveas.setEnabled(self.canSaveAs())
        self._act_close.setEnabled(self.canClose())

    def canSave(self):
        has_filepath = bool(self.controller().optionsFilepath(self.uid()))
        is_edited = self.controller().isOptionsEdited(self.uid())
        return is_edited or not has_filepath

    def requestSave(self):
        self.controller().optionsSaveRequested.emit(self.uid())

    def canSaveAs(self):
        return True

    def requestSaveAs(self):
        self.controller().optionsSaveAsRequested.emit(self.uid())

    def canClose(self):
        return True

    def requestClose(self):
        self.controller().optionsRemoveRequested.emit(self.uid())

class _OptionsTreeItem(_BaseOptionsTreeItem):

    def __init__(self, uid, controller, parent):
        _BaseOptionsTreeItem.__init__(self, uid, controller, parent)
        self.setText(0, controller.options(uid).name)
        self.setToolTip(0, controller.optionsFilepath(uid))

        # Actions
        act_modify = QAction("Modify", self.treeWidget())
        self.addAction(act_modify)

        # Signals
        act_modify.triggered.connect(self.requestModify)

        self.controller().optionsSaved.connect(self._onOptionsSaved)

    def _onOptionsModified(self, uid, options):
        _BaseOptionsTreeItem._onOptionsModified(self, uid, options)
        self.setText(0, options.name)

    def _onOptionsSaved(self, uid, filepath):
        self.setToolTip(0, filepath)

    def requestModify(self):
        self.controller().optionsModifyRequested.emit(self.uid())

class _BeamTreeItem(_BaseOptionsTreeItem):

    def __init__(self, uid, controller, parent):
        _BaseOptionsTreeItem.__init__(self, uid, controller, parent)
        self.setText(0, 'Beam')

        # Actions
        act_display = QAction("Display", self.treeWidget())
        self.addAction(act_display)
        self.setDefaultAction(act_display)

        # Signals
        act_display.triggered.connect(self.requestDisplay)

    def requestDisplay(self):
        self.controller().beamDisplayRequested.emit(self.uid())

class _GeometryTreeItem(_BaseOptionsTreeItem):

    def __init__(self, uid, controller, parent):
        _BaseOptionsTreeItem.__init__(self, uid, controller, parent)
        self.setText(0, 'Geometry')

        # Actions
        act_display = QAction("Display", self.treeWidget())
        self.addAction(act_display)
        self.setDefaultAction(act_display)

        # Signals
        act_display.triggered.connect(self.requestDisplay)

    def requestDisplay(self):
        self.controller().geometryDisplayRequested.emit(self.uid())

class _DetectorsTreeItem(_BaseOptionsTreeItem):

    def __init__(self, uid, controller, parent):
        _BaseOptionsTreeItem.__init__(self, uid, controller, parent)
        self.setText(0, 'Detectors')

        # Actions
        act_display = QAction("Display", self.treeWidget())
        self.addAction(act_display)
        self.setDefaultAction(act_display)

        # Signals
        act_display.triggered.connect(self.requestDisplay)

    def requestDisplay(self):
        self.controller().detectorsDisplayRequested.emit(self.uid())

class _LimitsTreeItem(_BaseOptionsTreeItem):

    def __init__(self, uid, controller, parent):
        _BaseOptionsTreeItem.__init__(self, uid, controller, parent)
        self.setText(0, 'Limits')

        # Actions
        act_display = QAction("Display", self.treeWidget())
        self.addAction(act_display)
        self.setDefaultAction(act_display)

        # Signals
        act_display.triggered.connect(self.requestDisplay)

    def requestDisplay(self):
        self.controller().limitsDisplayRequested.emit(self.uid())

class _ModelsTreeItem(_BaseOptionsTreeItem):

    def __init__(self, uid, controller, parent):
        _BaseOptionsTreeItem.__init__(self, uid, controller, parent)
        self.setText(0, 'Models')

        # Actions
        act_display = QAction("Display", self.treeWidget())
        self.addAction(act_display)
        self.setDefaultAction(act_display)

        # Signals
        act_display.triggered.connect(self.requestDisplay)

    def requestDisplay(self):
        self.controller().modelsDisplayRequested.emit(self.uid())

#--- Sub-windows

class _WidgetSubWindow(QMdiSubWindow):

    def __init__(self, controller, parent=None):
        QMdiSubWindow.__init__(self, parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowIcon(getIcon('text-x-generic'))

        # Variables
        self._controller = controller

        # Widgets
        scrollarea = QScrollArea()
        scrollarea.setWidgetResizable(True)

        # Layouts
        QMdiSubWindow.setWidget(self, scrollarea)

    def controller(self):
        return self._controller

    def widget(self):
        return QMdiSubWindow.widget(self).widget()

    def setWidget(self, widget):
        widget.layout().setContentsMargins(10, 10, 10, 10)
        return QMdiSubWindow.widget(self).setWidget(widget)

class _SubOptionsWidgetSubWindow(_WidgetSubWindow):

    def __init__(self, uid, controller, parent=None):
        _WidgetSubWindow.__init__(self, controller, parent)

        # Variables
        self._uid = uid

    def uid(self):
        return self._uid

class _BeamSubWindow(_SubOptionsWidgetSubWindow):

    def __init__(self, uid, controller, parent=None):
        _SubOptionsWidgetSubWindow.__init__(self, uid, controller, parent)
        self.setWindowTitle('Beam')

        # Widgets
        beam = controller.options(uid).beam
        widget = get_beam_widget_class(beam.__class__)()
        widget.setValue(beam)
        widget.setReadOnly(True)
        self.setWidget(widget)

    def closeEvent(self, event):
        self.controller().beamDisplayClosed.emit(self.uid())
        return _WidgetSubWindow.closeEvent(self, event)

class _GeometrySubWindow(_SubOptionsWidgetSubWindow):

    def __init__(self, uid, controller, parent=None):
        _SubOptionsWidgetSubWindow.__init__(self, uid, controller, parent)
        self.setWindowTitle('Geometry')

        # Widgets
        geometry = controller.options(uid).geometry
        widget = get_geometry_widget_class(geometry.__class__)()
        widget.setValue(geometry)
        widget.setReadOnly(True)
        self.setWidget(widget)

    def closeEvent(self, event):
        self.controller().geometryDisplayClosed.emit(self.uid())
        return _WidgetSubWindow.closeEvent(self, event)

class _DetectorsSubWindow(_SubOptionsWidgetSubWindow):

    def __init__(self, uid, controller, parent=None):
        _SubOptionsWidgetSubWindow.__init__(self, uid, controller, parent)
        self.setWindowTitle('Detectors')

        # Widgets
        detectors = controller.options(uid).detectors
        widget = DetectorsWidget()
        widget.addDetectors(detectors)
        widget.setReadOnly(True)
        self.setWidget(widget)

    def closeEvent(self, event):
        self.controller().detectorsDisplayClosed.emit(self.uid())
        return _WidgetSubWindow.closeEvent(self, event)

class _LimitsSubWindow(_SubOptionsWidgetSubWindow):

    def __init__(self, uid, controller, parent=None):
        _SubOptionsWidgetSubWindow.__init__(self, uid, controller, parent)
        self.setWindowTitle('Limits')

        # Widgets
        limits = controller.options(uid).limits
        widget = LimitsWidget()
        widget.addLimits(limits)
        widget.setReadOnly(True)
        self.setWidget(widget)

    def closeEvent(self, event):
        self.controller().limitsDisplayClosed.emit(self.uid())
        return _WidgetSubWindow.closeEvent(self, event)

class _ModelsSubWindow(_SubOptionsWidgetSubWindow):

    def __init__(self, uid, controller, parent=None):
        _SubOptionsWidgetSubWindow.__init__(self, uid, controller, parent)
        self.setWindowTitle('Models')

        # Widgets
        models = controller.options(uid).models
        widget = ModelTableWidget()
        widget.addModels(models)
        self.setWidget(widget)

    def closeEvent(self, event):
        self.controller().modelsDisplayClosed.emit(self.uid())
        return _WidgetSubWindow.closeEvent(self, event)

#--- Main widgets

class _Area(QMdiArea):

    def __init__(self, controller, parent=None):
        QMdiArea.__init__(self, parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Variables
        self._controller = controller
        self._options_windows = {}

        # Signals
        self.controller().optionsModified.connect(self._onOptionsModified)
        self.controller().optionsRemoved.connect(self._onOptionsRemoved)

        self.controller().beamDisplayRequested.connect(self._onBeamDisplayRequested)
        self.controller().beamDisplayClosed.connect(self._onBeamDisplayClosed)
        self.controller().geometryDisplayRequested.connect(self._onGeometryDisplayRequested)
        self.controller().geometryDisplayClosed.connect(self._onGeometryDisplayClosed)
        self.controller().detectorsDisplayRequested.connect(self._onDetectorsDisplayRequested)
        self.controller().detectorsDisplayClosed.connect(self._onDetectorsDisplayClosed)
        self.controller().limitsDisplayRequested.connect(self._onLimitsDisplayRequested)
        self.controller().limitsDisplayClosed.connect(self._onLimitsDisplayClosed)
        self.controller().modelsDisplayRequested.connect(self._onModelsDisplayRequested)
        self.controller().modelsDisplayClosed.connect(self._onModelsDisplayClosed)

    def _onOptionsModified(self, uid, options):
        for window in list(self._options_windows.get(uid, {}).values()):
            window.close()

    def _onOptionsRemoved(self, uid):
        for window in list(self._options_windows.get(uid, {}).values()):
            window.close()

    def _onBeamDisplayRequested(self, uid):
        window = self._getOptionsWindow(uid, 'beam', _BeamSubWindow)
        self._showWindow(window)
        self.controller().beamDisplayed.emit(uid)

    def _onBeamDisplayClosed(self, uid):
        self._options_windows[uid].pop('beam')

    def _onGeometryDisplayRequested(self, uid):
        window = self._getOptionsWindow(uid, 'geometry', _GeometrySubWindow)
        self._showWindow(window)
        self.controller().geometryDisplayed.emit(uid)

    def _onGeometryDisplayClosed(self, uid):
        self._options_windows[uid].pop('geometry')

    def _onDetectorsDisplayRequested(self, uid):
        window = self._getOptionsWindow(uid, 'detectors', _DetectorsSubWindow)
        self._showWindow(window)
        self.controller().detectorsDisplayed.emit(uid)

    def _onDetectorsDisplayClosed(self, uid):
        self._options_windows[uid].pop('detectors')

    def _onLimitsDisplayRequested(self, uid):
        window = self._getOptionsWindow(uid, 'limits', _LimitsSubWindow)
        self._showWindow(window)
        self.controller().limitsDisplayed.emit(uid)

    def _onLimitsDisplayClosed(self, uid):
        self._options_windows[uid].pop('limits')

    def _onModelsDisplayRequested(self, uid):
        window = self._getOptionsWindow(uid, 'models', _ModelsSubWindow)
        self._showWindow(window)
        self.controller().modelsDisplayed.emit(uid)

    def _onModelsDisplayClosed(self, uid):
        self._options_windows[uid].pop('models')

    def _getOptionsWindow(self, uid, name, clasz):
        window = self._options_windows.get(uid, {}).get(name)
        if window is None:
            window = clasz(uid, self.controller())
            self._options_windows.setdefault(uid, {})[name] = window
        return window

    def _showWindow(self, window):
        if window in self.subWindowList():
            self.setActiveSubWindow(window)
        else:
            self.addSubWindow(window)
        window.showNormal()
        window.raise_()

    def controller(self):
        return self._controller

class _Tree(QTreeWidget):

    def __init__(self, controller, parent=None):
        QTreeWidget.__init__(self, parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.header().close()

        # Variables
        self._controller = controller
        self._options_items = {}

        # Signals
        self.customContextMenuRequested.connect(self._onContextMenu)
        self.itemDoubleClicked.connect(self._onDoubleClicked)

        self.controller().optionsAdded.connect(self._onOptionsAdded)
        self.controller().optionsRemoved.connect(self._onOptionsRemoved)
        self.controller().optionsSaved.connect(self._onOptionsSaved)

        self.controller().beamDisplayed.connect(self._onBeamDisplayed)
        self.controller().beamDisplayClosed.connect(self._onBeamDisplayClosed)
        self.controller().geometryDisplayed.connect(self._onGeometryDisplayed)
        self.controller().geometryDisplayClosed.connect(self._onGeometryDisplayClosed)
        self.controller().detectorsDisplayed.connect(self._onDetectorsDisplayed)
        self.controller().detectorsDisplayClosed.connect(self._onDetectorsDisplayClosed)
        self.controller().limitsDisplayed.connect(self._onLimitsDisplayed)
        self.controller().limitsDisplayClosed.connect(self._onLimitsDisplayClosed)
        self.controller().modelsDisplayed.connect(self._onModelsDisplayed)
        self.controller().modelsDisplayClosed.connect(self._onModelsDisplayClosed)

    def _onContextMenu(self, point):
        item = self.itemAt(point)
        if item is None or not hasattr(item, 'popupMenu'):
            return

        menu = item.popupMenu()
        if menu is None or menu.isEmpty():
            return

        menu.exec_(self.mapToGlobal(point))

    def _onDoubleClicked(self, item, column):
        if not hasattr(item, 'popupMenu'):
            return

        menu = item.popupMenu()
        if menu is None or menu.isEmpty():
            return

        action = menu.defaultAction()
        if action is None:
            return

        action.trigger()

    def _onOptionsAdded(self, uid, options):
        c = self.controller()

        itm_options = _OptionsTreeItem(uid, c, self)
        self._options_items.setdefault(uid, {})['options'] = itm_options

        itm_beam = _BeamTreeItem(uid, c, itm_options)
        self._options_items[uid]['beam'] = itm_beam

        itm_geometry = _GeometryTreeItem(uid, c, itm_options)
        self._options_items[uid]['geometry'] = itm_geometry

        itm_detectors = _DetectorsTreeItem(uid, c, itm_options)
        self._options_items[uid]['detectors'] = itm_detectors

        itm_limits = _LimitsTreeItem(uid, c, itm_options)
        self._options_items[uid]['limits'] = itm_limits

        itm_models = _ModelsTreeItem(uid, c, itm_options)
        self._options_items[uid]['models'] = itm_models

        self.expandItem(itm_options)

    def _onOptionsRemoved(self, uid):
        item = self._options_items.pop(uid)
        self.headerItem().removeChild(item['options'])
        self.setCurrentItem(None) # Hack to ensure refresh of actions

    def _onOptionsSaved(self, uid, filepath):
        self.setCurrentItem(None) # Hack to ensure refresh of actions

    def _onBeamDisplayed(self, uid):
        item = self._options_items[uid]['beam']
        self._itemOpened(item)

    def _onBeamDisplayClosed(self, uid):
        item = self._options_items[uid]['beam']
        self._itemClosed(item)

    def _onGeometryDisplayed(self, uid):
        item = self._options_items[uid]['geometry']
        self._itemOpened(item)

    def _onGeometryDisplayClosed(self, uid):
        item = self._options_items[uid]['geometry']
        self._itemClosed(item)

    def _onDetectorsDisplayed(self, uid):
        item = self._options_items[uid]['detectors']
        self._itemOpened(item)

    def _onDetectorsDisplayClosed(self, uid):
        item = self._options_items[uid]['detectors']
        self._itemClosed(item)

    def _onLimitsDisplayed(self, uid):
        item = self._options_items[uid]['limits']
        self._itemOpened(item)

    def _onLimitsDisplayClosed(self, uid):
        item = self._options_items[uid]['limits']
        self._itemClosed(item)

    def _onModelsDisplayed(self, uid):
        item = self._options_items[uid]['models']
        self._itemOpened(item)

    def _onModelsDisplayClosed(self, uid):
        item = self._options_items[uid]['models']
        self._itemClosed(item)

    def _itemOpened(self, item):
        font = item.font(0)
        font.setUnderline(True)
        item.setFont(0, font)

    def _itemClosed(self, item):
        font = item.font(0)
        font.setUnderline(False)
        item.setFont(0, font)

    def controller(self):
        return self._controller

class MainWindow(QMainWindow):

    def __init__(self, parent):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle("pyMonteCarlo")
        self.setWindowIcon(getIcon('app_icon'))
        self.setAcceptDrops(True)

        # Variables
        self._controller = Controller()

        # Actions
        self._act_new = QAction(getIcon("document-new"), "&New", self)
        self._act_new.setShortcut(QKeySequence.New)
        self._act_open = QAction(getIcon("document-open"), "&Open", self)
        self._act_open.setShortcut(QKeySequence.Open)
        self._act_close = QAction("&Close", self)
        self._act_close.setEnabled(False)
        self._act_save = QAction(getIcon('document-save'), '&Save', self)
        self._act_save.setShortcut(QKeySequence.Save)
        self._act_save.setEnabled(False)
        self._act_saveas = QAction(getIcon('document-save-as'), 'Save as', self)
        self._act_saveas.setShortcut(QKeySequence.SaveAs)
        self._act_saveas.setEnabled(False)
        self._act_preferences = QAction('Preferences', self)
        self._act_preferences.setShortcut(QKeySequence.Preferences)
        self._act_exit = QAction('Exit', self)
        self._act_exit.setShortcut(QKeySequence.Quit)

        self._act_window_cascade = QAction("Cascade", self)
        self._act_window_tile = QAction("Tile", self)
        self._act_window_closeall = QAction("Close all", self)

        self._act_about = QAction("About", self)

        # Widgets
        self._area = _Area(self._controller)
        self._tree = _Tree(self._controller)

        dck_datafile = QDockWidget("Options && Results", self)
        dck_datafile.setAllowedAreas(Qt.LeftDockWidgetArea |
                                     Qt.RightDockWidgetArea)
        dck_datafile.setFeatures(QDockWidget.NoDockWidgetFeatures |
                                 QDockWidget.DockWidgetMovable)
        dck_datafile.setMinimumWidth(200)
        dck_datafile.setWidget(self._tree)

        self._dlg_progress = QProgressDialog()
        self._dlg_progress.setRange(0, 100)
        self._dlg_progress.setModal(True)
        self._dlg_progress.hide()

        # Menu
        mnu_file = self.menuBar().addMenu("&File")
        mnu_file.addAction(self._act_new)
        mnu_file.addAction(self._act_open)
        mnu_file.addSeparator()
        mnu_file.addAction(self._act_close)
        mnu_file.addSeparator()
        mnu_file.addAction(self._act_save)
        mnu_file.addAction(self._act_saveas)
        mnu_file.addSeparator()
        mnu_file.addAction(self._act_preferences)
        mnu_file.addSeparator()
        mnu_file.addAction(self._act_exit)

        mnu_windows = self.menuBar().addMenu("Window")
        mnu_windows.addAction(self._act_window_cascade)
        mnu_windows.addAction(self._act_window_tile)
        mnu_windows.addSeparator()
        mnu_windows.addAction(self._act_window_closeall)

        mnu_help = self.menuBar().addMenu("Help")
        mnu_help.addAction(self._act_about)

        # Toolbar
        tbl_file = self.addToolBar("File")
        tbl_file.setMovable(False)
        tbl_file.addAction(self._act_new)
        tbl_file.addAction(self._act_open)
        tbl_file.addSeparator()
        tbl_file.addAction(self._act_save)
        tbl_file.addAction(self._act_saveas)

        # Layouts
        self.setCentralWidget(self._area)
        self.addDockWidget(Qt.LeftDockWidgetArea, dck_datafile)

        # Signals
        self._act_new.triggered.connect(self._onNew)
        self._act_open.triggered.connect(self._onOpen)
        self._act_save.triggered.connect(self._onSave)
        self._act_saveas.triggered.connect(self._onSaveAs)
        self._act_close.triggered.connect(self._onClose)
        self._act_exit.triggered.connect(self._onExit)
        self._act_window_cascade.triggered.connect(self._onWindowCascade)
        self._act_window_tile.triggered.connect(self._onWindowTile)
        self._act_window_closeall.triggered.connect(self._onWindowCloseall)
        self._act_about.triggered.connect(self._onAbout)

        self._tree.itemSelectionChanged.connect(self._onTreeSelectionChanged)

        self._dlg_progress.canceled.connect(self.controller().optionsOpenCancel)
        self.controller().optionsOpenProgress.connect(self._onDialogProgressProgress)
        self.controller().optionsOpenCancel.connect(self._onDialogProgressCancel)
        self.controller().optionsOpenException.connect(self._onDialogProgressException)

        self._dlg_progress.canceled.connect(self.controller().optionsSaveCancel)
        self.controller().optionsSaveProgress.connect(self._onDialogProgressProgress)
        self.controller().optionsSaveCancel.connect(self._onDialogProgressCancel)
        self.controller().optionsSaveException.connect(self._onDialogProgressException)

        self.controller().optionsNewRequested.connect(self._onOptionsNewRequested)
        self.controller().optionsModifyRequested.connect(self._onOptionsModifyRequested)
        self.controller().optionsSaveRequested.connect(self._onOptionsSaveRequested)
        self.controller().optionsSaveAsRequested.connect(self._onOptionsSaveAsRequested)

        # Defaults
#        settings = self.controller().settings()
#        self.move(settings.value("pos", self.pos()))
#        self.resize(settings.value("size", self.size()))

    def _onNew(self):
        self.controller().optionsNewRequested.emit()

    def _onOpen(self):
        settings = self.controller().settings()
        curdir = getattr(settings, 'opendir', os.getcwd())
        namefilters = {'Options [*.xml] (*.xml)': '.xml',
                       'Results [*.h5] (*.h5)': '.h5'}

        filepath, namefilter = \
            QFileDialog.getOpenFileName(self, "Open", curdir,
                                        ';;'.join(namefilters.keys()))

        if not filepath or not namefilter:
            return
        settings.opendir = os.path.dirname(filepath)

        ext = namefilters[namefilter]
        if not filepath.endswith(ext):
            filepath += ext

        self._dlg_progress.reset()
        self._dlg_progress.show()

        if ext == '.xml':
            self.controller().optionsOpen.emit(filepath)
        else:
            print('Open results')

    def _onSave(self):
        item = self._tree.currentItem()
        if item is None:
            return
        item.requestSave()

    def _onSaveAs(self):
        item = self._tree.currentItem()
        if item is None:
            return
        item.requestSaveAs()

    def _onClose(self):
        item = self._tree.currentItem()
        if item is None:
            return
        item.requestClose()

    def _onExit(self):
        self.close()

    def _onWindowCascade(self):
        self._area.cascadeSubWindows()

    def _onWindowTile(self):
        self._area.tileSubWindows()

    def _onWindowCloseall(self):
        self._area.closeAllSubWindows()

    def _onAbout(self):
        fields = {'version': __version__,
                  'copyright': __copyright__,
                  'license': __license__}
        message = 'pyMonteCarlo (version {version})\n{copyright}\nLicensed under {license}'.format(**fields)
        QMessageBox.about(self, 'About', message)

    def _onTreeSelectionChanged(self):
        item = self._tree.currentItem()
        if item is None:
            self._act_close.setEnabled(False)
            self._act_save.setEnabled(False)
            self._act_saveas.setEnabled(False)
            return

        self._act_close.setEnabled(item.canClose())
        self._act_save.setEnabled(item.canSave())
        self._act_saveas.setEnabled(item.canSaveAs())

    def _onDialogProgressProgress(self, progress, status):
        self._dlg_progress.setValue(progress * 100)
        self._dlg_progress.setLabelText(status)

    def _onDialogProgressCancel(self):
        self._dlg_progress.hide()

    def _onDialogProgressException(self, ex):
        self._dlg_progress.hide()
        messagebox.exception(self, ex)

    def _onOptionsNewRequested(self):
#        dialog = OptionsWizard()
#        if not dialog.exec_():
#            return

        from pymontecarlo.options.options import Options
        from pymontecarlo.options.geometry import HorizontalLayers
        from pymontecarlo.options.material import Material
        from pymontecarlo.options.detector import ElectronFractionDetector
        from pymontecarlo.options.limit import ShowersLimit
        options = Options()
        options.geometry = HorizontalLayers(Material.pure(79))
        options.geometry.add_layer(Material.pure(13), 50e-6)
        options.detectors['fraction'] = ElectronFractionDetector()
        options.limits.add(ShowersLimit(1000))

#        options = dialog.options()
        self.controller().optionsAddRequested.emit(options)

    def _onOptionsModifyRequested(self, uid):
        options = self.controller().options(uid)

        dialog = OptionsWizard(options)
        if not dialog.exec_():
            return

        self.controller().optionsModified.emit(uid, dialog.options())

    def _onOptionsSaveRequested(self, uid):
        filepath = self.controller().optionsFilepath(uid)
        if filepath is None:
            self.controller().optionsSaveAsRequested.emit(uid)
            return

        self._dlg_progress.reset()
        self._dlg_progress.show()
        self.controller().optionsSave.emit(uid, filepath)

    def _onOptionsSaveAsRequested(self, uid):
        settings = self.controller().settings()
        curdir = getattr(settings, "savedir", os.getcwd())

        filepath, namefilter = \
            QFileDialog.getSaveFileName(self, "Save as", curdir,
                                        "Options [*.xml] (*.xml)")

        if not filepath or not namefilter:
            return
        settings.savedir = os.path.dirname(filepath)

        if not filepath.endswith('.xml'):
            filepath += '.xml'

        self._dlg_progress.reset()
        self._dlg_progress.show()
        self.controller().optionsSave.emit(uid, filepath)

    def controller(self):
        return self._controller

def _setup(argv):
    # Configuration directory
    dirpath = os.path.join(os.path.expanduser('~'), '.pymontecarlo')
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    # Logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if '-d' in argv else logging.INFO)

    fmt = '%(asctime)s - %(levelname)s - %(module)s - %(lineno)d: %(message)s'
    formatter = logging.Formatter(fmt)

    handler = logging.FileHandler(os.path.join(dirpath, 'pymontecarlo.log'), 'w')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logging.info('Started pyMonteCarlo')
    logging.info('version = %s', __version__)
    logging.info('operating system = %s %s',
                 platform.system(), platform.release())
    logging.info('machine = %s', platform.machine())
    logging.info('processor = %s', platform.processor())

    # Catch all exceptions
    def _excepthook(exc_type, exc_obj, exc_tb):
        messagebox.exception(None, exc_obj)
        sys.__excepthook__(exc_type, exc_obj, exc_tb)
    sys.excepthook = _excepthook

def run():
    argv = sys.argv
    _setup(argv)
    app = QApplication(argv)
    dialog = MainWindow(None)
    dialog.show()
    app.exec_()

if __name__ == '__main__':
    run()

