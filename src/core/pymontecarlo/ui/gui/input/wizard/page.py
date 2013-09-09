#!/usr/bin/env python
"""
================================================================================
:mod:`page` -- Base implementation of wizard page
================================================================================

.. module:: page
   :synopsis: Base implementation of wizard page

.. inheritance-diagram:: pymontecarlo.ui.gui.input.wizard.page

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.
from wxtools2.wizard import WizardPage as _WizardPage
from wxtools2.validator import form_validate

# Globals and constants variables.

class WizardPage(_WizardPage):

    def __init__(self, wizard, title, options):
        _WizardPage.__init__(self, wizard, title)

        self._options = options

    def Validate(self):
        return form_validate(self)

    def on_value_changed(self, event=None):
        self.GetParent().on_value_changed(event)

    @property
    def options(self):
        return self._options
