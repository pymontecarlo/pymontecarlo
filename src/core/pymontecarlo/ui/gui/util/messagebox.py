#!/usr/bin/env python
"""
================================================================================
:mod:`messagebox` -- Special message box
================================================================================

.. module:: messagebox
   :synopsis: Special message box

.. inheritance-diagram:: pyhmsa.ui.gui.util.messagebox

"""

# Standard library modules.
import sys
import traceback
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

# Third party modules.
from PySide.QtGui import QMessageBox

# Local modules.

# Globals and constants variables.

def exception(parent, ex, buttons=QMessageBox.Ok,
              defaultButton=QMessageBox.NoButton):
    title = type(ex).__name__
    message = str(ex)
    tb = StringIO()
    if hasattr(ex, '__traceback__'):
        exc_traceback = ex.__traceback__
    else:
        exc_traceback = sys.exc_info()[2]
    traceback.print_tb(exc_traceback, file=tb)

    msgbox = QMessageBox(QMessageBox.Icon.Critical, title, message, buttons, parent)
    msgbox.setDefaultButton(defaultButton)
    msgbox.setDetailedText(tb.getvalue())
    msgbox.exec_()
