#!/usr/bin/env python
"""
================================================================================
:mod:`widget` -- Common widgets
================================================================================

.. module:: widget
   :synopsis: Common widgets

.. inheritance-diagram:: pymontecarlo.ui.gui.util.widget

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import re
import math

# Third party modules.
from PySide.QtGui import \
    (QWidget, QLineEdit, QPushButton, QHBoxLayout, QFileDialog, QComboBox,
     QValidator)
from PySide.QtCore import Signal

import numpy as np

# Local modules.
import pymontecarlo.ui.gui.util.messagebox as messagebox

# Globals and constants variables.

class _BrowseWidget(QWidget):

    pathChanged = Signal(str)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        # Variables
        self._basedir = None

        # Widgets
        self._txt_path = QLineEdit()
        self._txt_path.setReadOnly(True)

        btn_browse = QPushButton("Browse")

        # Layouts
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._txt_path, 1)
        layout.addWidget(btn_browse)
        self.setLayout(layout)

        # Signal
        btn_browse.released.connect(self._onBrowse)

    def _showDialog(self, basedir):
        raise NotImplementedError

    def _validatePath(self, path):
        raise NotImplementedError

    def _onBrowse(self):
        oldpath = self.path()
        newpath = self._showDialog(self.baseDir())

        if not newpath and not oldpath:
            return
        elif not newpath and oldpath:
            newpath = oldpath
        else:
            self.pathChanged.emit(newpath)

        try:
            self.setPath(newpath)
        except Exception as ex:
            messagebox.exception(self, ex)

    def setBaseDir(self, path):
        if not path:
            path = os.getcwd()

        if os.path.isfile(path):
            path = os.path.dirname(path)

        if not os.path.isdir(path):
            raise ValueError('%s is not a directory' % path)

        self._basedir = path

    def baseDir(self):
        return self._basedir or os.getcwd()

    def setPath(self, path, update_basedir=True):
        if not path:
            self._txt_path.setText('')
            self.pathChanged.emit(None)
            return

        path = os.path.abspath(path)

        self._validatePath(path)

        self._txt_path.setText(path)
        self._txt_path.setCursorPosition(0)

        if update_basedir:
            self.setBaseDir(path)
            os.chdir(self.baseDir())

        self.pathChanged.emit(path)

    def path(self):
        """
        Returns the path to the selected file.
        If no file is selected, the method returns ``None``
        """
        path = self._txt_path.text()
        return path if path else None

class FileBrowseWidget(_BrowseWidget):

    def __init__(self, parent=None):
        _BrowseWidget.__init__(self, parent=parent)

        # Variables
        self._namefilters = []

    def _showDialog(self, basedir):
        filter = ';;'.join(self.nameFilters())
        return QFileDialog.getOpenFileName(self, "Browse file", basedir, filter)[0]

    def _validatePath(self, path):
        if os.path.splitext(path)[1] != '.app' and not os.path.isfile(path):
            raise ValueError('%s is not a file' % path)

    def setNameFilter(self, filter):
        self._namefilters.clear()
        self._namefilters.append(filter)

    def setNameFilters(self, filters):
        self._namefilters.clear()
        self._namefilters.extend(filters)

    def nameFilters(self):
        return list(self._namefilters)

class DirBrowseWidget(_BrowseWidget):

    def _showDialog(self, basedir):
        return QFileDialog.getExistingDirectory(self, "Browse directory", basedir)

    def _validatePath(self, path):
        if not os.path.isdir(path):
            raise ValueError('%s is not a directory' % path)

class NumericalValidator(object):

    def validate(self, value):
        raise NotImplementedError

class NumericalLineEdit(QLineEdit):

    class _Validator(QValidator):

        def __init__(self):
            QValidator.__init__(self)
            self._validator = None

        def validate(self, text, pos):
            try:
                value = float(text)
            except:
                return QValidator.Intermediate

            if self.validator() is None:
                return QValidator.Acceptable

            return self.validator().validate(value)

        def fixup(self, text):
            return text

        def validator(self):
            return self._validator

        def setValidator(self, validator):
            self._validator = validator

    def __init__(self, parent=None):
        QLineEdit.__init__(self, parent)
        QLineEdit.setValidator(self, self._Validator())

    def setText(self, text):
        value = float(text)
        self.setValue(value)

    def text(self):
        return str(self.value())

    def value(self):
        text = QLineEdit.text(self)
        return float(text)

    def setValue(self, value):
        QLineEdit.setText(self, str(value))

    def validator(self):
        return QLineEdit.validator(self).validator()

    def setValidator(self, validator):
        return QLineEdit.validator(self).setValidator(validator)

class MultiNumericalLineEdit(QLineEdit):

    _VALUE_SEPARATOR = ';'
    _PATTERN = r'(?P<start>inf|[\de\.+\-]*)(?:\:(?P<stop>[\de\.+\-]*))?(?:\:(?P<step>[\de\.+\-]*))?'

    @classmethod
    def _parse_text(cls, text):
        values = []

        for part in text.split(cls._VALUE_SEPARATOR):
            part = part.strip()
            if not part:
                continue

            match = re.match(cls._PATTERN, part)
            if not match:
                raise ValueError('Invalid part: %s' % part)

            start = float(match.group('start'))
            stop = float(match.group('stop') or start + 1)
            step = float(match.group('step') or 1)

            if math.isinf(start):
                values.append(start)
            else:
                values.extend(np.arange(start, stop, step))

        return np.array(values)

    class _Validator(QValidator):

        def __init__(self):
            QValidator.__init__(self)
            self._validator = None

        def validate(self, text, pos):
            try:
                values = MultiNumericalLineEdit._parse_text(text)
            except:
                return QValidator.Intermediate

            if self.validator() is None:
                return QValidator.Acceptable

            return self.validator().validate(values)

        def fixup(self, text):
            return text

        def validator(self):
            return self._validator

        def setValidator(self, validator):
            self._validator = validator

    def __init__(self, parent=None):
        QLineEdit.__init__(self, parent)
        QLineEdit.setValidator(self, self._Validator())

    def setText(self, text):
        values = self._parse_text(text)
        self.setValues(values)

    def text(self):
        return self._VALUE_SEPARATOR.join(map(str, self.values()))

    def values(self):
        text = QLineEdit.text(self)
        return np.sort(self._parse_text(text))

    def setValues(self, values):
        values = np.array(values, ndmin=1)
        text = self._VALUE_SEPARATOR.join(map(str, np.sort(values)))
        QLineEdit.setText(self, text)

    def validator(self):
        return QLineEdit.validator(self).validator()

    def setValidator(self, validator):
        return QLineEdit.validator(self).setValidator(validator)

class UnitComboBox(QComboBox):

    _PREFIXES = (('y', 1e-24), # yocto
                 ('z', 1e-21), # zepto
                 ('a', 1e-18), # atto
                 ('f', 1e-15), # femto
                 ('p', 1e-12), # pico
                 ('n', 1e-9), # nano
                 ('u', 1e-6), # micro
                 ('m', 1e-3), # mili
                 ('c', 1e-2), # centi
                 ('d', 1e-1), # deci
                 ('k', 1e3), # kilo
                 ('M', 1e6), # mega
                 ('G', 1e9), # giga
                 ('T', 1e12), # tera
                 ('P', 1e15), # peta
                 ('E', 1e18), # exa
                 ('Z', 1e21), # zetta
                 ('Y', 1e24)) # yotta

    def __init__(self, base_unit, parent=None):
        QComboBox.__init__(self, parent)

        self._base_unit = base_unit

        self._factors = {}
        for prefix, factor in self._PREFIXES:
            name = prefix + base_unit
            self.addItem(name)
            self._factors[name] = factor

            if prefix == 'd':
                self.addItem(base_unit)
                self._factors[base_unit] = 1.0

        self.setUnit(self._base_unit)

    def unit(self):
        return self.currentText()

    def setUnit(self, unit):
        self.setCurrentIndex(self.findText(unit))

    def prefix(self):
        return self.currentText().rstrip(self._base_unit)

    def setPrefix(self, prefix):
        self.setCurrentIndex(self.findText(prefix + self._base_unit))

    def factor(self):
        return self._factors[self.unit()]

class AngleComboBox(QComboBox):

    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)

        self.addItem('rad')
        self.addItem(u'\u00b0')
        self.setCurrentIndex(0)

    def unit(self):
        return self.currentText()

    def setUnit(self, unit):
        self.setCurrentIndex(self.findText(unit))

    def factor(self):
        return 1.0 if self.currentIndex() == 0 else np.pi / 180.0

class TimeComboBox(QComboBox):

    _FACTORS = (('year', 31536000.0),
                ('month', 2628000.0),
                ('day', 86400.0),
                ('hr', 3600.0),
                ('min', 60.0),
                ('s', 1.0))

    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)

        self._factors = {}
        for scale, factor in self._FACTORS:
            self.addItem(scale)
            self._factors[scale] = factor

        self.setScale('s')

    def scale(self):
        return self.currentText()

    def setScale(self, scale):
        self.setCurrentIndex(self.findText(scale))

    def factor(self):
        return self._factors[self.scale()]
