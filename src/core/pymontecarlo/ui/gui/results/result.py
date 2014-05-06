#!/usr/bin/env python
"""
================================================================================
:mod:`result` -- Result widgets
================================================================================

.. module:: result
   :synopsis: Result widgets

.. inheritance-diagram:: pymontecarlo.ui.gui.results.result

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.
from PySide.QtGui import QWidget, QLabel, QVBoxLayout, QHBoxLayout

# Local modules.
from pymontecarlo.util.human import camelcase_to_words

# Globals and constants variables.

class _ResultWidget(QWidget):

    def __init__(self, key, result, options, parent=None):
        QWidget.__init__(self, parent)

        # Variables
        self._options = options
        self._key = key
        self._result = result

        # Widgets
        lbl_key = QLabel(key)
        font = lbl_key.font()
        font.setBold(True)
        font.setPointSize(14)
        lbl_key.setFont(font)

        lbl_class = QLabel(camelcase_to_words(result.__class__.__name__[:-6]))
        font = lbl_class.font()
        font.setItalic(True)
        font.setPointSize(14)
        lbl_class.setFont(font)

        # Layouts
        layout = QVBoxLayout()

        sublayout = QHBoxLayout()
        sublayout.addWidget(lbl_key)
        sublayout.addStretch()
        sublayout.addWidget(lbl_class)
        layout.addLayout(sublayout)

        layout.addLayout(self._initUI())

        self.setLayout(layout)

    def _initUI(self):
        return QVBoxLayout()

    @property
    def options(self):
        return self._options

    @property
    def key(self):
        return self._key

    @property
    def result(self):
        return self._result

