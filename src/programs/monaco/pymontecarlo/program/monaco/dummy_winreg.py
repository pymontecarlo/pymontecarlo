#!/usr/bin/env python
"""
================================================================================
:mod:`dummy_winreg` -- Dummy winreg
================================================================================

.. module:: dummy_winreg
   :synopsis: Dummy winreg

.. inheritance-diagram:: pymontecarlo.program.monaco.runner.dummy_winreg

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

# Globals and constants variables.

HKEY_CURRENT_USER = None
KEY_ALL_ACCESS = None
REG_SZ = None

class _PyHKEY(object):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

def OpenKey(key, sub_key, res, sam):
    return _PyHKEY()

def CreateKey(key, sub_key):
    return _PyHKEY()

def SetValueEx(key, value_name, reserved, type_, value):
    pass
