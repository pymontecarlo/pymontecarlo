#!/usr/bin/env python
"""
================================================================================
:mod:`config` -- Base configuration interface of all Monte Carlo programs
================================================================================

.. module:: config
   :synopsis: Base configuration interface of all Monte Carlo programs

.. inheritance-diagram:: pymontecarlo.program.config

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.

# Globals and constants variables.

TYPE_FILE = 'file'
TYPE_DIR = 'dir'
TYPE_INT = 'int'
TYPE_BOOL = 'bool'
TYPE_FLOAT = 'float'
TYPE_TEXT = 'text'

class Program(object):

    def __hash__(self, *args, **kwargs):
        return hash(self._get_alias())

    def __repr__(self):
        return '<Program(%s)>' % self.name

    def __str__(self):
        return self.name

    def _get_name(self):
        raise NotImplementedError

    @property
    def name(self):
        """
        Full program name.
        """
        return self._get_name()

    def _get_alias(self):
        raise NotImplementedError

    @property
    def alias(self):
        """
        Short program name
        """
        return self._get_alias()

    def _get_converter(self):
        raise NotImplementedError

    @property
    def converter(self):
        """
        Converter class of program
        """
        return self._get_converter()

    def _get_exporter(self):
        raise NotImplementedError

    @property
    def exporter(self):
        """
        Exporter class of program
        """
        return self._get_exporter()

    def _get_importer(self):
        raise NotImplementedError

    @property
    def importer(self):
        """
        Importer class of program
        """
        return self._get_importer()

    def _get_worker(self):
        raise NotImplementedError

    @property
    def worker(self):
        """
        Worker class of program
        """
        return self._get_worker()

    def validate(self):
        raise AssertionError

    @property
    def configure_params(self):
        """
        Returns a :class:`list` of :class:`tuple` that will help the 
        user interface configure this program
        
        Each tuple contains four values.
        
          1. the name of the section in the settinsg file
          2. the name of the option in the settings file
          3. a description of the option
          4. type of value (see constants starting with ``TYPE_``)
        """
        return self._get_configure_params()

    def _get_configure_params(self):
        raise NotImplementedError
