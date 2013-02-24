#!/usr/bin/env python
"""
================================================================================
:mod:`programs` -- Utilities to find and load programs
================================================================================

.. module:: programs
   :synopsis: Utilities to find and load programs

.. inheritance-diagram:: programs

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import logging

# Third party modules.
from pkg_resources import iter_entry_points

# Local modules.
from pymontecarlo.settings import get_settings

# Globals and constants variables.

def get_programs():
    """
    Returns the available Monte Carlo programs.
    The programs are loaded based on the settings.

    .. note::

       Note that the programs are loaded only once when this method is called
       for the first time. After that, the same set is returned.

    :return: a set of programs
    """
    settings = get_settings()
    programs = []

    programs_value = getattr(settings.pymontecarlo, 'programs', '')
    if not programs_value:
        logging.error("No programs are defined in settings")
        return programs

    names = programs_value.split(',')
    for name in names:
        try:
            program = load_program(name)
        except Exception as ex:
            logging.error('The following exception occurred while loading program "%s": %s',
                          name, str(ex))
            continue

        programs.append(program)
        logging.debug("Loaded program (%s) from %s", program.name, name)

    return frozenset(programs)

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


def load_program(name, validate=True):
    """
    Imports, loads, validates and returns a program.
    
    :arg name: name of the program's module (e.g. ``penepma`` or ``winxray``)
    :arg validate: whether to validate if all the settings are correct for the
        program
    """
    for handler in iter_entry_points('pymontecarlo.program'):
        if handler.name == name:
            program = handler.load()

            if validate:
                program.validate()

            return program

    raise ValueError, 'Program %s not found' % name

def find_programs():
    """
    Returns a list of program aliases that could be found in the settings.cfg,
    but may not have been configured.
    """
    programs = []

    for handler in iter_entry_points('pymontecarlo.program'):
        programs.append(handler.name)

    return sorted(programs)

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

    for handler in iter_entry_points('pymontecarlo.program.cli'):
        if handler.name == name:
            return handler.load()

    raise ValueError, 'Program CLI %s not found' % name

def get_program_gui(program):
    """
    Imports, loads and returns the graphical user interface of the specified
    program.
    The method raises :exc:`ImportError` exception if:

      * No ``config_cli.py`` module exists in program package.
      * No ``cli`` variable exists in ``config_cli.py`` module.

    :arg program: program configuration object
    """
    name = program.alias

    for handler in iter_entry_points('pymontecarlo.program.gui'):
        if handler.name == name:
            return handler.load()

    raise ValueError, 'Program CLI %s not found' % name

