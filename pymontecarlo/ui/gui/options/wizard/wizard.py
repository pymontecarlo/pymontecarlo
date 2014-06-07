#!/usr/bin/env python
"""
================================================================================
:mod:`wizard` -- Options wizard
================================================================================

.. module:: wizard
   :synopsis: Options wizard

.. inheritance-diagram:: pymontecarlo.ui.gui.options.wizard.wizard

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import copy

# Third party modules.
from PySide.QtGui import QWizard

# Local modules.
from pymontecarlo.options.options import Options

from pymontecarlo.settings import get_settings

from pymontecarlo.ui.gui.options.wizard.name import NameWizardPage
from pymontecarlo.ui.gui.options.wizard.program import ProgramWizardPage
from pymontecarlo.ui.gui.options.wizard.beam import BeamWizardPage
from pymontecarlo.ui.gui.options.wizard.geometry import GeometryWizardPage
from pymontecarlo.ui.gui.options.wizard.detector import DetectorWizardPage
from pymontecarlo.ui.gui.options.wizard.limit import LimitWizardPage
from pymontecarlo.ui.gui.options.wizard.model import ModelWizardPage
from pymontecarlo.ui.gui.options.wizard.warning import WarningWizardPage

# Globals and constants variables.

class OptionsWizard(QWizard):

    def __init__(self, options=None, parent=None):
        QWizard.__init__(self, parent)
        if options is None:
            self.setWindowTitle("Create new options")
        else:
            self.setWindowTitle("Modify options")
        self.setWizardStyle(QWizard.WizardStyle.ClassicStyle)

        # Variables
        if options is None:
            options = Options()
        options = copy.deepcopy(options)
        self._options = options

        settings = get_settings()
        if not settings.get_programs():
            raise RuntimeError('No programs are defined. Run the configuration first.')

        # Pages
        self.addPage(NameWizardPage(options))
        self.addPage(ProgramWizardPage(options))
        self.addPage(BeamWizardPage(options))
        self.addPage(GeometryWizardPage(options))
        self.addPage(DetectorWizardPage(options))
        self.addPage(LimitWizardPage(options))
        self.addPage(ModelWizardPage(options))
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
