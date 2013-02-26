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
import re
import logging

# Third party modules.
from pkg_resources import iter_entry_points

# Local modules.
from pymontecarlo.util.config import ConfigParser
from pymontecarlo.program.config import Program

# Globals and constants variables.

class Settings(ConfigParser):

    def __init__(self):
        ConfigParser.__init__(self)
        self.add_section('pymontecarlo')

    def get_available_program_aliases(self):
        """
        Returns a list of program aliases that could be found in the settings.cfg,
        but may not have been configured.
        """
        programs = []

        for handler in iter_entry_points('pymontecarlo.program'):
            programs.append(handler.name)

        return tuple(programs)

    def get_available_programs(self):
        """
        Returns a list of program that could be in the settings.cfg, but may
        not have been configured.
        """
        programs = []

        for alias in self.get_available_program_aliases():
            try:
                program = self.get_program(alias, validate=False)
            except Exception as ex:
                logging.error('The following exception occurred while loading program "%s": %s',
                              alias, str(ex))
                continue

            programs.append(program)
            logging.debug("Loaded program (%s) from %s", program.name, alias)

        return tuple(programs)

    def get_program_aliases(self):
        """
        Returns the alias of all programs defined in the settings.
        """
        programs_value = getattr(self.pymontecarlo, 'programs', '')
        if not programs_value:
            logging.error("No programs are defined in settings")
            return ()

        return tuple(re.findall(r'[^,;\s]+', programs_value))

    def get_programs(self):
        programs = []

        for alias in self.get_program_aliases():
            try:
                program = self.get_program(alias)
            except Exception as ex:
                logging.error('The following exception occurred while loading program "%s": %s',
                              alias, str(ex))
                continue

            programs.append(program)
            logging.debug("Loaded program (%s) from %s", program.name, alias)

        return tuple(programs)

    def get_program(self, alias, validate=True):
        """
        Imports, loads, validates and returns a program.
        
        :arg name: name of the program's module (e.g. ``penepma`` or ``winxray``)
        :arg validate: whether to validate if all the settings are correct for the
            program
        """
        for handler in iter_entry_points('pymontecarlo.program'):
            if handler.name == alias:
                program = handler.load()

                if validate:
                    program.validate()

                return program

        raise ValueError, 'Program %s not found' % alias

    def get_program_cli(self, program):
        """
        Imports, loads and returns the command line interface of the specified
        program.
        The method raises :exc:`ImportError` exception if:
    
          * No ``config_cli.py`` module exists in program package.
          * No ``cli`` variable exists in ``config_cli.py`` module.
    
        :arg program: program configuration object or alias
        """
        if isinstance(program, Program):
            alias = program.alias
        else:
            alias = program

        for handler in iter_entry_points('pymontecarlo.program.cli'):
            if handler.name == alias:
                return handler.load()

        raise ValueError, 'Program CLI %s not found' % alias

    def get_program_gui(self, program):
        """
        Imports, loads and returns the graphical user interface of the specified
        program.
        The method raises :exc:`ImportError` exception if:
    
          * No ``config_cli.py`` module exists in program package.
          * No ``cli`` variable exists in ``config_cli.py`` module.
    
        :arg program: program configuration object or alias
        """
        if isinstance(program, Program):
            alias = program.alias
        else:
            alias = program

        for handler in iter_entry_points('pymontecarlo.program.gui'):
            if handler.name == alias:
                return handler.load()

        raise ValueError, 'Program GUI %s not found' % alias

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
    settings = Settings()

    for filepath in filepaths:
        if os.path.exists(filepath):
            logging.debug('Loading settings from: %s', filepath)

            with open(filepath, 'r') as f:
                settings.read(f)
                return settings

    logging.error("Settings could not be loaded")

    return settings

def reload_settings():
    global _settings
    _settings = None
