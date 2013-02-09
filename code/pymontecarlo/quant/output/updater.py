#!/usr/bin/env python
"""
================================================================================
:mod:`updater` -- Quantification results updater
================================================================================

.. module:: updater
   :synopsis: Quantification results updater

.. inheritance-diagram:: pymontecarlo.quant.output.updater

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
from pymontecarlo.quant.output.results import Results
from pymontecarlo.util.config import ConfigParser

# Globals and constants variables.
from pymontecarlo.quant.output.results import VERSION

class Updater(_Updater):

    def __init__(self):
        """
        Creates a new updater for the results.
        """
        _Updater.__init__(self)

        self._updaters[1] = self._update_version1
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

    def _update_version1(self, filepath):
        logging.debug('Updating from "version 1"')

        oldzip = ZipFile(filepath, 'r')
        newzip = ZipFile(filepath + ".new", 'w')

        # Update stats.cfg
        config = ConfigParser()
        config.read(oldzip.open('stats.cfg', 'r'))

        limit = config.stats.convergence_limit
        del config.stats.convergence_limit
        config.stats.convergor = '<CompositionConvergor(limit=%s)>' % limit

        fp = StringIO()
        config.write(fp)
        newzip.writestr('stats.cfg', fp.getvalue())

        # Add other files to new zip
        for zipinfo in oldzip.infolist():
            if zipinfo.filename == 'stats.cfg':
                continue

            data = oldzip.read(zipinfo)
            newzip.writestr(zipinfo, data)

        # Add version
        newzip.comment = 'version=%s' % VERSION

        # Remove old zip and replace with new one
        os.remove(filepath)
        os.rename(filepath + ".new", filepath)

        oldzip.close()
        newzip.close()

        return filepath

    def _update_version2(self, filepath):
        logging.info('Nothing to update')
        return filepath
