#!/usr/bin/env python
"""
================================================================================
:mod:`results` -- Main container of all results
================================================================================

.. module:: results
   :synopsis: Main container of all results

.. inheritance-diagram:: results

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from collections import Mapping
from zipfile import ZipFile
from ConfigParser import SafeConfigParser
from StringIO import StringIO

# Third party modules.

# Local modules.
from pymontecarlo.result.base.manager import ResultManager

# Globals and constants variables.
SECTION_KEYS = 'keys'
KEYS_INI_FILENAME = 'keys.ini'

class Results(Mapping):

    def __init__(self, options, results={}):
        """
        Creates a new container for the results.
        Once created, the results container cannot be modified.
        
        :arg options: options used to generate these results
        :type options: :class:`Options <pymontecarlo.input.base.options.Options>`
        
        :arg results: results to be part of this container.
            The results are specified by a key (key of the detector) and a
            :class:`Result <pymontecarlo.result.base.result.Result>` class.
        :type results: :class:`dict`
        """
        self._options = options
        self._results = {}

        # Validate and populate
        for key, result in results.iteritems():
            if key not in options.detectors:
                raise ValueError, 'No detector was found in the options for result key (%s)' % key

            self._results[key] = result

    def __repr__(self):
        return '<Results(%s)>' % ', '.join(self._results.keys())

    @classmethod
    def load(cls, source, options):
        """
        Loads results from a results ZIP.
        
        :arg source: filepath or file-object
        
        :arg options: options used to generate these results
        :type options: :class:`Options <pymontecarlo.input.base.options.Options>`
        
        :return: results container
        """
        zipfile = ZipFile(source, 'r')

        # Parse keys.ini
        try:
            zipinfo = zipfile.getinfo(KEYS_INI_FILENAME)
        except KeyError:
            raise IOError, "Zip file (%s) does not contain a %s" % \
                    (getattr(source, 'name', 'unknown'), KEYS_INI_FILENAME)
        config = SafeConfigParser()
        config.readfp(zipfile.open(zipinfo, 'r'))

        # Load each results
        results = {}
        for key in config.options(SECTION_KEYS):
            tag = config.get(SECTION_KEYS, key)
            klass = ResultManager._get_class(tag)
            detector = options.detectors[key]

            results[key] = klass.__loadzip__(zipfile, key, detector)

        zipfile.close()

        return cls(options, results)

    def save(self, source):
        """
        Saves results in a results ZIP.
        
        :arg source: filepath or file-object
        """
        zipfile = ZipFile(source, 'w')

        # Creates keys.ini
        config = SafeConfigParser()
        config.add_section(SECTION_KEYS)

        # Save each result and update keys.ini
        for key, result in self.iteritems():
            result.__savezip__(zipfile, key)

            tag = ResultManager._get_tag(result.__class__)
            config.set(SECTION_KEYS, key, tag)

        # Save keys.ini in zip
        fp = StringIO()
        config.write(fp)
        zipfile.writestr(KEYS_INI_FILENAME, fp.getvalue())

        zipfile.close()

    @property
    def options(self):
        """
        Options used to generate the results.
        """
        return self._options

    def __len__(self):
        return len(self._results)

    def __getitem__(self, key):
        return self._results[key]

    def __iter__(self):
        return iter(self._results)


