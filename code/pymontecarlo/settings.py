#!/usr/bin/env python
"""
================================================================================
:mod:`settings` -- Settings for pymontecarlo
================================================================================

.. module:: settings
   :synopsis: Settings for pymontecarlo

.. inheritance-diagram:: settings

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import logging

# Third party modules.

# Local modules.
from pymontecarlo.util.config import ConfigParser

# Globals and constants variables.

_settings = None

def get_settings():
    """
    Returns the global settings.

    .. note::

       Note that the settings are loaded only once when this method is called
       for the first time. After that, the same settings are returned.

    :return: settings
    :rtype: :class:`pymontecarlo.util.config.ConfigParser`
    """
    global _settings

    if _settings is not None:
        return _settings

    filepaths = []
    filepaths.append(os.path.join(os.path.expanduser('~'), '.pymontecarlo',
                                  'settings.cfg'))

    _settings = load_settings(filepaths)

    return _settings

def _set_settings(settings):
    global _settings
    _settings = settings

def load_settings(filepaths):
    """
    Loads the settings from the first file path that exists from those
    specified.

    :arg filepaths: :class:`list` of paths to potential settings file
    """
    settings = ConfigParser()

    for filepath in filepaths:
        if os.path.exists(filepath):
            logging.debug('Loading settings from: %s', filepath)

            with open(filepath, 'r') as f:
                settings.read(f)
                return settings

    logging.error("Settings could not be loaded")

    # Default settings
    settings.add_section('pymontecarlo')

    return settings

def reload_settings():
    global _settings
    _settings = None
