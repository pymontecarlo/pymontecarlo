#!/usr/bin/env python
"""
================================================================================
:mod:`config` -- Configuration parser
================================================================================

.. module:: config
   :synopsis: Read configuration file

.. inheritance-diagram:: pymontecarlo.util.config

Configuration parser to read INI type files. 
This parser differs slightly from those available in the :mod:`ConfigParser`
module as the sections, options and values can be accessed using attributes
instead of getters and setters.
While the access of the data is different, this class uses the 
:class:`SafeConfigParser` of the :mod:`ConfigParser` module to read and
write configuration file.

.. warning::

   This parser does *not* support section or option starting with a number.

Let's take the configuration file::

  [section1]
  option1=value1
  option2=value2
  
  [section2]
  option3 = value3
  
To load the configuration file, use the :meth:`read` method::

  >>> config = ConfigParser()
  >>> with open(filepath, 'r') as fp:
  ...     config.read(fp)

To get the value of ``option1`` in ``section1``::

  >>> config.section1.option1
  'value1'

or of ``option3`` in ``section2``::

  >>> config.section2.option3
  'value3'

To check if a section is present, use the ``in`` statement::

  >>> 'section3' in config
  False
  >>> 'option2' in config.section1
  True

To iterate over all sections and options::

  >>> for section, option, value in config:
  ...     print section, option, value
  'section1' 'option1' 'value1'
  'section1' 'option2' 'value2'
  'section2' 'option3' 'value3'

Note that the order may changed.

To add a section or option::

  >>> config.add_section('section3')
  >>> 'section3' in config
  True
  >>> config.section3.option4 = 'value4'

The following syntax can be shorten as :meth:`add_section` method returns the
added section::

  >>> config.add_section('section3').option4 = 'value4'

If the added section already exists, no section is added and the current one
is returned::

  >>> config.add_section('section1').option1
  'value1'

Finally, the configuration can be saved back to a file::

  >>> with open(filepath, 'w') as fp:
  ...     config.write(fp)

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
    def __init__(self, options={}):
        self.__dict__.update(options)

    def __iter__(self):
        for option_name, value in self.__dict__.iteritems():
            yield option_name, value

    def __contains__(self, option_name):
        return option_name in self.__dict__

class ConfigParser(object):
    """
    Configuration parser.
    """

    def __contains__(self, section_name):
        return section_name in self.__dict__

    def __iter__(self):
        for section_name, section in self.__dict__.iteritems():
            for option_name, value in section:
                yield section_name, option_name, value

    def add_section(self, section_name):
        """
        Adds a new section if the specified section name doesn't exist.
        Does nothing if the section already exists.
        
        :return: section
        """
        if section_name not in self.__dict__:
            self.__dict__[section_name] = _Section()
        return self.__dict__[section_name]

    def read(self, fileobj, ignore_errors=False):
        """
        Reads the configuration from the file object.
        
        If ``ignore_errors`` is ``True`` and a section or option starts with 
        a number, a :exc:`IOError` exception is raised.
        If not, these sections or options are skipped. 
        
        :arg fileobj: file object
        :arg ignore_errors: whether to raise exception or skip invalid 
            section(s) and option(s)
        """
        parser = SafeConfigParser()
        parser.readfp(fileobj)

        for section in parser.sections():
            if section[0].isdigit():
                if ignore_errors:
                    continue
                raise IOError, "Section name (%s) cannot start with a digit" % section

            options = {}

            for option in parser.options(section):
                if option[0].isdigit():
                    if ignore_errors:
                        continue
                    raise IOError, "Option name (%s) cannot start with a digit" % option

                options[option] = parser.get(section, option)

            self.__dict__[section] = _Section(options)

    def write(self, fileobj):
        """
        Writes the configuration inside the file object.
        
        :arg fileobj: file object
        """
        parser = SafeConfigParser()

        # Add sections
        for section_name in self.__dict__:
            parser.add_section(section_name)

        # Add options
        for section_name, option_name, value in self:
            parser.set(section_name, option_name, str(value))

        parser.write(fileobj)
