#!/usr/bin/env python
"""
================================================================================
:mod:`manager` -- Runner manager
================================================================================

.. module:: manager
   :synopsis: Runner manager

.. inheritance-diagram:: manager

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
from pymontecarlo.runner.base.runner import Runner

# Globals and constants variables.

class _RunnerManager(Manager):

    def register_loader(self, tag, klass):
        if not issubclass(klass, Runner):
            raise ValueError, 'The class (%s) must be a subclass of Runner.' % \
                klass.__name__

        Manager.register_loader(self, tag, klass)

    def register_saver(self, tag, klass):
        if not issubclass(klass, Runner):
            raise ValueError, 'The class (%s) must be a subclass of Runner.' % \
                klass.__name__

        Manager.register_saver(self, tag, klass)

RunnerManager = _RunnerManager()
