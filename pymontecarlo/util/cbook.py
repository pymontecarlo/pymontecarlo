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
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    value = re.sub(r"[-\s]+", "-", value)
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
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.strip().replace(" ", "_")
    s = re.sub(r"(?u)[^-\w.=]", "", s)
    return s[:255]


def normalize_angle(angle_rad):
    """
    Ensure angle is between 0 and 360 (excluded).
    """
    angle_rad = angle_rad % (2 * math.pi)

    if angle_rad < 0:
        angle_rad += 2 * math.pi

    return angle_rad


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
        return ""
