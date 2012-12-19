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

    def reset(self):
        """
        Unregisters all loaders and savers.
        """
        self._loaders.clear()
        self._savers.clear()

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

class ClassManager(object):

    def __init__(self):
        self._map = {}

    def register(self, key_class, value_class):
        """
        Registers a link between two classes.
        
        Raises :exc:`KeyError` if the specified *key* class is already 
        associated with a different *value* class. 
        
        :arg key_class: *key* class
        :arg value_class: *value* class
        """
        if key_class in self._map and self._loaders.get(key_class) != value_class:
            raise KeyError, 'A class (%s) is already registered for (%s).' % \
                (self._loaders[key_class].__name__, key_class.__name__)

        self._map[key_class] = value_class

    def get(self, key_class, search_inheritance=True):
        """
        Returns the *value* class associated with the specified *key* class.
        If *search_inheritance* is ``True``, the base classes of the specified
        *key* class are searched to find a potential match.
        
        :arg key_class: *key* class
        :arg search_inheritance: whether to search for a match in the base
            classes of the specified *key* class (default: ``True``)
        """
        value_class = self._map.get(key_class, None)
        if value_class is not None:
            return value_class

        if search_inheritance:
            for base_class in key_class.__bases__:
                value_class = self._map.get(base_class, None)
                if value_class is not None:
                    return value_class

        raise KeyError, 'No class was found for %s.' % key_class.__name__
