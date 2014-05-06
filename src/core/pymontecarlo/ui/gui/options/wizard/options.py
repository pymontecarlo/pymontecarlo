#!/usr/bin/env python
"""
================================================================================
:mod:`options` -- Options widgets and wizard
================================================================================

.. module:: options
   :synopsis: Options widgets and wizard

.. inheritance-diagram:: pymontecarlo.ui.gui.options.options

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from operator import attrgetter, methodcaller

# Third party modules.
from PySide.QtGui import \
    (QWizard, QWizardPage, QVBoxLayout, QFormLayout, QCheckBox, QPushButton,
     QHBoxLayout, QSpacerItem, QSizePolicy, QLabel, QFrame)
from PySide.QtCore import Qt, Signal

from pkg_resources import iter_entry_points

# Local modules.
from pymontecarlo.options.options import Options
from pymontecarlo.settings import get_settings

# Globals and constants variables.

class SimulationCountLabel(QLabel):

    def setValue(self, value):
        if value > 1:
            text = '%i simulations defined'
        else:
            text = '%i simulation defined'
        QLabel.setText(self, text % value)

    def value(self):
        return int(QLabel.text(self).split(' ')[0])

class _OptionsWizardPage(QWizardPage):

    def __init__(self, options, parent=None):
        QWizardPage.__init__(self, parent)

        # Variables
        self._options = options

        # Layouts
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        sublayout = self._initUI() # Initialize widgets
        sublayout.setContentsMargins(10, 10, 10, 10)
        layout.addLayout(sublayout, 1)
        layout.addStretch()

        self.setLayout(layout)

    def _initUI(self):
        return QFormLayout()

    def options(self):
        return self._options

class _ExpandableOptionsWizardPage(_OptionsWizardPage):

    valueChanged = Signal()

    def __init__(self, options, parent=None):
        _OptionsWizardPage.__init__(self, options, parent)

        # Widgets
        self._lbl_count = SimulationCountLabel()
        self._lbl_count.setAlignment(Qt.AlignCenter)

        # Layouts
        layout = self.layout()

        frm_line = QFrame()
        frm_line.setFrameStyle(QFrame.HLine)
        frm_line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(frm_line)

        sublayout = QHBoxLayout()
        sublayout.setContentsMargins(10, 0, 10, 0)
        sublayout.addWidget(self._lbl_count)
        layout.addLayout(sublayout)

        # Signals
        self.valueChanged.connect(self._onChanged)

    def _onChanged(self):
        wizard = self.parent().parent().parent()

        count = 1
        for pageid in wizard.pageIds():
            page = wizard.page(pageid)
            if hasattr(page, 'expandCount'):
                count *= wizard.page(pageid).expandCount()

        self._lbl_count.setValue(count)

    def _iter_widgets(self, entry_point_group, converter_attr):
        allwidgets = {}
        for entry_point in iter_entry_points(entry_point_group):
            allwidgets[entry_point.name] = entry_point.load()

        widget_classes = {}
        programs = {}
        for program in self.options().programs:
            converter = program.converter_class

            for clasz in getattr(converter, converter_attr):
                name = clasz.__name__
                if name not in allwidgets:
                    continue
                widget_classes[clasz] = allwidgets[name]
                programs.setdefault(clasz, set()).add(program)

        for clasz in sorted(widget_classes.keys(), key=attrgetter('__name__')):
            yield clasz, widget_classes[clasz], programs[clasz]

    def expandCount(self):
        raise NotImplementedError

class ProgramWizardPage(_OptionsWizardPage):

    def __init__(self, options, parent=None):
        _OptionsWizardPage.__init__(self, options, parent)
        self.setTitle("Program")

    def _initUI(self):
        # Variable
        settings = get_settings()

        # Widgets
        self._checkboxes = {}
        for program in settings.get_available_programs():
            self._checkboxes[program] = QCheckBox(program.name)

        btn_selectall = QPushButton('Select all')
        btn_deselectall = QPushButton('Deselect all')

        # Layouts
        layout = _OptionsWizardPage._initUI(self)
        for checkbox in self._checkboxes.values():
            layout.addRow(checkbox)

        spacer = QSpacerItem(0, 1000, QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addItem(spacer)

        sublayout = QHBoxLayout()
        sublayout.addWidget(btn_selectall)
        sublayout.addWidget(btn_deselectall)
        layout.addRow(sublayout)

        # Signals
        btn_selectall.released.connect(self._onSelectAll)
        btn_deselectall.released.connect(self._onDeselectAll)

        return layout

    def _onSelectAll(self):
        for checkbox in self._checkboxes.values():
            checkbox.setChecked(True)

    def _onDeselectAll(self):
        for checkbox in self._checkboxes.values():
            checkbox.setChecked(False)

    def initializePage(self):
        programs = self.options().programs
        for program, checkbox in self._checkboxes.items():
            checkbox.setChecked(program in programs)

    def validatePage(self):
        if not any(map(methodcaller('isChecked'), self._checkboxes.values())):
            return False

        self.options().programs.clear()
        for program, checkbox in self._checkboxes.items():
            if checkbox.isChecked():
                self.options().programs.add(program)

        return True

class OptionsWizard(QWizard):

    def __init__(self, options=None, parent=None):
        QWizard.__init__(self, parent)
        if options is None:
            self.setWindowTitle("Create new options")
        else:
            self.setWindowTitle("Modify options")

        # Variables
        if options is None:
            options = Options()
        self._options = options

        # Pages
        self.addPage(ProgramWizardPage(options))

        from pymontecarlo.ui.gui.options.wizard.beam import BeamWizardPage
        self.addPage(BeamWizardPage(options))

        from pymontecarlo.ui.gui.options.wizard.geometry import GeometryWizardPage
        self.addPage(GeometryWizardPage(options))

        from pymontecarlo.ui.gui.options.wizard.detector import DetectorWizardPage
        self.addPage(DetectorWizardPage(options))

        from pymontecarlo.ui.gui.options.wizard.limit import LimitWizardPage
        self.addPage(LimitWizardPage(options))

        from pymontecarlo.ui.gui.options.wizard.model import ModelWizardPage
        self.addPage(ModelWizardPage(options))

        from pymontecarlo.ui.gui.options.wizard.warning import WarningWizardPage
        self.addPage(WarningWizardPage(options))

    def options(self):
        return self._options

def __run():
    import sys
    from PySide.QtGui import QApplication

    app = QApplication(sys.argv)

    from pymontecarlo.options.detector import TimeDetector
    from pymontecarlo.options.limit import ShowersLimit
    options = Options()
    options.detectors['time'] = TimeDetector()
    options.limits.add(ShowersLimit(1000))

    wizard = OptionsWizard(options)
    wizard.show()

    app.exec_()

    print(wizard.options())

if __name__ == '__main__':
    __run()
