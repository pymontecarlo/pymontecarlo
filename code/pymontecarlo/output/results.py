#!/usr/bin/env python
"""
================================================================================
:mod:`results` -- Container of all results
================================================================================

.. module:: results
   :synopsis: Container of all results

.. inheritance-diagram:: pymontecarlo.output.results

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
from StringIO import StringIO

# Third party modules.

# Local modules.
from pymontecarlo.output.manager import ResultManager
import pymontecarlo.output.result #@UnusedImport

from pymontecarlo.util.config import ConfigParser

# Globals and constants variables.
from zipfile import ZIP_DEFLATED

VERSION = '2'
SECTION_KEYS = 'keys'
KEYS_INI_FILENAME = 'keys.ini'

class Results(Mapping):

    def __init__(self, results={}):
        """
        Creates a new container for the results.
        Once created, the results container cannot be modified (i.e. read-only).
        
        :arg results: results to be part of this container.
            The results are specified by a key (key of the detector) and a
            :class:`Result <pymontecarlo.result.base.result.Result>` class.
        :type results: :class:`dict`
        """
        self._results = {}
        self._results.update(results)

    def __repr__(self):
        return '<Results(%s)>' % ', '.join(self._results.keys())

    @classmethod
    def load(cls, source):
        """
        Loads results from a results ZIP.
        
        :arg source: filepath or file-object
        
        :return: results container
        """
        zipfile = ZipFile(source, 'r')

        # Check version
        if zipfile.comment != 'version=%s' % VERSION:
            raise IOError, "Incorrect version of results. Only version %s is accepted" % \
                    VERSION

        # Parse keys.ini
        try:
            zipinfo = zipfile.getinfo(KEYS_INI_FILENAME)
        except KeyError:
            raise IOError, "Zip file (%s) does not contain a %s" % \
                    (getattr(source, 'name', 'unknown'), KEYS_INI_FILENAME)
        config = ConfigParser()
        config.read(zipfile.open(zipinfo, 'r'))

        # Load each results
        results = {}
        for key, tag in getattr(config, SECTION_KEYS):
            klass = ResultManager._get_class(tag)

            results[key] = klass.__loadzip__(zipfile, key)

        zipfile.close()

        return cls(results)

    def save(self, source):
        """
        Saves results in a results ZIP.
        
        :arg source: filepath or file-object
        """
        zipfile = ZipFile(source, 'w', compression=ZIP_DEFLATED)
        zipfile.comment = 'version=%s' % VERSION

        # Creates keys.ini
        config = ConfigParser()
        section = config.add_section(SECTION_KEYS)

        # Save each result and update keys.ini
        for key, result in self.iteritems():
            result.__savezip__(zipfile, key)

            tag = ResultManager._get_tag(result.__class__)
            setattr(section, key, tag)

        # Save keys.ini in zip
        fp = StringIO()
        config.write(fp)
        zipfile.writestr(KEYS_INI_FILENAME, fp.getvalue())

        zipfile.close()

    def __len__(self):
        return len(self._results)

    def __getitem__(self, key):
        return self._results[key]

    def __iter__(self):
        return iter(self._results)


