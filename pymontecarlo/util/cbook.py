"""
Cookbook solutions.
"""

# Standard library modules.
import math
import abc
import unicodedata
import re

# Third party modules.
import more_itertools

# Local modules.

# Globals and constants variables.

def are_sequence_equal(list0, list1):
    if len(list0) != len(list1):
        return False

    for item0, item1 in zip(list0, list1):
        if item0 != item1:
            return False

    return True

def are_sequence_similar(list0, list1):
    if len(list0) != len(list1):
        return False

    for item0 in list0:
        count = sum(item0 == item1 for item1 in list1)
        if count != 1:
            return False

    return True

def are_sequence_close(list0, list1, rel_tol=1e-9, abs_tol=0.0):
    if len(list0) != len(list1):
        return False

    for item0, item1 in zip(list0, list1):
        if not math.isclose(item0, item1, rel_tol=rel_tol, abs_tol=abs_tol):
            return False

    return True

def are_mapping_equal(map0, map1):
    if len(map0) != len(map1):
        return False

    for key in map0:
        if key not in map1:
            return False

        if map0[key] != map1[key]:
            return False

    return True

def are_mapping_value_close(map0, map1, rel_tol=1e-9, abs_tol=0.0):
    if len(map0) != len(map1):
        return False

    for key in map0:
        if key not in map1:
            return False

        if not math.isclose(map0[key], map1[key], rel_tol=rel_tol, abs_tol=abs_tol):
            return False

    return True

def unique(seq):
    return list(more_itertools.unique_everseen(seq))

def find_by_type(objects, clasz):
    found_objects = []
    for obj in objects:
        if isinstance(obj, clasz):
            found_objects.append(obj)
    return found_objects

def organize_by_type(objects):
    out = {}
    for obj in objects:
        clasz = obj.__class__
        out.setdefault(clasz, []).append(obj)
    return out

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    value = re.sub('[-\s]+', '-', value)
    return value

def get_valid_filename(s):
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
    >>> get_valid_filename("john's portrait in 2004.jpg")
    'johns_portrait_in_2004.jpg'
    """
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    s = s.strip().replace(' ', '_')
    s = re.sub(r'(?u)[^-\w.]', '', s)
    return s[:255]

class MultiplierAttribute(object):

    def __init__(self, attrname, multiplier):
        self.attrname = attrname
        self.multiplier = multiplier

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return getattr(instance, self.attrname) * self.multiplier

    def __set__(self, instance, value):
        setattr(instance, self.attrname, value / self.multiplier)

    def __delete__(self, instance):
        delattr(instance, self.attrname)

class DegreesAttribute(MultiplierAttribute):

    def __init__(self, attrname_rad):
        super().__init__(attrname_rad, 180.0 / math.pi)

class Monitorable(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def running(self):
        """
        Returns whether process is running
        """
        raise NotImplementedError

    @abc.abstractmethod
    def cancelled(self):
        raise NotImplementedError

    @abc.abstractproperty
    def progress(self):
        """
        Returns progress as a :class:`float` from 0.0 to 1.0.
        """
        return 0.0

    @abc.abstractproperty
    def status(self):
        """
        Returns status.
        """
        return ''
