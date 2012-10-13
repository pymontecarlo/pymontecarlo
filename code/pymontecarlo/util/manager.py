#!/usr/bin/env python
"""
================================================================================
:mod:`manager` -- Manager of loaders and savers
================================================================================

.. module:: manager
   :synopsis: Manager

.. inheritance-diagram:: pymontecarlo.util.manager

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

# Globals and constants variables.

class Manager(object):
    def __init__(self):
        self._loaders = {}
        self._savers = {}

    def register(self, tag, klass):
        """
        Associates a tag with a class. This class will be used to load the 
        specified tag. Every object of this class will be saved with the 
        specified tag.
        
        Raises :exc:`ValueError` if the specified tag is already associated with
        a different class. 
        
        :arg tag: tag for the class
        :arg klass: a class
        """
        self.register_loader(tag, klass)
        self.register_saver(tag, klass)

    def register_loader(self, tag, klass):
        """
        Associates a tag with a class. This class will be used to load the 
        specified tag.
        
        Raises :exc:`ValueError` if the specified tag is already associated with
        a different class. 
        Note that several loaders can be associated with the same class.
        
        :arg tag: tag for the class
        :arg klass: a class
        """
        if tag in self._loaders and self._loaders.get(tag) != klass:
            raise ValueError, 'A class (%s) is already registered with the tag (%s).' % \
                (self._loaders[tag].__name__, tag)

        self._loaders[tag] = klass

    def register_saver(self, tag, klass):
        """
        Associates a tag with a class. Every object of this class will be saved
        with the specified tag.
        
        Raises :exc:`ValueError` if the specified tag is already associated with
        a different class. 
        Note that a class can only have one tag.
        
        :arg tag: tag for the class
        :arg klass: a class
        """
        if klass in self._savers and self._savers.get(klass) != tag:
            raise ValueError, 'A tag (%s) is already associated with class (%s).' % \
                (self._savers[klass], klass.__name__)

        self._savers[klass] = tag

    def get_class(self, tag):
        """
        Returns the loader class for the specified tag.
        Raises :exc:`ValueError` if no class is associated with this tag.
        
        :arg tag: tag associated with a class
        
        :return: loader class
        """
        if tag not in self._loaders:
            raise ValueError, 'No loader found for element (%s). Please register it first.' % tag
        return self._loaders[tag]

    def get_tag(self, klass):
        """
        Returns the tag for the specified class.
        Raises :exc:`ValueError` if no tag is associated with this class.
        
        :arg klass: class associated with a tag
        
        :return: tag for the class
        """
        if klass not in self._savers:
            raise ValueError, 'No saver found for class (%s). Please register it first.' % klass
        return self._savers[klass]

