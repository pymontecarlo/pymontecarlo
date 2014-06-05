#!/usr/bin/env python
"""
================================================================================
:mod:`periodictable` -- Periodic table of element dialog
================================================================================

.. module:: periodictable
   :synopsis: Periodic table of element dialog

.. inheritance-diagram:: pyhmsa.ui.gui.util.periodictable

"""

# Standard library modules.
import math

# Third party modules.
from PySide.QtGui import \
    (QWidget, QDialog, QPushButton, QPainter, QGridLayout, QColor, QFont,
     QLabel, QSizePolicy, QButtonGroup, QDialogButtonBox, QVBoxLayout,
     QMessageBox)
from PySide.QtCore import Qt, Signal

import six

# Local modules.
import pyxray.element_properties as ep

# Globals and constants variables.

class ElementPushButton(QPushButton):

    def __init__(self, atomic_number, parent=None):
        QPushButton.__init__(self, parent)
        self.setFixedSize(40, 40)

        self._atomic_number = atomic_number
        self._symbol = ep.symbol(atomic_number)

        self.setText(self._symbol)

        font = self.font()
        font.setWeight(QFont.Bold)
        self.setFont(font)

        self.setSizePolicy(QSizePolicy.MinimumExpanding,
                           QSizePolicy.MinimumExpanding)

        self.setDefault(False)
        self.setAutoDefault(False)

    def paintEvent(self, event):
        QPushButton.paintEvent(self, event)

        qp = QPainter()
        qp.begin(self)

        font = qp.font()
        font.setPixelSize(8)
        font.setWeight(QFont.Normal)
        qp.setFont(font)

        qp.drawText(event.rect().translated(1, 1), str(self._atomic_number))

        qp.end()

    @property
    def atomic_number(self):
        return self._atomic_number

    @property
    def symbol(self):
        return self._symbol

_ELEMENT_POSITIONS = \
    {1: (0, 0), 2: (0, 17), 3: (1, 0), 4: (1, 1), 5: (1, 12), 6: (1, 13),
     7: (1, 14), 8: (1, 15), 9: (1, 16), 10: (1, 17), 11: (2, 0), 12: (2, 1),
     13: (2, 12), 14: (2, 13), 15: (2, 14), 16: (2, 15), 17: (2, 16),
     18: (2, 17), 19: (3, 0), 20: (3, 1), 21: (3, 2), 22: (3, 3), 23: (3, 4),
     24: (3, 5), 25: (3, 6), 26: (3, 7), 27: (3, 8), 28: (3, 9), 29: (3, 10),
     30: (3, 11), 31: (3, 12), 32: (3, 13), 33: (3, 14), 34: (3, 15),
     35: (3, 16), 36: (3, 17), 37: (4, 0), 38: (4, 1), 39: (4, 2), 40: (4, 3),
     41: (4, 4), 42: (4, 5), 43: (4, 6), 44: (4, 7), 45: (4, 8), 46: (4, 9),
     47: (4, 10), 48: (4, 11), 49: (4, 12), 50: (5, 12), 51: (4, 14),
     52: (4, 15), 53: (4, 16), 54: (4, 17), 55: (5, 0), 56: (5, 1), 57: (8, 3),
     58: (8, 4), 59: (8, 5), 60: (8, 6), 61: (8, 7), 62: (8, 8), 63: (8, 9),
     64: (8, 10), 65: (8, 11), 66: (8, 12), 67: (8, 13), 68: (8, 14),
     69: (8, 15), 70: (8, 16), 71: (8, 17), 72: (5, 3), 73: (5, 4), 74: (5, 5),
     75: (5, 6), 76: (5, 7), 77: (5, 8), 78: (5, 9), 79: (5, 10), 80: (5, 11),
     81: (4, 13), 82: (5, 13), 83: (5, 14), 84: (5, 15), 85: (5, 16),
     86: (5, 17), 87: (6, 0), 88: (6, 1), 89: (9, 3), 90: (9, 4), 91: (9, 5),
     92: (9, 6), 93: (9, 7), 94: (9, 8), 95: (9, 9), 96: (9, 10), 97: (9, 11),
     98: (9, 12), 99: (9, 13), 100: (9, 14), 101: (9, 15), 102: (9, 16),
     103: (9, 17), 104: (6, 3), 105: (6, 4), 106: (6, 5), 107: (6, 6),
     108: (6, 7), 109: (6, 8), 110: (6, 9), 111: (6, 10), 112: (6, 11),
     113: (6, 12), 114: (6, 13), 115: (6, 14), 116: (6, 15), 117: (6, 16),
     118: (6, 17)}

def _category_color_function(z):
    ALKALI_METALS = QColor(204, 153, 204)
    ALKALI_EARTH_METALS = QColor(0, 255, 255)
    NON_METALS = QColor(0, 204, 102)
    TRANSITION_METALS = QColor(102, 255, 153)
    OTHER_METALS = QColor(153, 51, 204)
    HALOGENS = QColor(255, 204, 0)
    INERT_GAS = QColor(204, 0, 0)
    LANTHANIDES = QColor(102, 0, 255)
    ACTINIDES = QColor(102, 102, 255)
    METALLOIDS = QColor(80, 150, 150)

    if z in [1]:
        return NON_METALS

    elif z in [3, 11, 19, 37, 55, 87]:
        return ALKALI_METALS

    elif z in [4, 12, 20, 38, 56, 88]:
        return ALKALI_EARTH_METALS

    elif z in [21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
               39, 40, 41, 42, 43, 44, 45, 46, 47, 48,
               72, 73, 74, 75, 76, 77, 78, 79, 80,
               104, 105, 106, 107, 108, 109, 110, 111, 112]:
        return TRANSITION_METALS

    elif z in [5, 14, 32, 33, 51, 52, 84]:
        return METALLOIDS

    elif z in [6, 7, 8, 14, 15, 16, 33, 34, 52]:
        return NON_METALS

    elif z in [13, 31, 49, 50, 81, 82, 83, 113, 114, 115, 116]:
        return OTHER_METALS

    elif z in [9, 17, 35, 53, 85, 117]:
        return HALOGENS

    elif z in [2, 10, 18, 36, 54, 86, 118]:
        return INERT_GAS

    elif z in [57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71]:
        return LANTHANIDES

    elif z in [89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103]:
        return ACTINIDES

    raise ValueError('No color definition for z: %s' % z)

def _calculate_brightness(color):
    """
    Returns a value between 0 and 255 corresponding to the brightness of the
    specified color.

    From:http://tech.chitgoks.com/2010/07/27/check-if-color-is-dark-or-light-using-java/
    """
    return int(math.sqrt(color.red() ** 2 * .241 + \
                         color.green() ** 2 * .691 + \
                         color.blue() ** 2 * .068))

class PeriodicTableWidget(QWidget):

    selectionChanged = Signal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        # Widgets, layouts and signals
        self._group = QButtonGroup()

        layout = QGridLayout()
        layout.setSpacing(0)

        for i in range(18):
            layout.setColumnMinimumWidth(i, 40)
            layout.setColumnStretch(i, 0)
        for i in list(range(7)) + [8, 9]:
            layout.setRowMinimumHeight(i, 40)
            layout.setRowStretch(i, 0)

        ## Element
        for z, position in _ELEMENT_POSITIONS.items():
            widget = ElementPushButton(z)
            widget.setCheckable(True)
            layout.addWidget(widget, *position)
            self._group.addButton(widget, z)

        ## Labels
        layout.addWidget(QLabel(''), 7, 0) # Dummy
        layout.addWidget(QLabel('*'), 5, 2, Qt.AlignCenter)
        layout.addWidget(QLabel('*'), 8, 2, Qt.AlignCenter)
        layout.addWidget(QLabel('**'), 6, 2, Qt.AlignCenter)
        layout.addWidget(QLabel('**'), 9, 2, Qt.AlignCenter)

        for row in [0, 1, 2, 3, 4, 5, 6, 8, 9]:
            layout.setRowStretch(row, 1)

        self.setLayout(layout)

        # Signals
        self._group.buttonClicked.connect(self.selectionChanged)

        # Default
        self.setColorFunction(_category_color_function)

    def setColorFunction(self, func):
        if not callable(func):
            raise ValueError('Not a function')
        self._color_function = func

        # Redraw
        for widget in self._group.buttons():
            z = self._group.id(widget)
            bcolor = func(z)
            fcolor = 'white' if _calculate_brightness(bcolor) < 128 else 'black'
            sheet = 'background-color: %s; color: %s' % (bcolor.name(), fcolor)
            widget.setStyleSheet(sheet)

    def colorFunction(self):
        return self._color_function

    def setMultipleSelection(self, multiple):
        self._group.setExclusive(not multiple)

    def isMultipleSelection(self):
        return not self._group.exclusive()

    def setSelection(self, selection):
        def _uncheckedAll():
            for widget in self._group.buttons():
                widget.setChecked(False)

        if selection is None:
            _uncheckedAll()
            self.selectionChanged.emit()
            return

        if isinstance(selection, (int, six.string_types)):
            selection = [selection]

        if not self.isMultipleSelection() and len(selection) > 1:
            raise ValueError('Multiple selection mode is off. Cannot select more than one element')

        _uncheckedAll()

        for z in selection:
            if isinstance(z, six.string_types):
                z = ep.atomic_number(z.strip())
            self._group.button(z).setChecked(True)

        self.selectionChanged.emit()
#
    def selection(self):
        selection = set()
        for widget in self._group.buttons():
            if widget.isChecked():
                selection.add(self._group.id(widget))

        if self.isMultipleSelection():
            return frozenset(selection)
        else:
            if len(selection) > 0:
                return list(selection)[0]
            else:
                return None

    def selectionSymbol(self):
        selection = self.selection()
        if self.isMultipleSelection():
            return frozenset(map(ep.symbol, selection))
        else:
            if selection is None:
                return None
            else:
                return ep.symbol(selection)

class PeriodicTableDialog(QDialog):

    selectionChanged = Signal()

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle('Periodic table')

        # Variables
        self._required_selection = True

        # Widgets
        self._wdg_table = PeriodicTableWidget()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        # Layouts
        layout = QVBoxLayout()
        layout.addWidget(self._wdg_table)
        layout.addWidget(buttons)
        self.setLayout(layout)

        # Signals
        self._wdg_table.selectionChanged.connect(self.selectionChanged)
        buttons.accepted.connect(self._onOk)
        buttons.rejected.connect(self._onCancel)

    def _onOk(self):
        if self.isRequiresSelection() and not self._wdg_table.selection():
            QMessageBox.critical(self, self.windowTitle(),
                                 'Please select one element')
            return
        self.accept()

    def _onCancel(self):
        self.setSelection(None)
        self.reject()

    def setColorFunction(self, func):
        self._wdg_table.setColorFunction(func)

    def colorFunction(self):
        return self._wdg_table.colorFunction()

    def setMultipleSelection(self, multiple):
        self._wdg_table.setMultipleSelection(multiple)

    def isMultipleSelection(self):
        return self._wdg_table.isMultipleSelection()

    def setSelection(self, zs):
        self._wdg_table.setSelection(zs)
#
    def selection(self):
        return self._wdg_table.selection()

    def selectionSymbol(self):
        return self._wdg_table.selectionSymbol()

    def setRequiresSelection(self, required):
        self._required_selection = required

    def isRequiresSelection(self):
        return self._required_selection

def run():
    import sys
    from PySide.QtGui import QApplication

    def selection():
        print('hello')

    app = QApplication(sys.argv)
    dialog = PeriodicTableDialog(None)
    dialog.selectionChanged.connect(selection)
    dialog.exec_()
    print(dialog.selection())
    app.exec_()

if __name__ == '__main__':
    run()
