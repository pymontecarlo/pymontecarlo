#!/usr/bin/env python
"""
================================================================================
:mod:`updater` -- Base class for updaters
================================================================================

.. module:: updater
   :synopsis: Base class for updaters

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import shutil
import logging

# Third party modules.

# Local modules.

# Globals and constants variables.

class _Updater(object):
    """
    Base class of all updaters.
    Derived class must implement the method :meth:`_get_version` and registers
    updater function in the :attr:`_updaters` dictionary.
    Updater functions takes only one argument which is the path to the file
    to be updated.
    The method :meth:`_validate` can also be overridden for validation.
    """

    def __init__(self):
        self._updaters = {}

    def update(self, filepath, validate=True):
        """
        Updates the specified file to the most current file format.
        
        :arg filepath: path to the file to be updated
        :arg validate: whether to validate the updated file [default:``True``]
        """
        version = self._get_version(filepath)

        updater = self._updaters.get(version)
        if not updater:
            raise ValueError, "Cannot update %s" % filepath

        bak_filepath = self._make_backup(filepath)
        logging.debug("Backup at %s", bak_filepath)

        updater(filepath)
        logging.debug("File (%s) was updated", filepath)

        if validate:
            self._validate(filepath)
            logging.debug("File (%s) is valid", filepath)

    def _make_backup(self, filepath):
        """
        Creates a copy of the specified file.
        
        :arg filepath: path to the original file
        
        :return: filepath of the backup file
        """
        bak_filepath = filepath + '.bak'
        shutil.copy2(filepath, bak_filepath)
        return bak_filepath

    def _get_version(self, filepath):
        """
        Returns the version of the file.
        The method should returns ``0`` if no version is found.
        
        :arg filepath: path to the file to be updated 
        """
        raise NotImplementedError

    def _validate(self, filepath):
        """
        Validates the updated file.
        The method should raise an exception if the file is not valid.
        
        :arg filepath: path to the updated file
        """
        pass

