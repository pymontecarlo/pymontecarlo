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
import sys
from collections import Mapping
from zipfile import ZipFile
from ConfigParser import SafeConfigParser
from StringIO import StringIO

# Third party modules.

# Local modules.

# Globals and constants variables.
SECTION_KEYS = 'keys'

class Results(Mapping):

    def __init__(self, options, results={}):
        self._options = options
        self._results = dict(results) # copy

    def __repr__(self):
        return '<Results(%s)>' % ', '.join(self._results.keys())

    @classmethod
    def load(cls, fileobj, options):
        zipfile = ZipFile(fileobj, 'r')

        # Parse keys.ini
        try:
            zipinfo = zipfile.getinfo('keys.ini')
        except KeyError:
            raise IOError, "Zip file (%s) does not contain a keys.ini" % fileobj
        config = SafeConfigParser()
        config.readfp(zipfile.open(zipinfo, 'r'))

        # Load each results
        results = {}
        for key in config.options(SECTION_KEYS):
            module, name = config.get(SECTION_KEYS, key).rsplit('.', 1)
            detector = options.detectors[key]

            # This import technique is the same as the one used in pickle
            # See Unpickler.find_class
            __import__(module)
            mod = sys.modules[module]
            klass = getattr(mod, name)

            results[key] = klass.__loadzip__(zipfile, key, detector)

        zipfile.close()

        return cls(options, results)

    def save(self, fileobj):
        zipfile = ZipFile(fileobj, 'w')

        # Creates keys.ini
        config = SafeConfigParser()
        config.add_section(SECTION_KEYS)

        # Save each result and update keys.ini
        for key, result in self.iteritems():
            result.__savezip__(zipfile, key)

            value = result.__class__.__module__ + "." + result.__class__.__name__
            config.set(SECTION_KEYS, key, value)

        # Save keys.ini in zip
        fp = StringIO()
        config.write(fp)
        zipfile.writestr('keys.ini', fp.getvalue())

        zipfile.close()

    @property
    def options(self):
        return self._options

    def __len__(self):
        return len(self._results)

    def __getitem__(self, key):
        return self._results[key]

    def __iter__(self):
        return iter(self._results)


