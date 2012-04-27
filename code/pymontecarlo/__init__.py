#!/usr/bin/env python
"""
================================================================================
:mod:`pymontecarlo` -- Common interface to several Monte Carlo codes
================================================================================

.. module:: pymontecarlo
   :synopsis: Common interface to several Monte Carlo codes

.. inheritance-diagram:: pymontecarlo

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import logging

# Third party modules.
from pkg_resources import resource_filename #@UnresolvedImport

# Local modules.
from pymontecarlo.util.config import ConfigParser
from pymontecarlo.util.xmlutil import XMLIO

# Globals and constants variables.

################################################################################
# Register XML namespace and schema
################################################################################

XMLIO.add_namespace('mc', 'http://pymontecarlo.sf.net',
                    resource_filename(__name__, 'schema.xsd'))

################################################################################
# Settings
################################################################################

_settings = None

def get_settings():
    global _settings

    if _settings is not None:
        return _settings

    _settings = ConfigParser()

    filepaths = []
    filepaths.append(os.path.join(os.path.expanduser('~'), '.pymontecarlo',
                                  'settings.cfg'))
    filepaths.append(os.path.join(os.path.dirname(__file__), 'settings.cfg'))

    for filepath in filepaths:
        if os.path.exists(filepath):
            logging.debug('Loading settings from: %s', filepath)

            with open(filepath, 'r') as f:
                _settings.read(f)

            break

    return _settings

################################################################################
# Programs
################################################################################

_programs = None

def get_programs():
    global _programs

    if _programs is not None:
        return _programs

    settings = get_settings()

    value = getattr(settings.pymontecarlo, 'extensions', '')
    if not value:
        return

    extensions = getattr(settings.pymontecarlo, 'extensions').split(',')
    for extension in extensions:
        mod = __import__(extension, None, None, ['config'])

        if not hasattr(mod, 'config'):
            raise ImportError, "Extension '%s' does not have a 'config' module." % extension

        if not hasattr(mod.config, 'program'):
            raise ImportError, "Module 'config' of extension '%s' must have a 'program' attribute" % extension

        program = mod.config.program
        program.validate()

        _programs.add(program)
        logging.debug("Loaded program (%s) from %s", program.name, extension)

def reload():
    _settings = None
    _programs = None
