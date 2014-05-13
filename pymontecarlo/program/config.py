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

class Program(object):

    def __init__(self, name, alias, converter_class, worker_class,
                 exporter_class, importer_class):
        """
        Creates a new program.
        
        :arg name: full name of the program
        :type name: :class:`str`
        
        :arg alias: name of the package containing the program. 
        :type alias: :class:`str`
        
        :arg converter_class: class of the converter
        :type converter_class: :class:`Converter <pymontecarlo.input.converter.Converter>`
        
        :arg worker_class: class of the worker
        :type worker_class: :class:`Worker <pymontecarlo.program.worker.Worker>`
        
        :arg exporter_class: class of the exporter
        :type exporter_class: :class:`Exporter <pymontecarlo.io.exporter.Exporter>`
        
        :arg importer_class: class of the importer
        :type importer_class: :class:`Importer <pymontecarlo.io.importer.Importer>`
        """
        self._name = name
        self._alias = alias
        self._converter_class = converter_class
        self._worker_class = worker_class
        self._exporter_class = exporter_class
        self._importer_class = importer_class

    def __hash__(self):
        return hash(self.alias)

    def __repr__(self):
        return '<Program(%s)>' % self.name

    def __str__(self):
        return self.name

    @property
    def name(self):
        """
        Full program name.
        """
        return self._name

    @property
    def alias(self):
        """
        Short program name
        """
        return self._alias

    @property
    def converter_class(self):
        """
        Converter class of program
        """
        return self._converter_class

    @property
    def worker_class(self):
        """
        Worker class of program
        """
        return self._worker_class

    @property
    def exporter_class(self):
        """
        Exporter class of program
        """
        return self._exporter_class

    @property
    def importer_class(self):
        """
        Importer class of program
        """
        return self._importer_class

    def validate(self):
        pass
