"""
Cookbook solutions.
"""

# Standard library modules.
import math

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
