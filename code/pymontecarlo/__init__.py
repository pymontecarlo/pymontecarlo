#!/usr/bin/env python
"""
================================================================================
:mod:`pymontecarlo` -- Common interface to several Monte Carlo codes
================================================================================

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

# Local modules.
from pymontecarlo.util.config import ConfigParser
from pymontecarlo.util.xmlutil import XMLIO

# Globals and constants variables.

################################################################################
# Register XML namespace and schema
################################################################################

XMLIO.add_namespace('mc', 'http://pymontecarlo.sf.net',
                    os.path.join(os.path.dirname(__file__), 'schema.xsd'))

################################################################################
# Settings
################################################################################

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
    filepaths.append(os.path.join(os.path.dirname(__file__), 'settings.cfg'))

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

    raise IOError, "Settings could not be loaded"

################################################################################
# Programs
################################################################################

_programs = None

def get_programs():
    """
    Returns the available Monte Carlo programs.
    The programs are loaded based on the settings.
    
    .. note:: 
       
       Note that the programs are loaded only once when this method is called
       for the first time. After that, the same set is returned.
    
    :return: a set of programs
    """
    global _programs

    if _programs is not None:
        return _programs

    _programs = frozenset(load_programs(get_settings()))

    return _programs

def load_programs(settings, validate=True):
    """
    Loads the programs defined in the settings.
    The list of programs should be set under the section ``pymontecarlo`` and
    the option ``program``. An :exc:`IOError` exception is raised if the option
    is not defined.
    
    If ``validate`` is ``True``, the method will raise a :exc:`AssertionError` 
    if one of the programs is not valid.
    
    :arg settings: settings
    :arg validate: whether to validate if all the settings are correct for the
        programs
    """
    programs = set()

    value = getattr(settings.pymontecarlo, 'programs', '')
    if not value:
        raise IOError, "No programs are defined in settings"

    names = getattr(settings.pymontecarlo, 'programs').split(',')
    for name in names:
        try:
            program = load_program(name, validate)
        except Exception as ex:
            logging.error('The following exception occurred while loading program "%s": %s',
                          name, str(ex))
            continue

        programs.add(program)
        logging.debug("Loaded program (%s) from %s", program.name, name)

    return programs

def load_program(name, validate=True):
    """
    Imports, loads, validates and returns a program.
    The method raises :exc:`ImportError` exception if:
    
      * No ``config.py`` module exists in program package.
      * No ``program`` variable exists in ``config.py`` module.
    
    If ``validate`` is ``True``, the method will raise a :exc:`AssertionError` 
    if the program is not valid.
    
    :arg name: name of the program's module (e.g. ``penepma`` or ``winxray``)
    :arg validate: whether to validate if all the settings are correct for the
        program
    """
    mod = __import__('pymontecarlo.program.' + name, None, None, ['config'])

    if not hasattr(mod, 'config'):
        raise ImportError, "Package '%s' does not have a 'config' module." % name

    if not hasattr(mod.config, 'program'):
        raise ImportError, "Module 'config' of package '%s' must have a 'program' attribute" % name

    program = mod.config.program

    if validate:
        program.validate()

    return program

def find_programs():
    """
    Returns a list of program aliases that could be found in the settings.cfg,
    but may not have been configured.
    """
    dirpath = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(dirpath, 'settings.cfg.example')

    settings = ConfigParser()
    with open(filepath, 'r') as fp:
        settings.read(fp)

    return settings.pymontecarlo.programs.split(',')

def get_program_cli(program):
    """
    Imports, loads and returns the command line interface of the specified
    program.
    The method raises :exc:`ImportError` exception if:
    
      * No ``config_cli.py`` module exists in program package.
      * No ``cli`` variable exists in ``config_cli.py`` module.
    
    :arg program: program configuration object
    """
    name = program.alias
    mod = __import__('pymontecarlo.program.' + name, None, None, ['config_cli'])

    if not hasattr(mod, 'config_cli'):
        raise ImportError, "Package '%s' does not have a 'config_cli' module." % name

    if not hasattr(mod.config_cli, 'cli'):
        raise ImportError, "Module 'config_cli' of package '%s' must have a 'cli' attribute" % name

    return mod.config_cli.cli

def get_program_gui(program):
    """
    Imports, loads and returns the graphical user interface of the specified
    program.
    The method raises :exc:`ImportError` exception if:
    
      * No ``config_gui.py`` module exists in program package.
      * No ``gui`` variable exists in ``config_gui.py`` module.
    
    :arg program: program configuration object
    """
    name = program.alias
    mod = __import__('pymontecarlo.program.' + name, None, None, ['config_gui'])

    if not hasattr(mod, 'config_gui'):
        raise ImportError, "Package '%s' does not have a 'config_gui' module." % name

    if not hasattr(mod.config_gui, 'gui'):
        raise ImportError, "Module 'config_gui' of package '%s' must have a 'gui' attribute" % name

    return mod.config_gui.gui


################################################################################
# Reload
################################################################################

def reload():
    """
    Resets the settings and programs.
    Once the methods :meth:`get_settings` or :meth:`get_programs` are called,
    the settings and programs will be reloaded.
    """
    _settings = None
    _programs = None

################################################################################
# Initialize
################################################################################

get_programs()
