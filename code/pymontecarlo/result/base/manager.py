#!/usr/bin/env python
"""
================================================================================
:mod:`manager` -- Results manager
================================================================================

.. module:: manager
   :synopsis: Results manager

.. inheritance-diagram:: pymontecarlo.result.base.manager

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
from pymontecarlo.util.manager import Manager

# Globals and constants variables.

class Result(object):

    def __init__(self, detector):
        self._detector = detector

    @classmethod
    def __loadzip__(cls, zipfile, key, detector):
        return cls(detector)

    def __savezip__(self, zipfile, key):
        pass

    @property
    def detector(self):
        """
        Detector associated to this result.
        """
        return self._detector

class _ResultsManager(Manager):
    def register_loader(self, tag, klass):
        if not issubclass(klass, Result):
            raise ValueError, 'The class (%s) must be a subclass of Result.' % \
                klass.__name__

        Manager.register_loader(self, tag, klass)

    def register_saver(self, tag, klass):
        if not issubclass(klass, Result):
            raise ValueError, 'The class (%s) must be a subclass of Result.' % \
                klass.__name__

        Manager.register_saver(self, tag, klass)

ResultsManager = _ResultsManager()
