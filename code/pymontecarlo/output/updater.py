#!/usr/bin/env python
"""
================================================================================
:mod:`updater` -- Results updater
================================================================================

.. module:: updater
   :synopsis: Results updater

.. inheritance-diagram:: pymontecarlo.output.updater

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import logging
from zipfile import ZipFile
import os
from StringIO import StringIO

# Third party modules.

# Local modules.
from pymontecarlo.util.updater import _Updater
from pymontecarlo.output.results import Results
from pymontecarlo.util.config import ConfigParser

# Globals and constants variables.
from pymontecarlo.output.results import KEYS_INI_FILENAME, VERSION

class Updater(_Updater):

    def __init__(self):
        """
        Creates a new updater for the results.
        """
        _Updater.__init__(self)

        self._updaters[0] = self._update_noversion
        self._updaters[2] = self._update_version2

    def _get_version(self, filepath):
        with ZipFile(filepath, 'r') as zip:
            comment = zip.comment

        try:
            return int(comment.split('=')[1])
        except:
            return 0

    def _validate(self, filepath):
        Results.load(filepath)

    def _update_noversion(self, filepath):
        logging.debug('Updating from "no version"')

        oldzip = ZipFile(filepath, 'r')
        newzip = ZipFile(filepath + ".new", 'w')

        # Update keys.ini
        config = ConfigParser()
        config.read(oldzip.open(KEYS_INI_FILENAME, 'r'))

        for section, option, value in config:
            value = value.replace('pymontecarlo.result.base.result.', '')
            setattr(getattr(config, section), option, value)

        fp = StringIO()
        config.write(fp)
        newzip.writestr(KEYS_INI_FILENAME, fp.getvalue())

        # Add other files to new zip
        for zipinfo in oldzip.infolist():
            if zipinfo.filename == KEYS_INI_FILENAME:
                continue

            data = oldzip.read(zipinfo)
            newzip.writestr(zipinfo, data)

        # Add version
        newzip.comment = 'version=%s' % VERSION

        oldzip.close()
        newzip.close()

        # Remove old zip and replace with new one
        os.remove(filepath)
        os.rename(filepath + ".new", filepath)

    def _update_version2(self, filepath):
        logging.info('Nothing to update')
