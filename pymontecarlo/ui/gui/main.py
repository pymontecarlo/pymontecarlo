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
from PySide.QtCore import Qt, QPoint, QSize

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
from pymontecarlo.ui.gui.results.result import \
    get_widget_class as get_result_widget_class
from pymontecarlo.ui.gui.results.summary import SummaryWidget
from pymontecarlo.ui.gui.configure import ConfigureDialog
from pymontecarlo.ui.gui.runner import RunnerDialog

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

    def addSeparator(self):
        self._menu.addSeparator()

    def setDefaultAction(self, action):
        self._menu.setDefaultAction(action)

    def popupMenu(self):
        return self._menu

class _BaseTreeItem(_ActionTreeItem):

    def __init__(self, uid, controller, parent):
        _ActionTreeItem.__init__(self, controller, parent)

        # Variables
        self._uid = uid

    def uid(self):
        return self._uid

    def canReload(self):
        return False

    def requestReload(self):
        pass

    def canSave(self):
        return False

    def requestSave(self):
        pass

    def canSaveAs(self):
        return False

    def requestSaveAs(self):
        pass

    def canClose(self):
        return False

    def requestClose(self):
        pass

class _OptionsTreeItem(_BaseTreeItem):

    def __init__(self, uid, controller, parent):
        _BaseTreeItem.__init__(self, uid, controller, parent)
        self.setText(0, controller.options(uid).name)
        self.setToolTip(0, controller.optionsFilepath(uid))

        # Actions
        self._act_modify = QAction("Modify", self.treeWidget())
        self.addAction(self._act_modify)
        self.addSeparator()

        self._act_reload = QAction("Reload", self.treeWidget())
        self._act_reload.setEnabled(self.canReload())
        self.addAction(self._act_reload)
        self.addSeparator()

        self._act_save = QAction("Save", self.treeWidget())
        self._act_save.setEnabled(self.canSave())
        self.addAction(self._act_save)

        self._act_saveas = QAction("Save As", self.treeWidget())
        self.addAction(self._act_saveas)
        self.addSeparator()

        self._act_close = QAction("Close", self.treeWidget())
        self.addAction(self._act_close)

        # Signals
        self._act_modify.triggered.connect(self.requestModify)
        self._act_reload.triggered.connect(self.requestReload)
        self._act_save.triggered.connect(self.requestSave)
        self._act_saveas.triggered.connect(self.requestSaveAs)
        self._act_close.triggered.connect(self.requestClose)

        self.controller().optionsModified.connect(self._onOptionsModified)
        self.controller().optionsReloaded.connect(self._onOptionsReloaded)
        self.controller().optionsSaved.connect(self._onOptionsSaved)

    def _onOptionsModified(self, uid, options):
        self._act_save.setEnabled(self.canSave())
        self.setText(0, options.name)

    def _onOptionsReloaded(self, uid, options):
        self.setText(0, options.name)

    def _onOptionsSaved(self, uid, filepath):
        self._act_reload.setEnabled(self.canReload())
        self._act_save.setEnabled(self.canSave())
        self.setToolTip(0, filepath)

    def canReload(self):
        return bool(self.controller().optionsFilepath(self.uid()))

    def requestReload(self):
        self.controller().optionsReloadRequested.emit(self.uid())

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

    def requestModify(self):
        self.controller().optionsModifyRequested.emit(self.uid())

class _BeamTreeItem(_BaseTreeItem):

    def __init__(self, uid, controller, parent):
        _BaseTreeItem.__init__(self, uid, controller, parent)
        self.setText(0, 'Beam')

        # Actions
        act_display = QAction("Display", self.treeWidget())
        self.addAction(act_display)
        self.setDefaultAction(act_display)

        # Signals
        act_display.triggered.connect(self.requestDisplay)

    def requestDisplay(self):
        self.controller().beamDisplayRequested.emit(self.uid())

class _GeometryTreeItem(_BaseTreeItem):

    def __init__(self, uid, controller, parent):
        _BaseTreeItem.__init__(self, uid, controller, parent)
        self.setText(0, 'Geometry')

        # Actions
        act_display = QAction("Display", self.treeWidget())
        self.addAction(act_display)
        self.setDefaultAction(act_display)

        # Signals
        act_display.triggered.connect(self.requestDisplay)

    def requestDisplay(self):
        self.controller().geometryDisplayRequested.emit(self.uid())

class _DetectorsTreeItem(_BaseTreeItem):

    def __init__(self, uid, controller, parent):
        _BaseTreeItem.__init__(self, uid, controller, parent)
        self.setText(0, 'Detectors')

        # Actions
        act_display = QAction("Display", self.treeWidget())
        self.addAction(act_display)
        self.setDefaultAction(act_display)

        # Signals
        act_display.triggered.connect(self.requestDisplay)

    def requestDisplay(self):
        self.controller().detectorsDisplayRequested.emit(self.uid())

class _LimitsTreeItem(_BaseTreeItem):

    def __init__(self, uid, controller, parent):
        _BaseTreeItem.__init__(self, uid, controller, parent)
        self.setText(0, 'Limits')

        # Actions
        act_display = QAction("Display", self.treeWidget())
        self.addAction(act_display)
        self.setDefaultAction(act_display)

        # Signals
        act_display.triggered.connect(self.requestDisplay)

    def requestDisplay(self):
        self.controller().limitsDisplayRequested.emit(self.uid())

class _ModelsTreeItem(_BaseTreeItem):

    def __init__(self, uid, controller, parent):
        _BaseTreeItem.__init__(self, uid, controller, parent)
        self.setText(0, 'Models')

        # Actions
        act_display = QAction("Display", self.treeWidget())
        self.addAction(act_display)
        self.setDefaultAction(act_display)

        # Signals
        act_display.triggered.connect(self.requestDisplay)

    def requestDisplay(self):
        self.controller().modelsDisplayRequested.emit(self.uid())

class _ResultsTreeItem(_BaseTreeItem):

    def __init__(self, uid, controller, parent):
        _BaseTreeItem.__init__(self, uid, controller, parent)
        results = controller.results(uid)
        self.setText(0, results.options.name)
        self.setToolTip(0, controller.resultsFilepath(uid))

        # Actions
        self._act_summary = QAction('Create summary', self.treeWidget())
        self._act_summary.setEnabled(len(results) > 1)
        self.addAction(self._act_summary)
        self.addSeparator()

        self._act_saveas = QAction("Save As", self.treeWidget())
        self.addAction(self._act_saveas)
        self.addSeparator()

        self._act_reload = QAction("Reload", self.treeWidget())
        self.addAction(self._act_reload)
        self.addSeparator()

        self._act_close = QAction("Close", self.treeWidget())
        self.addAction(self._act_close)

        # Signals
        self._act_summary.triggered.connect(self.requestSummary)
        self._act_saveas.triggered.connect(self.requestSaveAs)
        self._act_reload.triggered.connect(self.requestReload)
        self._act_close.triggered.connect(self.requestClose)

        self.controller().resultsSaved.connect(self._onResultsSaved)

    def _onResultsSaved(self, uid, filepath):
        self.setToolTip(0, filepath)

    def requestSummary(self):
        self.controller().summaryDisplayRequested.emit(self.uid())

    def canReload(self):
        return True

    def requestReload(self):
        self.controller().resultsReloadRequested.emit(self.uid())

    def canSaveAs(self):
        return True

    def requestSaveAs(self):
        self.controller().resultsSaveAsRequested.emit(self.uid())

    def canClose(self):
        return True

    def requestClose(self):
        self.controller().resultsRemoveRequested.emit(self.uid())

class _ResultsOptionsTreeItem(_BaseTreeItem):

    def __init__(self, uid, controller, parent):
        _BaseTreeItem.__init__(self, uid, controller, parent)
        self.setText(0, 'Options')

class _ResultsContainerTreeItem(_BaseTreeItem):

    def __init__(self, uid, index, controller, parent):
        _BaseTreeItem.__init__(self, uid, controller, parent)
        container = controller.results(uid)[index]
        self.setText(0, '%i - %s' % (index, container.options.name))

        # Variables
        self._index = index

    def index(self):
        return self._index

class _ResultTreeItem(_BaseTreeItem):

    def __init__(self, uid, index, key, controller, parent):
        _BaseTreeItem.__init__(self, uid, controller, parent)
        self.setText(0, key)

        # Variables
        self._index = index
        self._key = key

        # Actions
        act_display = QAction("Display", self.treeWidget())
        self.addAction(act_display)
        self.setDefaultAction(act_display)

        # Signals
        act_display.triggered.connect(self.requestDisplay)

    def requestDisplay(self):
        self.controller().resultDisplayRequested.emit(self.uid(), self.index(), self.key())

    def index(self):
        return self._index

    def key(self):
        return self._key

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
        return _SubOptionsWidgetSubWindow.closeEvent(self, event)

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
        return _SubOptionsWidgetSubWindow.closeEvent(self, event)

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
        return _SubOptionsWidgetSubWindow.closeEvent(self, event)

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
        return _SubOptionsWidgetSubWindow.closeEvent(self, event)

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
        return _SubOptionsWidgetSubWindow.closeEvent(self, event)

class _ResultSubWindow(_WidgetSubWindow):

    def __init__(self, uid, index, key, controller, parent=None):
        _WidgetSubWindow.__init__(self, controller, parent)
        self.setWindowTitle(key)

        # Variables
        self._uid = uid
        self._index = index
        self._key = key

        # Widgets
        result = controller.result(uid, index, key)
        options = controller.resultsContainer(uid, index).options
        widget_class = get_result_widget_class(result.__class__)
        widget = widget_class(key, result, options)
        self.setWidget(widget)

    def uid(self):
        return self._uid

    def index(self):
        return self._index

    def key(self):
        return self._key

    def closeEvent(self, event):
        self.controller().resultDisplayClosed.emit(self.uid(), self.index(), self.key())
        return _WidgetSubWindow.closeEvent(self, event)

class _SummarySubWindow(_WidgetSubWindow):

    def __init__(self, uid, controller, parent=None):
        _WidgetSubWindow.__init__(self, controller, parent)
        self.setWindowTitle('Summary')

        # Variables
        self._uid = uid

        # Widgets
        results = controller.results(uid)
        widget = SummaryWidget(results)
        self.setWidget(widget)

    def uid(self):
        return self._uid

    def closeEvent(self, event):
        self.controller().summaryDisplayedClosed.emit(self.uid())
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
        self._results_windows = {}

        # Signals
        self.controller().optionsModified.connect(self._onOptionsModified)
        self.controller().optionsRemoveRequestApproved.connect(self._onOptionsRemoveRequestApproved)
        self.controller().optionsReloadRequestApproved.connect(self._onOptionsReloadRequestApproved)

        self.controller().resultsRemoveRequestApproved.connect(self._onResultsRemoveRequestApproved)
        self.controller().resultsReloadRequestApproved.connect(self._onResultsReloadRequestApproved)

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
        self.controller().resultDisplayRequested.connect(self._onResultDisplayRequested)
        self.controller().resultDisplayClosed.connect(self._onResultDisplayClosed)
        self.controller().summaryDisplayRequested.connect(self._onSummaryDisplayRequested)

    def _onOptionsModified(self, uid, options):
        logging.debug('area: optionsModified')
        for window in list(self._options_windows.get(uid, {}).values()):
            window.close()

    def _onOptionsReloadRequestApproved(self, uid):
        logging.debug('area: optionsReloadRequestApproved')
        for window in list(self._options_windows.get(uid, {}).values()):
            window.close()

    def _onOptionsRemoveRequestApproved(self, uid):
        logging.debug('area: optionsRemoveRequestApproved')
        for window in list(self._options_windows.get(uid, {}).values()):
            window.close()

    def _onResultsReloadRequestApproved(self, uid):
        logging.debug('area: resultsReloadRequestApproved')
        for window in list(self._results_windows.get(uid, {}).values()):
            window.close()

        for options_uid in self.controller()._resultsOptionsUIDs(uid).values():
            for window in list(self._options_windows.get(options_uid, {}).values()):
                window.close()

    def _onResultsRemoveRequestApproved(self, uid):
        logging.debug('area: resultsRemoveRequestApproved')
        for window in list(self._results_windows.get(uid, {}).values()):
            window.close()

        for options_uid in self.controller()._resultsOptionsUIDs(uid).values():
            for window in list(self._options_windows.get(options_uid, {}).values()):
                window.close()

    def _onBeamDisplayRequested(self, uid):
        logging.debug('area: beamDisplayRequested')
        window = self._getOptionsWindow(uid, 'beam', _BeamSubWindow)
        self._showWindow(window)
        self.controller().beamDisplayed.emit(uid)

    def _onBeamDisplayClosed(self, uid):
        logging.debug('area: beamDisplayClosed')
        self._options_windows[uid].pop('beam')

    def _onGeometryDisplayRequested(self, uid):
        logging.debug('area: geometryDisplayRequested')
        window = self._getOptionsWindow(uid, 'geometry', _GeometrySubWindow)
        self._showWindow(window)
        self.controller().geometryDisplayed.emit(uid)

    def _onGeometryDisplayClosed(self, uid):
        logging.debug('area: geometryDisplayClosed')
        self._options_windows[uid].pop('geometry')

    def _onDetectorsDisplayRequested(self, uid):
        logging.debug('area: detectorsDisplayRequested')
        window = self._getOptionsWindow(uid, 'detectors', _DetectorsSubWindow)
        self._showWindow(window)
        self.controller().detectorsDisplayed.emit(uid)

    def _onDetectorsDisplayClosed(self, uid):
        logging.debug('area: detectorsDisplayClosed')
        self._options_windows[uid].pop('detectors')

    def _onLimitsDisplayRequested(self, uid):
        logging.debug('area: limitsDisplayRequested')
        window = self._getOptionsWindow(uid, 'limits', _LimitsSubWindow)
        self._showWindow(window)
        self.controller().limitsDisplayed.emit(uid)

    def _onLimitsDisplayClosed(self, uid):
        logging.debug('area: limitsDisplayClosed')
        self._options_windows[uid].pop('limits')

    def _onModelsDisplayRequested(self, uid):
        logging.debug('area: modelsDisplayRequested')
        window = self._getOptionsWindow(uid, 'models', _ModelsSubWindow)
        self._showWindow(window)
        self.controller().modelsDisplayed.emit(uid)

    def _onModelsDisplayClosed(self, uid):
        logging.debug('area: modelsDisplayClosed')
        self._options_windows[uid].pop('models')

    def _onResultDisplayRequested(self, uid, index, key):
        logging.debug('area: resultDisplayRequested')
        window = self._getResultWindow(uid, index, key, _ResultSubWindow)
        self._showWindow(window)
        self.controller().resultDisplayed.emit(uid, index, key)

    def _onResultDisplayClosed(self, uid, index, key):
        logging.debug('area: resultDisplayClosed')
        self._results_windows[uid].pop((index, key))

    def _onSummaryDisplayRequested(self, uid):
        logging.debug('area: summaryDisplayRequested')
        window = _SummarySubWindow(uid, self.controller())
        self._showWindow(window)
        self.controller().summaryDisplayed.emit(uid)

    def _getOptionsWindow(self, uid, name, clasz):
        window = self._options_windows.get(uid, {}).get(name)
        if window is None:
            window = clasz(uid, self.controller())
            self._options_windows.setdefault(uid, {})[name] = window
        return window

    def _getResultWindow(self, uid, index, key, clasz):
        window = self._results_windows.get(uid, {}).get((index, key))
        if window is None:
            window = clasz(uid, index, key, self.controller())
            self._results_windows.setdefault(uid, {})[(index, key)] = window
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
        self._results_items = {}

        # Signals
        self.customContextMenuRequested.connect(self._onContextMenu)
        self.itemDoubleClicked.connect(self._onDoubleClicked)

        self.controller().optionsAdded.connect(self._onOptionsAdded)
        self.controller().optionsRemoveRequestApproved.connect(self._onOptionsRemoveRequestApproved)

        self.controller().resultsAdded.connect(self._onResultsAdded)
        self.controller().resultsRemoveRequestApproved.connect(self._onResultsRemoveRequestApproved)
        self.controller().resultsReloadRequestApproved.connect(self._onResultsReloadRequestApproved)
        self.controller().resultsReloaded.connect(self._onResultsReloaded)

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
        self.controller().resultDisplayed.connect(self._onResultDisplayed)
        self.controller().resultDisplayClosed.connect(self._onResultDisplayClosed)

    def _onContextMenu(self, point):
        logging.debug('tree: contextMenu')
        item = self.itemAt(point)
        if item is None or not hasattr(item, 'popupMenu'):
            return

        menu = item.popupMenu()
        if menu is None or menu.isEmpty():
            return

        menu.exec_(self.mapToGlobal(point))

    def _onDoubleClicked(self, item, column):
        logging.debug('tree: doubleClicked')
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
        logging.debug('tree: optionsAdded')
        c = self.controller()

        itm_options = _OptionsTreeItem(uid, c, self)
        self._options_items.setdefault(uid, {})['root'] = itm_options

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

    def _onOptionsRemoveRequestApproved(self, uid):
        logging.debug('tree: optionsRemoveRequestApproved')
        item = self._options_items.pop(uid)['root']
        self.headerItem().removeChild(item)
        self.setCurrentItem(None) # Hack to ensure refresh of actions

    def _onResultsAdded(self, uid, results):
        logging.debug('tree: resultsAdded')
        c = self.controller()

        def _addOptions(options, index, parent):
            options_uid = c._resultsOptionsUID(uid, index)
            self._options_items.setdefault(options_uid, {})

            itm_beam = _BeamTreeItem(options_uid, c, parent)
            self._options_items[options_uid]['beam'] = itm_beam

            itm_geometry = _GeometryTreeItem(options_uid, c, parent)
            self._options_items[options_uid]['geometry'] = itm_geometry

            itm_detectors = _DetectorsTreeItem(options_uid, c, parent)
            self._options_items[options_uid]['detectors'] = itm_detectors

            itm_limits = _LimitsTreeItem(options_uid, c, parent)
            self._options_items[options_uid]['limits'] = itm_limits

            itm_models = _ModelsTreeItem(options_uid, c, parent)
            self._options_items[options_uid]['models'] = itm_models

            return options_uid

        # Root results

        itm_results = _ResultsTreeItem(uid, c, self)
        self._results_items.setdefault(uid, {})['root'] = itm_results

        itm_options = _ResultsOptionsTreeItem(uid, c, itm_results)
        options_uid = _addOptions(results.options, 'base', itm_options)
        self._results_items[uid].setdefault('options', set()).add(options_uid)

        # Containers
        for index, container in enumerate(results):
            itm_container = _ResultsContainerTreeItem(uid, index, c, itm_results)

            itm_options = _ResultsOptionsTreeItem(uid, c, itm_container)
            options_uid = _addOptions(container.options, index, itm_options)
            self._results_items[uid]['options'].add(options_uid)

            for key in container.keys():
                itm_result = _ResultTreeItem(uid, index, key, c, itm_container)
                self._results_items[uid][(index, key)] = itm_result

        self.expandItem(itm_results)

    def _onResultsRemoveRequestApproved(self, uid):
        logging.debug('tree: resultsRemoveRequestApproved')
        items = self._results_items.pop(uid)

        for options_uid in items['options']:
            self._options_items.pop(options_uid)

        self.headerItem().removeChild(items['root'])
        self.setCurrentItem(None) # Hack to ensure refresh of actions

    def _onResultsReloadRequestApproved(self, uid):
        logging.debug('tree: resultsReloadRequestApproved')
        self._onResultsRemoveRequestApproved(uid)

    def _onResultsReloaded(self, uid, results):
        logging.debug('tree: resultsReloaded')
        self._onResultsAdded(uid, results)

    def _onBeamDisplayed(self, uid):
        logging.debug('tree: beamDisplayed')
        item = self._options_items[uid]['beam']
        self._itemOpened(item)

    def _onBeamDisplayClosed(self, uid):
        logging.debug('tree: beamDisplayClosed')
        item = self._options_items[uid]['beam']
        self._itemClosed(item)

    def _onGeometryDisplayed(self, uid):
        logging.debug('tree: geometryDisplayed')
        item = self._options_items[uid]['geometry']
        self._itemOpened(item)

    def _onGeometryDisplayClosed(self, uid):
        logging.debug('tree: geometryDisplayClosed')
        item = self._options_items[uid]['geometry']
        self._itemClosed(item)

    def _onDetectorsDisplayed(self, uid):
        logging.debug('tree: detectorsDisplayed')
        item = self._options_items[uid]['detectors']
        self._itemOpened(item)

    def _onDetectorsDisplayClosed(self, uid):
        logging.debug('tree: detectorsDisplayClosed')
        item = self._options_items[uid]['detectors']
        self._itemClosed(item)

    def _onLimitsDisplayed(self, uid):
        logging.debug('tree: limitsDisplayed')
        item = self._options_items[uid]['limits']
        self._itemOpened(item)

    def _onLimitsDisplayClosed(self, uid):
        logging.debug('tree: limitsDisplayClosed')
        item = self._options_items[uid]['limits']
        self._itemClosed(item)

    def _onModelsDisplayed(self, uid):
        logging.debug('tree: modelsDisplayed')
        item = self._options_items[uid]['models']
        self._itemOpened(item)

    def _onModelsDisplayClosed(self, uid):
        logging.debug('tree: modelsDisplayClosed')
        item = self._options_items[uid]['models']
        self._itemClosed(item)

    def _onResultDisplayed(self, uid, index, key):
        logging.debug('tree: resultDisplayed')
        item = self._results_items[uid][(index, key)]
        self._itemOpened(item)

    def _onResultDisplayClosed(self, uid, index, key):
        logging.debug('tree: resultDisplayClosed')
        item = self._results_items[uid][(index, key)]
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

    def requestCloseAll(self):
        for uid in list(self._results_items.keys()):
            self._results_items[uid]['root'].requestClose()
        for uid in list(self._options_items.keys()):
            self._options_items[uid]['root'].requestClose()

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
        self._act_reload = QAction(getIcon('document-revert'), 'Reload', self)
        self._act_reload.setShortcut(QKeySequence.Refresh)
        self._act_reload.setEnabled(False)
        self._act_close = QAction("&Close", self)
        self._act_close.setShortcut(QKeySequence.Close)
        self._act_close.setEnabled(False)
        self._act_closeall = QAction("Close all", self)
        self._act_closeall.setEnabled(False)
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

        self._act_run = QAction(getIcon("media-playback-start"), 'Run simulations', self)
        self._act_run.setShortcut(QKeySequence(Qt.Key_F5))

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

        self._dlg_runner = RunnerDialog()
        self._dlg_runner.hide()

        # Menu
        mnu_file = self.menuBar().addMenu("&File")
        mnu_file.addAction(self._act_new)
        mnu_file.addAction(self._act_open)
        mnu_file.addAction(self._act_reload)
        mnu_file.addSeparator()
        mnu_file.addAction(self._act_close)
        mnu_file.addAction(self._act_closeall)
        mnu_file.addSeparator()
        mnu_file.addAction(self._act_save)
        mnu_file.addAction(self._act_saveas)
        mnu_file.addSeparator()
        mnu_file.addAction(self._act_preferences)
        mnu_file.addSeparator()
        mnu_file.addAction(self._act_exit)

        mnu_windows = self.menuBar().addMenu("Window")
        mnu_windows.addAction(self._act_run)
        mnu_windows.addSeparator()
        mnu_windows.addAction(self._act_window_cascade)
        mnu_windows.addAction(self._act_window_tile)
        mnu_windows.addSeparator()
        mnu_windows.addAction(self._act_window_closeall)

        mnu_help = self.menuBar().addMenu("Help")
        mnu_help.addAction(self._act_about)

        # Toolbar
        tlb_file = self.addToolBar("File")
        tlb_file.setMovable(False)
        tlb_file.addAction(self._act_new)
        tlb_file.addAction(self._act_open)
        tlb_file.addSeparator()
        tlb_file.addAction(self._act_save)
        tlb_file.addAction(self._act_saveas)
        tlb_file.addSeparator()
        tlb_file.addAction(self._act_run)

        # Layouts
        self.setCentralWidget(self._area)
        self.addDockWidget(Qt.LeftDockWidgetArea, dck_datafile)

        # Signals
        self._act_new.triggered.connect(self._onNew)
        self._act_open.triggered.connect(self._onOpen)
        self._act_reload.triggered.connect(self._onReload)
        self._act_save.triggered.connect(self._onSave)
        self._act_saveas.triggered.connect(self._onSaveAs)
        self._act_close.triggered.connect(self._onClose)
        self._act_closeall.triggered.connect(self._onCloseAll)
        self._act_preferences.triggered.connect(self._onPreferences)
        self._act_exit.triggered.connect(self._onExit)
        self._act_run.triggered.connect(self._onRun)
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

        self._dlg_progress.canceled.connect(self.controller().resultsOpenCancel)
        self.controller().resultsOpenProgress.connect(self._onDialogProgressProgress)
        self.controller().resultsOpenCancel.connect(self._onDialogProgressCancel)
        self.controller().resultsOpenException.connect(self._onDialogProgressException)

        self._dlg_progress.canceled.connect(self.controller().resultsSaveCancel)
        self.controller().resultsSaveProgress.connect(self._onDialogProgressProgress)
        self.controller().resultsSaveCancel.connect(self._onDialogProgressCancel)
        self.controller().resultsSaveException.connect(self._onDialogProgressException)

        self.controller().optionsNewRequested.connect(self._onOptionsNewRequested)
        self.controller().optionsOpenRequested.connect(self._onOptionsOpenRequested)
        self.controller().optionsReloadRequested.connect(self._onOptionsReloadRequested)
        self.controller().optionsModifyRequested.connect(self._onOptionsModifyRequested)
        self.controller().optionsSaveRequested.connect(self._onOptionsSaveRequested)
        self.controller().optionsSaveAsRequested.connect(self._onOptionsSaveAsRequested)
        self.controller().optionsSaved.connect(self._onOptionsSaved)
        self.controller().optionsOpened.connect(self._onOptionsOpened)
        self.controller().optionsAddRequested.connect(self._onOptionsAddRequested)
        self.controller().optionsAdded.connect(self._onTreeChanged)
        self.controller().optionsAdded.connect(self._onOptionsAdded)
        self.controller().optionsRemoveRequested.connect(self._onOptionsRemoveRequested)
        self.controller().optionsRemoved.connect(self._onTreeChanged)
        self.controller().optionsModified.connect(self._onOptionsModified)

        self.controller().resultsSaveAsRequested.connect(self._onResultsSaveAsRequested)
        self.controller().resultsReloadRequested.connect(self._onResultsReloadRequested)
        self.controller().resultsOpened.connect(self._onResultsOpened)
        self.controller().resultsReloaded.connect(self._onResultsReloaded)
        self.controller().resultsAddRequested.connect(self._onResultsAddRequested)
        self.controller().resultsAdded.connect(self._onTreeChanged)
        self.controller().resultsRemoveRequested.connect(self._onResultsRemoveRequested)
        self.controller().resultsRemoved.connect(self._onTreeChanged)
        self.controller().resultsSaved.connect(self._onResultsSaved)

        # Defaults
        settings = self.controller().settings()
        section = settings.add_section('gui')
        if hasattr(section, 'position'):
            pos = list(map(int, section.position.split(',')))
            self.move(QPoint(*pos))
        if hasattr(section, 'size'):
            size = list(map(int, section.size.split(',')))
            self.resize(QSize(*size))

    def _onNew(self):
        logging.debug('main: new')
        self.controller().optionsNewRequested.emit()

    def _onOpen(self):
        logging.debug('main: open')
        self.controller().optionsOpenRequested.emit()

    def _onReload(self):
        logging.debug('main: reload')
        item = self._tree.currentItem()
        if item is None:
            return
        item.requestReload()

    def _onSave(self):
        logging.debug('main: save')
        item = self._tree.currentItem()
        if item is None:
            return
        item.requestSave()

    def _onSaveAs(self):
        logging.debug('main: saveAs')
        item = self._tree.currentItem()
        if item is None:
            return
        item.requestSaveAs()

    def _onClose(self):
        logging.debug('main: close')
        item = self._tree.currentItem()
        if item is None:
            return
        item.requestClose()

    def _onCloseAll(self):
        logging.debug('main: closeAll')
        self._tree.requestCloseAll()

    def _onPreferences(self):
        logging.debug('main: preferences')
        dialog = ConfigureDialog()
        dialog.exec_()

    def _onExit(self):
        logging.debug('main: exit')
        self.close()

    def _onRun(self):
        logging.debug('main: run')
        self._dlg_runner.show()

    def _onWindowCascade(self):
        logging.debug('main: windowCascade')
        self._area.cascadeSubWindows()

    def _onWindowTile(self):
        logging.debug('main: windowTile')
        self._area.tileSubWindows()

    def _onWindowCloseall(self):
        logging.debug('main: windowCloseAll')
        self._area.closeAllSubWindows()

    def _onAbout(self):
        logging.debug('main: about')
        fields = {'version': __version__,
                  'copyright': __copyright__,
                  'license': __license__}
        message = 'pyMonteCarlo (version {version})\n{copyright}\nLicensed under {license}'.format(**fields)
        QMessageBox.about(self, 'About', message)

    def _onTreeSelectionChanged(self):
        logging.debug('main: treeSelectionChanged')
        item = self._tree.currentItem()
        if item is None:
            self._act_reload.setEnabled(False)
            self._act_close.setEnabled(False)
            self._act_save.setEnabled(False)
            self._act_saveas.setEnabled(False)
            return

        self._act_reload.setEnabled(item.canReload())
        self._act_close.setEnabled(item.canClose())
        self._act_save.setEnabled(item.canSave())
        self._act_saveas.setEnabled(item.canSaveAs())

    def _onTreeChanged(self):
        logging.debug('main: treeChanged')
        self._act_closeall.setEnabled(self._tree.topLevelItemCount() > 0)

    def _onDialogProgressProgress(self, progress, status):
#        logging.debug('main: dialogProgressProgress')
        self._dlg_progress.setValue(progress * 100)
        self._dlg_progress.setLabelText(status)

    def _onDialogProgressCancel(self):
        logging.debug('main: dialogProgressCancel')
        self._dlg_progress.hide()

    def _onDialogProgressException(self, ex):
        logging.debug('main: dialogProgressException')
        self._dlg_progress.hide()
        messagebox.exception(self, ex)

    def _onOptionsNewRequested(self):
        logging.debug('main: optionsNewRequested')
        dialog = OptionsWizard()
        if not dialog.exec_():
            return
        options = dialog.options()
        self.controller().optionsAddRequested.emit(options, None)

    def _onOptionsOpenRequested(self):
        logging.debug('main: optionsOpenRequested')
        settings = self.controller().settings()
        curdir = getattr(settings.gui, 'opendir', os.getcwd())
        namefilters = {'Options [*.xml] (*.xml)': '.xml',
                       'Results [*.h5] (*.h5)': '.h5'}

        filepath, namefilter = \
            QFileDialog.getOpenFileName(self, "Open", curdir,
                                        ';;'.join(namefilters.keys()))

        if not filepath or not namefilter:
            return
        settings.gui.opendir = os.path.dirname(filepath)

        ext = namefilters[namefilter]
        if not filepath.endswith(ext):
            filepath += ext

        if ext == '.xml' and not self.controller().canOpenOptions(filepath):
            QMessageBox.critical(self, 'Open', 'Options already opened')
            return
        elif ext == '.h5' and not self.controller().canOpenResults(filepath):
            QMessageBox.critical(self, 'Open', 'Results already opened')
            return

        if ext == '.xml':
            self.controller().optionsOpen.emit(filepath)
        elif ext == '.h5':
            self.controller().resultsOpen.emit(filepath)

        self._dlg_progress.reset()
        self._dlg_progress.show()

    def _onOptionsReloadRequested(self, uid):
        logging.debug('main: optionsReloadRequested')
        if not self._checkOptionsSave(uid):
            return

        self.controller().optionsReloadRequestApproved.emit(uid)
        self.controller().optionsReload.emit(uid)
        self._dlg_progress.reset()
        self._dlg_progress.show()

    def _onOptionsModifyRequested(self, uid):
        logging.debug('main: optionsModifyRequested')
        options = self.controller().options(uid)

        dialog = OptionsWizard(options)
        if not dialog.exec_():
            return

        self.controller().optionsModified.emit(uid, dialog.options())

    def _onOptionsSaveRequested(self, uid):
        logging.debug('main: optionsSaveRequested')
        filepath = self.controller().optionsFilepath(uid)
        if not filepath:
            self.controller().optionsSaveAsRequested.emit(uid)
            return

        self._dlg_progress.reset()
        self._dlg_progress.show()
        self.controller().optionsSave.emit(uid, filepath)

    def _onOptionsSaveAsRequested(self, uid):
        logging.debug('main: optionsSaveAsRequested')
        settings = self.controller().settings()
        curdir = getattr(settings.gui, "savedir", os.getcwd())

        filepath, namefilter = \
            QFileDialog.getSaveFileName(self, "Save as", curdir,
                                        "Options [*.xml] (*.xml)")

        if not filepath or not namefilter:
            return
        settings.gui.savedir = os.path.dirname(filepath)

        if not filepath.endswith('.xml'):
            filepath += '.xml'

        self._dlg_progress.reset()
        self._dlg_progress.show()
        self.controller().optionsSave.emit(uid, filepath)

    def _onOptionsOpened(self, options, filepath):
        logging.debug('main: optionsOpened')
        self._dlg_progress.hide()

    def _onOptionsReloaded(self, uid, options):
        logging.debug('main: optionsReloaded')
        self._dlg_progress.hide()

    def _onOptionsAddRequested(self, options, filepath):
        logging.debug('main: optionsAddRequested')
        self.controller().optionsAddRequestApproved.emit(options, filepath)

    def _onOptionsAdded(self, uid, options):
        logging.debug('main: optionsAdded')
        try:
            self._dlg_runner.addAvailableOptions(options)
        except:
            pass

    def _onOptionsModified(self, uid, options):
        logging.debug('main: optionsModified')
        try:
            self._dlg_runner.addAvailableOptions(options)
        except:
            pass

    def _onOptionsRemoveRequested(self, uid):
        logging.debug('main: optionsRemoveRequested')
        if not self._checkOptionsSave(uid):
            return
        self.controller().optionsRemoveRequestApproved.emit(uid)

    def _onOptionsSaved(self, uid, filepath):
        logging.debug('main: optionsSaved')
        self._dlg_progress.hide()

        QMessageBox.information(self, 'pyMonteCarlo', 'Saved')

        self._act_save.setEnabled(False)

    def _onResultsSaveAsRequested(self, uid):
        logging.debug('main: resultsSaveAsRequested')
        settings = self.controller().settings()
        curdir = getattr(settings.gui, "savedir", os.getcwd())

        filepath, namefilter = \
            QFileDialog.getSaveFileName(self, "Save as", curdir,
                                        "Results [*.h5] (*.h5)")

        if not filepath or not namefilter:
            return
        settings.gui.savedir = os.path.dirname(filepath)

        if not filepath.endswith('.h5'):
            filepath += '.h5'

        self._dlg_progress.reset()
        self._dlg_progress.show()
        self.controller().resultsSave.emit(uid, filepath)

    def _onResultsReloadRequested(self, uid):
        logging.debug('main: resultsReloadSRequested')
        self.controller().resultsReloadRequestApproved.emit(uid)
        self.controller().resultsReload.emit(uid)
        self._dlg_progress.reset()
        self._dlg_progress.show()

    def _onResultsOpened(self, results, filepath):
        logging.debug('main: resultsOpened')
        self._dlg_progress.hide()

    def _onResultsReloaded(self, uid, results):
        logging.debug('main: resultsReloaded')
        self._dlg_progress.hide()

    def _onResultsSaved(self, uid, filepath):
        logging.debug('main: resultsSaved')
        self._dlg_progress.hide()
        QMessageBox.information(self, 'pyMonteCarlo', 'Saved')

    def _onResultsAddRequested(self, options, filepath):
        logging.debug('main: resultsAddRequested')
        self.controller().resultsAddRequestApproved.emit(options, filepath)

    def _onResultsRemoveRequested(self, uid):
        logging.debug('main: resultsRemoveRequested')
        self.controller().resultsRemoveRequestApproved.emit(uid)

    def _checkOptionsSave(self, uid):
        if not self.controller().isOptionsEdited(uid):
            return True

        message = 'Modifications not saved. Do you want to continue?'
        answer = QMessageBox.question(self, 'Save modification', message,
                                      QMessageBox.Yes | QMessageBox.No)
        if answer == QMessageBox.Yes:
            return True
        elif answer == QMessageBox.No:
            return False

    def closeEvent(self, event):
        if self._dlg_runner.is_running():
            message = 'Runner is running. Do you want to continue?'
            answer = QMessageBox.question(self, 'Runner', message,
                                          QMessageBox.Yes | QMessageBox.No)
            if answer == QMessageBox.No:
                event.ignore()
                return

        self._dlg_runner.close()

        settings = self.controller().settings()
        section = settings.add_section('gui')

        pos = self.pos()
        section.position = '%i,%i' % (pos.x(), pos.y())

        size = self.size()
        section.size = '%i,%i' % (size.width(), size.height())

        settings.write()

        event.accept()

    def controller(self):
        return self._controller

def _setup(argv):
    # Configuration directory
    dirpath = os.path.join(os.path.expanduser('~'), '.pymontecarlo')
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    
    # Redirect stdout and stderr when frozen
    if getattr(sys, 'frozen', False):
        ## Note: Important since warnings required sys.stderr not be None
        filepath = os.path.join(dirpath, 'pymontecarlo.stdout')
        sys.stdout = open(filepath, 'w')

        filepath = os.path.join(dirpath, 'pymontecarlo.stderr')
        sys.stderr = open(filepath, 'w')

    # Logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if '-d' in argv else logging.INFO)

    fmt = '%(asctime)s - %(levelname)s - %(module)s - %(lineno)d: %(message)s'
    formatter = logging.Formatter(fmt)

    handler = logging.FileHandler(os.path.join(dirpath, 'pymontecarlo.log'), 'w')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if not getattr(sys, 'frozen', False):
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

    # Output sys.path
    logging.info("sys.path = %s", sys.path)

    # Output environment variables
    logging.info('ENVIRON = %s' % os.environ)

def run():
    argv = sys.argv
    _setup(argv)
    app = QApplication(argv)
    dialog = MainWindow(None)
    dialog.show()
    app.exec_()

if __name__ == '__main__':
    run()

