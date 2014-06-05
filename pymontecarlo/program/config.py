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
from operator import attrgetter, methodcaller

# Third party modules.

# Local modules.
from pkg_resources import iter_entry_points

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

        # Validate exporters
        fields = [('BEAMS', '_beam_exporters'),
                  ('GEOMETRIES', '_geometry_exporters'),
                  ('DETECTORS', '_detector_exporters'),
                  ('LIMITS', '_limit_exporters'),
                  ('MODELS', '_model_exporters')]
        for field1, field2 in fields:
            exporter = exporter_class()
            expecteds = set(getattr(converter_class, field1))
            actuals = getattr(exporter, field2).keys()
            missings = expecteds - actuals
            if len(missings) > 0:
                s = ', '.join(map(attrgetter('__name__'), missings))
                raise ValueError("These %s cannot be exported: %s" % \
                                 (field1.lower(), s))

        # Validate importers
        expecteds = set(self.converter_class.DETECTORS)
        actuals = self.importer_class()._importers.keys()
        missings = expecteds - actuals
        if len(missings) > 0:
            s = ', '.join(map(attrgetter('__name__'), missings))
            raise ValueError("These %s cannot be imported: %s" % \
                             (field1.lower(), s))

        # Validate options handlers
        fields = [('MATERIALS', 'pymontecarlo.fileformat.options.material'),
                  ('BEAMS', 'pymontecarlo.fileformat.options.beam'),
                  ('GEOMETRIES', 'pymontecarlo.fileformat.options.geometry'),
                  ('DETECTORS', 'pymontecarlo.fileformat.options.detector'),
                  ('LIMITS', 'pymontecarlo.fileformat.options.limit')]
        for field1, field2 in fields:
            expecteds = set(getattr(converter_class, field1))
            actuals = set(map(attrgetter('CLASS'),
                              map(methodcaller('load'),
                                  iter_entry_points(field2))))
            missings = expecteds - actuals
            if len(missings) > 0:
                s = ', '.join(map(attrgetter('__name__'), missings))
                raise ValueError("These %s cannot be read/write: %s" % \
                                 (field1.lower(), s))

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

    def autoconfig(self, programs_path):
        return False

