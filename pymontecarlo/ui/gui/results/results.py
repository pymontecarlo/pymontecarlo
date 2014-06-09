#!/usr/bin/env python
"""
================================================================================
:mod:`results` -- Results widget
================================================================================

.. module:: results
   :synopsis: Results widget

.. inheritance-diagram:: pymontecarlo.ui.gui.results.results

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import csv
import sys

# Third party modules.
from PySide.QtGui import \
    (QWidget, QVBoxLayout, QFormLayout, QSplitter, QToolBar, QLabel,
     QHBoxLayout, QSizePolicy, QToolBox, QApplication, QFileDialog, QAction)
from PySide.QtCore import Qt, Signal

import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4'] = 'PySide'
from matplotlib.backends.backend_qt4agg import \
    (FigureCanvasQTAgg as FigureCanvas,
     NavigationToolbar2QTAgg as NavigationToolbar)

# Local modules.
from pymontecarlo.settings import get_settings

from pymontecarlo.ui.gui.util.tango import getIcon

# Globals and constants variables.

class _BaseResultToolItem(QWidget):

    stateChanged = Signal()

    def __init__(self, parent):
        QWidget.__init__(self, parent)

        # Variables
        self._options = parent.options()

        # Layouts
        layout = QVBoxLayout()
        layout.addLayout(self._initUI())
        layout.addStretch()
        self.setLayout(layout)

    def _initUI(self):
        layout = QFormLayout()
        if sys.platform == 'darwin': # Fix for Mac OS
            layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        return layout

    def options(self):
        return self._options

class _BaseResultWidget(QWidget):

    def __init__(self, options, parent=None):
        QWidget.__init__(self, parent)

        # Variables
        self._options = options

        # Widgets
        self._lbl_title = QLabel("Untitled")
        font = self._lbl_title.font()
        font.setBold(True)
        font.setPointSize(14)
        self._lbl_title.setFont(font)

        self._lbl_subtitle = QLabel("")
        font = self._lbl_subtitle.font()
        font.setItalic(True)
        font.setPointSize(14)
        self._lbl_subtitle.setFont(font)

        # Layouts
        layout = QVBoxLayout()

        sublayout = QHBoxLayout()
        sublayout.addWidget(self._lbl_title)
        sublayout.addStretch()
        sublayout.addWidget(self._lbl_subtitle)
        layout.addLayout(sublayout)

        wdglayout = QVBoxLayout()
        wdglayout.addLayout(self._initUI(), 1)
        wdglayout.addWidget(self._initToolbar())

        toolbox = self._initToolbox()
        if toolbox.count() == 0:
            layout.addLayout(wdglayout)
        else:
            wdg_dummy = QWidget()
            wdg_dummy.setLayout(wdglayout)

            splitter = QSplitter()
            splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            splitter.addWidget(wdg_dummy)
            splitter.addWidget(toolbox)
            splitter.setCollapsible(0, False)
            splitter.setCollapsible(1, True)
            layout.addWidget(splitter)

        self.setLayout(layout)

    def _initUI(self):
        return QVBoxLayout()

    def _initToolbar(self):
        return QToolBar()

    def _initToolbox(self):
        return QToolBox()

    def options(self):
        return self._options

    def title(self):
        return self._lbl_title.text()

    def setTitle(self, title):
        self._lbl_title.setText(title)

    def subTitle(self):
        return self._lbl_subtitle.text()

    def setSubTitle(self, subtitle):
        self._lbl_subtitle.setText(subtitle)

class _SaveableResultMixin(object):

    def __init__(self):
        self._save_namefilters = {}
        self._save_methods = {}

        self._register_save_method('CSV file', ('csv',), self._save_csv)

    def _initToolbar(self):
        toolbar = super(_SaveableResultMixin, self)._initToolbar()

        # Actions
        act_copy = toolbar.addAction(getIcon('edit-copy'), 'Copy')
        act_save = toolbar.addAction(getIcon('document-save'), 'Save')

        # Signals
        act_copy.triggered.connect(self.copy)
        act_save.triggered.connect(self.save)

        return toolbar

    def _register_save_method(self, ext_name, exts, method):
        ext_text = ' '.join('*.' + ext for ext in exts)
        namefilter = '%s [%s] (%s)' % (ext_name, ext_text, ext_text)
        self._save_namefilters[namefilter] = exts
        for ext in exts:
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

        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def save(self):
        settings = get_settings()
        section = settings.add_section('gui')
        curdir = getattr(section, 'savedir', os.getcwd())
        namefilters = ';;'.join(sorted(self._save_namefilters.keys()))

        filepath, namefilter = \
            QFileDialog.getSaveFileName(self, "Save", curdir, namefilters)

        if not filepath:
            return
        section.savedir = os.path.dirname(filepath)

        exts = self._save_namefilters[namefilter]
        if not any(filter(lambda ext: filepath.endswith(ext), exts)):
            filepath += '.' + exts[0]

        ext = os.path.splitext(filepath)[1][1:]
        method = self._save_methods.get(ext)
        if method is not None:
            method(filepath)

    def _save_csv(self, filepath):
        with open(filepath, 'w') as fp:
            writer = csv.writer(fp)
            writer.writerows(self.dump())

class _FigureResultMixin(_SaveableResultMixin):

    def __init__(self):
        _SaveableResultMixin.__init__(self)

    def _createFigure(self):
        raise NotImplementedError

    def _drawFigure(self):
        self._ax.relim()
        self._ax.autoscale_view(True, True, True)
        self._canvas.draw()

    def _initUI(self):
        # Variables
        figure = self._createFigure()

        # Widgets
        self._canvas = FigureCanvas(figure)
        self._canvas.setFocusPolicy(Qt.StrongFocus)
        self._canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._canvas.updateGeometry()

        # Layouts
        layout = super(_FigureResultMixin, self)._initUI()
        layout.addWidget(self._canvas, 1)

        # Defaults
        for ext_name, exts in \
                self._canvas.get_supported_filetypes_grouped().items():
            self._register_save_method(ext_name, exts, self._canvas.print_figure)

        return layout

    def _initToolbar(self):
        toolbar = NavigationToolbar(self._canvas, self.parent())

        act_save = toolbar._actions['save_figure']

        act_copy = QAction(getIcon('edit-copy'), 'Copy', toolbar)
        toolbar.insertAction(act_save, act_copy)

        # Signals
        act_save.triggered.disconnect(toolbar.save_figure)
        act_save.triggered.connect(self.save)

        act_copy.triggered.connect(self.copy)

        return toolbar
