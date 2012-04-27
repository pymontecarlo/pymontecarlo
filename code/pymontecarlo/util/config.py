#!/usr/bin/env python
"""
================================================================================
:mod:`config` -- Read configuration file
================================================================================

.. module:: config
   :synopsis: Read configuration file

.. inheritance-diagram:: pymontecarlo.util.config

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from ConfigParser import SafeConfigParser

# Third party modules.

# Local modules.

# Globals and constants variables.

class _Section(object):
    def __init__(self, options):
        self.__dict__.update(options)

    def __iter__(self):
        for option_name, value in self.__dict__.iteritems():
            yield option_name, value

    def __contains__(self, option_name):
        return option_name in self.__dict__

class ConfigParser(object):

    def read(self, fileobj):
        parser = SafeConfigParser()
        parser.readfp(fileobj)

        for section in parser.sections():
            options = {}

            for option in parser.options(section):
                options[option] = parser.get(section, option)

            self.__dict__[section] = _Section(options)

    def __contains__(self, section_name):
        return section_name in self.__dict__

    def __iter__(self):
        for section_name, section in self.__dict__.iteritems():
            for option_name, value in section:
                yield section_name, option_name, value

    def write(self, fileobj):
        parser = SafeConfigParser()

        # Add sections
        for section_name in self.__dict__:
            parser.add_section(section_name)

        # Add options
        for section_name, option_name, value in self:
            parser.set(section_name, option_name, value)

        parser.write(fileobj)
