#!/usr/bin/env python
"""
================================================================================
:mod:`geometry` -- Geometry definition for PENGEOM
================================================================================

.. module:: geometry
   :synopsis: Geometry definition for PENGEOM

.. inheritance-diagram:: penelopetools.api.input.pengeom.geometry

"""

# Script information for the file.
__email__ = "pypenelope-info@lists.sourceforge.net"
__author__ = "Philippe T. Pinard and Hendrix Demers"
__version__ = "0.2.4"
__date__ = ""
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard and Hendrix Demers"
__license__ = ""

# Standard library modules.
import math
from itertools import chain
from operator import methodcaller, attrgetter

# Third party modules.
from lxml.etree import Element
from pyparsing import (Word, ZeroOrMore, Optional, Suppress, alphanums,
                       ParseException, delimitedList, Group, printables, stringEnd)

# Local modules.
from pymontecarlo.input.base.geometry import _Geometry
from pymontecarlo.input.penelope.material import VACUUM
from pymontecarlo.input.penelope.body import Body
from pymontecarlo.input.base.option import Option
from pymontecarlo.util.xmlutil import objectxml
from pymontecarlo.util.sort import topological_sort

# Globals and constants variables.
_SURFACES_GETTER = methodcaller('get_surfaces')

LINE_SIZE = 64

LINE_START = 'X' * LINE_SIZE
LINE_SEPARATOR = '0' * LINE_SIZE
LINE_EXTRA = '1' * LINE_SIZE
LINE_END = 'END      0000000000000000000000000000000000000000000000000000000'

SIDEPOINTER_POSITIVE = 1
SIDEPOINTER_NEGATIVE = -1

AXIS_X = 'x'
AXIS_Y = 'y'
AXIS_Z = 'z'

LINE_SIZE = 64
LINE_KEYWORDS_SIZE = 8

class _Keyword(object):
    def __init__(self, name, termination=""):
        self._name = name
        self._termination = termination

    @property
    def name(self):
        return self._name

    @property
    def termination(self):
        return self._termination

    def _toexponent(self, number):
        """
        Formats exponent to PENELOPE format (E22.15)
        
        :arg number: number to format
        :type number: :class:`float`
        
        :rtype: :class:`str`
        """
        if number == 0.0:
            exponent = 0.0
        else:
            exponent = math.log10(abs(number))

        if exponent >= 0 :
            exponentStr = '+%2i' % abs(exponent)
        else:
            exponentStr = '-%2i' % abs(exponent)

        exponentStr = exponentStr.replace(' ', '0') #Replace white space in the exponent

        coefficient = float(abs(number)) / 10 ** int(exponent)

        if number >= 0:
            numberStr = '+%17.15fE%s' % (coefficient, exponentStr)
        else:
            numberStr = '-%17.15fE%s' % (coefficient, exponentStr)

        # The number should not be longer than 22 characters
        assert len(numberStr) == 22

        return numberStr

    def _extract_keyword_values_termination(self, line):
        """
        Extracts the keyword, the values and the termination of an input line.
        The values are returned as a list.
        
        :arg line: input line
        
        :return: keyword, values, comment
        """
        keywordletters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ-="
        keyword = Word(keywordletters, max=8)('keyword')

        value = Word(alphanums + ".-+")
        values = Group(Optional(delimitedList(value)))('vals')

        termination = ZeroOrMore(Word(printables))('termination')
        termination.setParseAction(lambda tokens: ' '.join(tokens))

        expr = keyword + Suppress("(") + values + Suppress(")") + termination + stringEnd

        try:
            result = expr.parseString(line)
        except ParseException:
            return None, None, None

        return result.keyword, result.vals, result.termination

    def _extract_keyword(self, line):
        """
        Returns the keyword of the specified line.
        
        :arg line: a line from the input file
        :type line: :class:`str`
        
        :rtype: :class:`str`
        """
        return self._extract_keyword_values_termination(line)[0]

    def _extract_values(self, line):
        """
        Returns the values inside the specified line.
        
        :arg line: a line from the input file
        :type line: :class:`str`
        
        :rtype: :class:`list`
        """
        return self._extract_keyword_values_termination(line)[1]

    def find_single_line(self, lines):
        """
        Finds the first line starting with this keyword.
        If no occurrence is not found, the exception :class:`KeywordNotFound` is raised.
    
        :arg lines: all the lines in the input file
        :type lines: :class:`list`
    
        :arg expected_keyword: keyword of the line of interest
        :type expected_keyword: :class:`str`
    
        :return: line
        :rtype: :class:`str`
        """
        for line in lines:
            keyword = self._extract_keyword(line)
            if keyword == self.name:
                return line

        raise ValueError

    def find_multiple_lines(self, lines):
        """
        Finds all the lines starting with the expected keyword.
        
        :arg lines: all the lines in the input file
        :type lines: :class:`list`
    
        :arg expected_keyword: keyword of the line of interest
        :type expected_keyword: :class:`str`
    
        :return: List of all the lines
        :rtype: :class:`list`
        """
        keywordlines = []

        for line in lines:
            keyword = self._extract_keyword(line)
            if keyword == self.name:
                keywordlines.append(line)

        return keywordlines

    def create_expline(self, value):
        """
        Creates a exponent line.
        This type of line is characterised by a keyword, a value express as an 
        exponent (see :meth:`._toexponent`) and a termination string.
        The keyword and the total length of the line is checked not to exceed 
        their respective maximum size.
        
        :arg keyword: 8-character keyword
        :arg value: value of the keyword
        :type value: :class:`float`
        :arg termination: termination of the line
        """
        keyword = self.name.rjust(LINE_KEYWORDS_SIZE)

        assert len(keyword) == LINE_KEYWORDS_SIZE

        line = '%s(%s,%4i)%s' % (keyword, self._toexponent(value), 0, self.termination)

        assert len(line) <= LINE_SIZE

        return line

    def create_line(self, text, override_comment=None):
        """
        Creates an input line from the specified keyword, text and comment.
        The white space between the items is automatically adjusted to fit the
        line size.
        The keyword and the total length of the line is checked not to exceed 
        their respective maximum size.
        
        :arg keyword: 8-character keyword
        :arg text: value of the keyword
        :arg comment: comment associated with the line
        """
        keyword = self.name.ljust(LINE_KEYWORDS_SIZE)

        assert len(keyword) == LINE_KEYWORDS_SIZE

        if override_comment is None:
            line = '%s(%s)%s' % (keyword, text, self.termination)
        else:
            line = '%s(%s)%s' % (keyword, text, override_comment)

        assert len(line) <= LINE_SIZE

        return line

class Rotation(Option):
    _KEYWORD_OMEGA = _Keyword('OMEGA=', ' DEG          (DEFAULT=0.0)')
    _KEYWORD_THETA = _Keyword('THETA=', ' DEG          (DEFAULT=0.0)')
    _KEYWORD_PHI = _Keyword('PHI=', ' DEG          (DEFAULT=0.0)')

    def __init__(self, omega_rad=0.0, theta_rad=0.0, phi_rad=0.0):
        """
        Represents a rotation using 3 Euler angles (YZY).
        
        :arg omega_rad: rotation around the z-axis (rad)
        :arg theta_rad: rotation around the y-axis (rad)
        :arg phi_rad: rotation around the new z-axis (rad)
        """
        Option.__init__(self)

        self.omega_rad = omega_rad
        self.theta_rad = theta_rad
        self.phi_rad = phi_rad

    def __repr__(self):
        return "<Rotation(omega=%s, theta=%s, phi=%s)>" % \
                    (self.omega_rad, self.theta_rad, self.phi_rad)

    def __str__(self):
        return '(omega=%s, theta=%s, phi=%s)' % \
                    (self.omega_rad, self.theta_rad, self.phi_rad)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        omega_rad = float(element.get('omega'))
        theta_rad = float(element.get('theta'))
        phi_rad = float(element.get('phi'))

        return cls(omega_rad, theta_rad, phi_rad)

    def __savexml__(self, element, *args, **kwargs):
        element.set('omega', str(self.omega_rad))
        element.set('theta', str(self.theta_rad))
        element.set('phi', str(self.phi_rad))

    @property
    def omega_rad(self):
        """
        Rotation around the z-axis (rad).
        The value must be between 0 and 2pi.
        """
        return self._props['omega']

    @omega_rad.setter
    def omega_rad(self, angle):
        if angle < 0 or angle > 2 * math.pi:
            raise ValueError, "Angle (%s) must be between [0,pi]." % angle
        self._props['omega'] = angle

    @property
    def theta_rad(self):
        """
        Rotation around the y-axis (rad).
        The value must be between 0 and 2pi.
        """
        return self._props['theta']

    @theta_rad.setter
    def theta_rad(self, angle):
        if angle < 0 or angle > 2 * math.pi:
            raise ValueError, "Angle (%s) must be between [0,pi]." % angle
        self._props['theta'] = angle

    @property
    def phi_rad(self):
        """
        Rotation around the new z-axis (rad).
        The new z-axis refer to the axis after the omega and theta rotation were
        applied on the original coordinate system.
        The value must be between 0 and 2pi.
        """
        return self._props['phi']

    @phi_rad.setter
    def phi_rad(self, angle):
        if angle < 0 or angle > 2 * math.pi:
            raise ValueError, "Angle (%s) must be between [0,pi]." % angle
        self._props['phi'] = angle

    def to_geo(self):
        """
        Returns the lines of this class to create a GEO file.
        """
        lines = []

        line = self._KEYWORD_OMEGA.create_expline(math.degrees(self.omega_rad))
        lines.append(line)

        line = self._KEYWORD_THETA.create_expline(math.degrees(self.theta_rad))
        lines.append(line)

        line = self._KEYWORD_PHI.create_expline(math.degrees(self.phi_rad))
        lines.append(line)

        return lines

class Shift(Option):
    _KEYWORD_X = _Keyword('X-SHIFT=', '              (DEFAULT=0.0)')
    _KEYWORD_Y = _Keyword('Y-SHIFT=', '              (DEFAULT=0.0)')
    _KEYWORD_Z = _Keyword('Z-SHIFT=', '              (DEFAULT=0.0)')

    def __init__(self, x_m=0.0, y_m=0.0, z_m=0.0):
        """
        Represents a translation in space.
        
        :arg x_m: translation along the x direction (m)
        :arg y_m: translation along the y direction (m)
        :arg z_m: translation along the z direction (m)
        """
        Option.__init__(self)

        self.x_m = x_m
        self.y_m = y_m
        self.z_m = z_m

    def __repr__(self):
        return "<Shift(x=%s, y=%s, z=%s)>" % (self.x_m, self.y_m, self.z_m)

    def __str__(self):
        return "(x=%s, y=%s, z=%s)" % (self.x_m, self.y_m, self.z_m)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        x_m = float(element.get('x'))
        y_m = float(element.get('y'))
        z_m = float(element.get('z'))

        return cls(x_m, y_m, z_m)

    def __savexml__(self, element, *args, **kwargs):
        element.set('x', str(self.x_m))
        element.set('y', str(self.y_m))
        element.set('z', str(self.z_m))

    @property
    def x_m(self):
        """
        Translation along the x direction (m).
        """
        return self._props['x']

    @x_m.setter
    def x_m(self, shift):
        self._props['x'] = shift

    @property
    def y_m(self):
        """
        Translation along the y direction (m).
        """
        return self._props['y']

    @y_m.setter
    def y_m(self, shift):
        self._props['y'] = shift

    @property
    def z_m(self):
        """
        Translation along the z direction (m).
        """
        return self._props['z']

    @z_m.setter
    def z_m(self, shift):
        self._props['z'] = shift

    def to_geo(self):
        """
        Returns the lines of this class to create a GEO file.
        """
        lines = []

        line = self._KEYWORD_X.create_expline(self.x_m * 100.0)
        lines.append(line)

        line = self._KEYWORD_Y.create_expline(self.y_m * 100.0)
        lines.append(line)

        line = self._KEYWORD_Z.create_expline(self.z_m * 100.0)
        lines.append(line)

        return lines

class Scale(Option):
    _KEYWORD_X = _Keyword('X-SCALE=', '              (DEFAULT=1.0)')
    _KEYWORD_Y = _Keyword('Y-SCALE=', '              (DEFAULT=1.0)')
    _KEYWORD_Z = _Keyword('Z-SCALE=', '              (DEFAULT=1.0)')

    def __init__(self, x=1.0, y=1.0, z=1.0):
        """
        Represents the scaling.
        
        :arg x: scaling along the x direction
        :arg y: scaling along the y direction
        :arg z: scaling along the z direction
        """
        Option.__init__(self)

        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return "<Shift(x=%s, y=%s, z=%s)>" % (self.x, self.y, self.z)

    def __str__(self):
        return "(x=%s, y=%s, z=%s)" % (self.x, self.y, self.z)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        x = float(element.get('x'))
        y = float(element.get('y'))
        z = float(element.get('z'))

        return cls(x, y, z)

    def __savexml__(self, element, *args, **kwargs):
        element.set('x', str(self.x))
        element.set('y', str(self.y))
        element.set('z', str(self.z))

    @property
    def x(self):
        """
        Scaling along the x direction.
        The value cannot be 0.
        """
        return self._props['x']

    @x.setter
    def x(self, scale):
        if scale == 0.0:
            raise ValueError, "X scale cannot be equal to 0."
        self._props['x'] = scale

    @property
    def y(self):
        """
        Scaling along the y direction.
        The value cannot be 0.
        """
        return self._props['y']

    @y.setter
    def y(self, scale):
        if scale == 0.0:
            raise ValueError, "Y scale cannot be equal to 0."
        self._props['y'] = scale

    @property
    def z(self):
        """
        Scaling along the z direction.
        The value cannot be 0.
        """
        return self._props['z']

    @z.setter
    def z(self, scale):
        if scale == 0.0:
            raise ValueError, "Z scale cannot be equal to 0."
        self._props['z'] = scale

    def to_geo(self):
        """
        Returns the lines of this class to create a GEO file.
        """
        lines = []

        line = self._KEYWORD_X.create_expline(self.x)
        lines.append(line)

        line = self._KEYWORD_Y.create_expline(self.y)
        lines.append(line)

        line = self._KEYWORD_Z.create_expline(self.z)
        lines.append(line)

        return lines

class _Surface(Option):
    _KEYWORD_SURFACE = _Keyword("SURFACE")
    _KEYWORD_INDICES = _Keyword('INDICES=')

    def __init__(self, description=''):
        Option.__init__(self)

        self.description = description

        self._props['rotation'] = Rotation()
        self._props['shift'] = Shift()

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        description = str(element.get('description'))
        obj = cls(description)

        child = list(element.find("rotation"))[0]
        obj._props['rotation'] = Rotation.from_xml(child, *args, **kwargs)

        child = list(element.find("shift"))[0]
        obj._props['shift'] = Shift.from_xml(child, *args, **kwargs)

        return obj

    def __savexml__(self, element, *args, **kwargs):
        element.set('index', str(self._index))
        element.set('description', str(self.description))

        child = Element('rotation')
        child.append(self.rotation.to_xml())
        element.append(child)

        child = Element('shift')
        child.append(self.shift.to_xml())
        element.append(child)

    @property
    def description(self):
        """
        Description of the surface.
        """
        return self._props['description']

    @description.setter
    def description(self, desc):
        self._props['description'] = desc

    @property
    def rotation(self):
        """
        Rotation of the surface.
        The rotation is defined by a :class:`.Rotation`.
        """
        return self._props['rotation']

    @property
    def shift(self):
        """
        Shift/translation of the surface.
        The shift is defined by a :class:`.Shift`.
        """
        return self._props['shift']

    def to_geo(self):
        lines = []

        text = "%4i" % (self._index + 1,)
        comment = " %s" % self.description
        line = self._KEYWORD_SURFACE.create_line(text, comment)
        lines.append(line)

        lines.extend(self.rotation.to_geo())
        lines.extend(self.shift.to_geo())

        return lines

class SurfaceImplicit(_Surface):
    _KEYWORD_AXX = _Keyword('AXX=', '              (DEFAULT=0.0)')
    _KEYWORD_AXY = _Keyword('AXY=', '              (DEFAULT=0.0)')
    _KEYWORD_AXZ = _Keyword('AXZ=', '              (DEFAULT=0.0)')
    _KEYWORD_AYY = _Keyword('AYY=', '              (DEFAULT=0.0)')
    _KEYWORD_AYZ = _Keyword('AYZ=', '              (DEFAULT=0.0)')
    _KEYWORD_AZZ = _Keyword('AZZ=', '              (DEFAULT=0.0)')
    _KEYWORD_AX = _Keyword('AX=', '              (DEFAULT=0.0)')
    _KEYWORD_AY = _Keyword('AY=', '              (DEFAULT=0.0)')
    _KEYWORD_AZ = _Keyword('AZ=', '              (DEFAULT=0.0)')
    _KEYWORD_A0 = _Keyword('A0=', '              (DEFAULT=0.0)')

    def __init__(self, coefficients=[0.0] * 10, description=''):
        _Surface.__init__(self, description)

        self.coefficients = coefficients

    def __repr__(self):
        coeffs = ['%s=%s' % (key, value) for key, value in self.coefficients.iteritems()]
        return '<Surface(description=%s, %s, rotation=%s, shift=%s)>' % \
            (self.description, ', '.join(coeffs), str(self.rotation), str(self.shift))

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        surface = _Surface.__loadxml__(element, *args, **kwargs)

        keys = ['xx', 'xy', 'xz', 'yy', 'yz', 'zz', 'x', 'y', 'z', '0']
        values = map(float, map(element.get, keys))
        coefficients = dict(zip(keys, values))

        obj = cls(coefficients, surface.description)
        obj._props['rotation'] = surface.rotation
        obj._props['shift'] = surface.shift

        return obj

    def __savexml__(self, element, *args, **kwargs):
        _Surface.__savexml__(self, element, *args, **kwargs)

        for key, value in self.coefficients.iteritems():
            element.set(key, str(value))

    @property
    def coefficients(self):
        """
        Coefficients for the implicit form of the quadratic equation.
        The coefficients are defined by a dictionary, a list or a tuple.
        See examples below. 
    
        **Examples**::
    
          >>> s = Surface()
          >>> s.coefficients = {'xx': 0.0, 'xy': 0.0, 'xz': 0.0, 'yy': 0.0, 'yz': 0.0, 'zz': 0.0, 'x': 0.0, 'y': 0.0, 'z': 0.0, '0': 0.0}
          >>> s.coefficients = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
          >>> s.coefficients = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
          >>> s.coefficients = {'xx': 1.0, 'xy': 1.0}
        """
        return self._props['coefficients']

    @coefficients.setter
    def coefficients(self, coefficients):
        if isinstance(coefficients, dict):
            self._props['coefficients'] = {'xx': 0.0, 'xy': 0.0, 'xz': 0.0,
                                           'yy': 0.0, 'yz': 0.0,
                                           'zz': 0.0,
                                           'x': 0.0, 'y': 0.0, 'z': 0.0, '0': 0.0}

            for key in coefficients:
                assert key in self._props['coefficients']
                self._props['coefficients'][key] = coefficients[key]
        else:
            assert len(coefficients) == 10

            self._props['coefficients'] = \
                {'xx': coefficients[0], 'xy': coefficients[1], 'xz': coefficients[2],
                 'yy': coefficients[3], 'yz': coefficients[4],
                 'zz': coefficients[5],
                 'x': coefficients[6], 'y': coefficients[7], 'z': coefficients[8],
                 '0': coefficients[9]}

    def to_geo(self):
        def create_coefficient_line(key):
            value = self.coefficients[key]
            keyword = getattr(self, "_KEYWORD_A" + key.upper())
            return keyword.create_expline(value)

        lines = _Surface.to_geo(self)

        # Indices
        text = "%2i,%2i,%2i,%2i,%2i" % (0, 0, 0, 0, 0)
        line = self._KEYWORD_INDICES.create_line(text)
        lines.insert(1, line)

        # Coefficients
        lines.insert(2, create_coefficient_line('xx'))
        lines.insert(3, create_coefficient_line('xy'))
        lines.insert(4, create_coefficient_line('xz'))
        lines.insert(5, create_coefficient_line('yy'))
        lines.insert(6, create_coefficient_line('yz'))
        lines.insert(7, create_coefficient_line('zz'))
        lines.insert(8, create_coefficient_line('x'))
        lines.insert(9, create_coefficient_line('y'))
        lines.insert(10, create_coefficient_line('z'))
        lines.insert(11, create_coefficient_line('0'))
        lines.insert(12, LINE_EXTRA)

        return lines

class SurfaceReduced(_Surface):

    def __init__(self, indices, description=''):
        _Surface.__init__(self, description)

        self.indices = indices
        self._props['scale'] = Scale()

    def __repr__(self):
        return '<Surface(description=%s, indices=%s, scale=%s, rotation=%s, shift=%s)>' % \
            (self.description, str(self.indices), str(self.scale),
             str(self.rotation), str(self.shift))

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        surface = _Surface.__loadxml__(element, *args, **kwargs)

        indices = map(int, map(element.get, 'abcde'))

        child = list(element.find("scale"))[0]
        scale = Scale.from_xml(child)

        obj = cls(indices, surface.description)
        obj._props['scale'] = scale
        obj._props['rotation'] = surface.rotation
        obj._props['shift'] = surface.shift

        return obj

    def __savexml__(self, element, *args, **kwargs):
        _Surface.__savexml__(self, element, *args, **kwargs)

        for key, value in zip('abcde', self.indices):
            element.set(key, str(value))

        child = Element('scale')
        child.append(self.scale.to_xml())
        element.append(child)

    @property
    def indices(self):
        """
        Indices for the explicit form of the quadratic equation.
        The indices are defined by a :class:`tuple` containing 5 indices (-1, 0 or 1).
        If the attribute is deleted, all the indices are set to 0.
        """
        return self._props['indices']

    @indices.setter
    def indices(self, indices):
        if len(indices) != 5:
            raise ValueError, "Five indices must be defined."

        for indice in indices:
            if not indice in [-1, 0, 1]:
                raise ValueError, "Index (%s) must be either -1, 0 or 1." % indice

        self._props['indices'] = tuple(indices)

    @property
    def scale(self):
        """
        Scaling of the surface.
        The scaling is defined by a :class:`.Scale`.
        """
        return self._props['scale']

    def to_geo(self):
        lines = _Surface.to_geo(self)

        # Indices
        text = "%2i,%2i,%2i,%2i,%2i" % self.indices
        line = self._KEYWORD_INDICES.create_line(text)
        lines.insert(1, line)

        for i, line in enumerate(self.scale.to_geo()):
            lines.insert(2 + i, line)

        return lines

def zplane(z_m):
    """
    Returns a surface for a plane Z=z
    
    :arg z_m: intercept on the z-axis (in m)
    
    :rtype: :class:`.Surface`
    """
    s = SurfaceReduced((0, 0, 0, 1, 0), 'Plane Z=%4.2f m' % z_m)
    s.shift.z_m = z_m
    return s

def xplane(x_m):
    """
    Returns a surface for a plane X=x
    
    :arg z_m: intercept on the x-axis (in m)
    
    :rtype: :class:`.Surface`
    """
    s = SurfaceReduced((0, 0, 0, 1, 0), 'Plane X=%4.2f m' % x_m)
    s.shift.x_m = x_m
    s.rotation.theta_rad = math.pi / 2.0
    return s

def yplane(y_m):
    """
    Returns a surface for a plane Y=y
    
    :arg y_m: intercept on the y-axis (in m)
    
    :rtype: :class:`.Surface`
    """
    s = SurfaceReduced((0, 0, 0, 1, 0), 'Plane Y=%4.2f m' % y_m)
    s.shift.y_m = y_m
    s.rotation.theta_rad = math.pi / 2.0
    s.rotation.phi_rad = math.pi / 2.0
    return s

def cylinder(radius_m, axis=AXIS_Z):
    """
    Returns a surface for a cylinder along *axis* with *radius*
    
    :arg radius_m: radius of the cylinder (in m)
    :arg axis: axis of the cylinder (:const:`AXIS_X`, :const:`AXIS_Y` or :const:`AXIS_Z`)
    
    :rtype: :class:`.Surface`
    """
    axis = axis.lower()
    description = 'Cylinder of radius %4.2f m along %s-axis' % (radius_m, axis)
    s = SurfaceReduced((1, 1, 0, 0, -1), description)

    s.scale.x = radius_m * 100
    s.scale.y = radius_m * 100

    if axis == 'z':
        pass
    elif axis == 'x':
        s.rotation.theta_rad = math.pi / 2.0
    elif axis == 'y':
        s.rotation.theta_rad = math.pi / 2.0
        s.rotation.phi_rad = math.pi / 2.0

    return s

def sphere(radius_m):
    """
    Returns a surface for a sphere or *radius*
    
    :arg radius_m: radius of the cylinder (in m)
    
    :rtype: :class:`.Surface`
    """
    description = 'Sphere of radius %4.2f m' % radius_m
    s = SurfaceReduced((1, 1, 1, 0, -1), description)

    s.scale.x = radius_m * 100
    s.scale.y = radius_m * 100
    s.scale.z = radius_m * 100

    return s

class Module(Body):
    _KEYWORD_MODULE = _Keyword("MODULE")
    _KEYWORD_MATERIAL = _Keyword('MATERIAL')
    _KEYWORD_SURFACE = _Keyword("SURFACE")
    _KEYWORD_SIDEPOINTER = ', SIDE POINTER='
    _KEYWORD_MODULE = _Keyword('MODULE')

    def __init__(self, material, description=''):
        Body.__init__(self, material)

        self.description = description

        self._props['surfaces'] = {}
        self._props['modules'] = set()

        self._props['rotation'] = Rotation()
        self._props['shift'] = Shift()

    def __repr__(self):
        return '<Module(description=%s, material=%s, %i interaction forcing(s), dsmax=%s m, surfaces_count=%i, modules_count=%i, rotation=%s, shift=%s)>' % \
            (self.description, self.material, len(self.interaction_forcings),
             self.maximum_step_length_m, len(self._surfaces), len(self._modules),
             str(self.rotation), str(self.shift))

    @classmethod
    def __loadxml__(cls, element, materials_lookup, surfaces_lookup,
                    modules_lookup, *args, **kwargs):
        index = int(element.find('material').get('index'))
        material = materials_lookup[index]

        body = Body.__loadxml__(element, material, *args, **kwargs)

        description = str(element.get('description'))
        obj = cls(body.material, description)
        obj._props['interaction forcings'] |= body.interaction_forcings
        obj.maximum_step_length_m = body.maximum_step_length_m

        children = list(element.find('surfaces'))
        for child in children:
            index = int(child.get('index'))
            pointer = int(child.get('pointer'))
            obj.add_surface(surfaces_lookup[index], pointer)

        children = list(element.find('modules'))
        for child in children:
            index = int(child.get('index'))
            obj.add_module(modules_lookup[index])

        child = list(element.find("rotation"))[0]
        obj._props['rotation'] = Rotation.from_xml(child, *args, **kwargs)

        child = list(element.find("shift"))[0]
        obj._props['shift'] = Shift.from_xml(child, *args, **kwargs)

        return obj

    def __savexml__(self, element, *args, **kwargs):
        Body.__savexml__(self, element, *args, **kwargs)

        element.remove(element.find('material'))

        element.set('index', str(self._index))
        element.set('description', str(self.description))

        attrib = {'index': str(self.material._index)}
        element.append(Element('material', attrib))

        child = Element('surfaces')
        surfaces = self._props['surfaces']
        for surface, pointer in surfaces.iteritems():
            attrib = {'index': str(surface._index), 'pointer': str(pointer)}
            child.append(Element('surface', attrib))
        element.append(child)

        child = Element('modules')
        modules = self._props['modules']
        for module in modules:
            attrib = {'index': str(module._index)}
            child.append(Element('module', attrib))
        element.append(child)

        child = Element('rotation')
        child.append(self.rotation.to_xml())
        element.append(child)

        child = Element('shift')
        child.append(self.shift.to_xml())
        element.append(child)

        return element

    @classmethod
    def from_body(cls, body, description=''):
        """
        Creates a module from a :class:`PenelopeBody`.
        """
        module = cls(body.material, description)

        module._props.update(body._props)

        return module

    @property
    def description(self):
        """
        Description of the module.
        """
        return self._props['description']

    @description.setter
    def description(self, desc):
        self._props['description'] = desc

    def add_module(self, module):
        if module == self:
            raise ValueError, "Cannot add this module to this module."
        self._props['modules'].add(module)

    def pop_module(self, module):
        self._props['modules'].discard(module)

    def clear_modules(self):
        self._props['modules'].clear()

    def get_modules(self):
        return list(self._props['modules'])

    def add_surface(self, surface, pointer):
        if pointer not in [-1, 1]:
            raise ValueError, "Pointer (%s) must be either -1 or 1." % pointer
        if surface in self._props['surfaces']:
            raise ValueError, "Module already contains this surface."
        self._props['surfaces'][surface] = pointer

    def pop_surface(self, surface):
        self._props['surfaces'].pop(surface)

    def clear_surfaces(self):
        self._props['surfaces'].clear()

    def get_surface_pointer(self, surface):
        """
        Returns the surface pointer for the specified surface.
        """
        return self._props['surfaces'][surface]

    def get_surfaces(self):
        return self._props['surfaces'].keys()

    @property
    def rotation(self):
        """
        Rotation of the surface.
        The rotation is defined by a :class:`.Rotation`.
        """
        return self._props['rotation']

    @property
    def shift(self):
        """
        Shift/translation of the surface.
        The shift is defined by a :class:`.Shift`.
        """
        return self._props['shift']

    def to_geo(self):
        """
        Returns the lines of this class to create a GEO file.
        """
        lines = []

        text = "%4i" % (self._index + 1,)
        comment = " %s" % self.description
        line = self._KEYWORD_MODULE.create_line(text, comment)
        lines.append(line)

        # Material index
        text = "%4i" % self.material._index
        line = self._KEYWORD_MATERIAL.create_line(text)
        lines.append(line)

        # Surface pointers
        surfaces = sorted(self.get_surfaces(), key=attrgetter('_index'))

        for surface in surfaces:
            text = "%4i" % (surface._index + 1,)
            comment = "%s(%2i)" % (self._KEYWORD_SIDEPOINTER, self.get_surface_pointer(surface))
            line = self._KEYWORD_SURFACE.create_line(text, comment)
            lines.append(line)

        # Module indexes
        modules = sorted(self.get_modules(), key=attrgetter('_index'))

        for module in modules:
            text = "%4i" % (module._index + 1,)
            line = self._KEYWORD_MODULE.create_line(text)
            lines.append(line)

        # Seperator
        lines.append(LINE_EXTRA)

        # Rotation
        lines.extend(self.rotation.to_geo())

        # Shift
        lines.extend(self.shift.to_geo())

        return lines

class PenelopeGeometry(_Geometry):

    def __init__(self, title="Untitled"):
        """
        Creates a new PENELOPE geometry.
        """
        _Geometry.__init__(self)

        self.title = title
        self._props['modules'] = set()

    @classmethod
    def _parse_xml_surfaces(cls, element):
        children = list(element.find('surfaces'))
        surfaces_lookup = {}
        for child in children:
            index = int(child.get('index'))
            surfaces_lookup[index] = objectxml.from_xml(child)

        return surfaces_lookup

    @classmethod
    def _parse_xml_modules(cls, element, materials_lookup, surfaces_lookup):
        children = list(element.find('modules'))
        modules_dep = {} # module dependencies
        modules_element = {} # module xml element
        for child in children:
            index = int(child.get('index'))
            modules_element[index] = child

            modules_dep.setdefault(index, [])
            for grandchild in list(child.find('modules')):
                modules_dep[index].append(int(grandchild.get('index')))

        modules_lookup = {}
        for index in modules_dep:
            for dep_index in topological_sort(modules_dep, index):
                if dep_index in modules_lookup: continue # skip already loaded module

                element = modules_element[dep_index]
                modules_lookup[dep_index] = \
                    objectxml.from_xml(element, materials_lookup,
                                        surfaces_lookup, modules_lookup)

        return modules_lookup

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        materials_lookup = cls._parse_xml_materials(element)
        surfaces_lookup = cls._parse_xml_surfaces(element)
        modules_lookup = cls._parse_xml_modules(element, materials_lookup, surfaces_lookup)

        title = str(element.get('title'))
        obj = cls(title)

        obj._props['modules'] |= set(modules_lookup.values())

        obj.tilt_rad = float(element.get('tilt'))
        obj.rotation_rad = float(element.get('rotation'))

        return obj

    def _surfaces_to_xml(self):
        element = Element('surfaces')
        for surface in self.get_surfaces():
            element.append(surface.to_xml())

        return element

    def _modules_to_xml(self):
        element = Element('modules')
        for module in self.modules:
            element.append(module.to_xml())

        return element

    def __savexml__(self, element, *args, **kwargs):
        self._indexify()

        element.set('title', self.title)
        element.set('tilt', str(self.tilt_rad))
        element.set('rotation', str(self.rotation_rad))

        element.append(self._materials_to_xml())
        element.append(self._surfaces_to_xml())
        element.append(self._modules_to_xml())

    @property
    def title(self):
        """
        Title of the geometry.
        The title must have less than 61 charaters.
        """
        return self._props['title']

    @title.setter
    def title(self, title):
        if len(title) > LINE_SIZE - 3:
            raise ValueError, "The length of the title (%i) must be less than %i." % \
                (len(title), LINE_SIZE - 3)
        self._props['title'] = title

    def get_bodies(self):
        return set(self._props['modules']) # copy

    def get_surfaces(self):
        return set(chain(*map(_SURFACES_GETTER, self.modules)))

    @property
    def modules(self):
        return self._props['modules']

    def _indexify(self):
        _Geometry._indexify(self)

        # Surfaces
        for i, surface in enumerate(self.get_surfaces()):
            surface._index = i

        # Modules
        modules_dep = {} # module dependencies
        for module in self.modules:
            modules_dep.setdefault(module, [])
            for submodule in module.get_modules():
                modules_dep[module].append(submodule)

        modules_order = []
        for module in modules_dep:
            for dep_module in topological_sort(modules_dep, module):
                if dep_module not in modules_order:
                    modules_order.append(dep_module)

        for i, module in enumerate(modules_order):
            module._index = i

    def to_geo(self):
        self._indexify()

        lines = []

        lines.append(LINE_START)
        lines.append('       %s' % self.title)
        lines.append(LINE_SEPARATOR)

        # Surfaces
        surfaces = sorted(self.get_surfaces(), key=attrgetter('_index'))
        for surface in surfaces:
            lines.extend(surface.to_geo())
            lines.append(LINE_SEPARATOR)

        # Modules
        modules = sorted(self.modules, key=attrgetter('_index'))
        for module in modules:
            lines.extend(module.to_geo())
            lines.append(LINE_SEPARATOR)

        # Extra module for tilt and rotation
        extra = Module(VACUUM, description='Extra module for rotation and tilt')

        ## Find all unlinked modules
        all_modules = set(self.modules)
        linked_modules = set(chain(*map(methodcaller('get_modules'), self.modules)))
        unlinked_modules = all_modules - linked_modules
        for module in unlinked_modules:
            extra.add_module(module)

        ## Change of Euler angles convention from ZXZ to ZYZ
        extra.rotation.omega_rad = (self.rotation_rad - math.pi / 2.0) % (2 * math.pi)
        extra.rotation.theta_rad = self.tilt_rad
        extra.rotation.phi_rad = math.pi / 2.0

        # Write module
        extra._index = len(self.modules)
        lines.extend(extra.to_geo())
        lines.append(LINE_SEPARATOR)

        # End of line
        lines.append(LINE_END)

        return lines

