#!/usr/bin/env python
"""
================================================================================
:mod:`geometry` -- Geometry definition for PENGEOM
================================================================================

.. module:: geometry
   :synopsis: Geometry definition for PENGEOM

.. inheritance-diagram:: pymontecarlo.program._penelope.input.geometry

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
from collections import namedtuple

# Third party modules.
from pyparsing import (Word, ZeroOrMore, Optional, Suppress, alphanums,
                       ParseException, delimitedList, Group, printables, stringEnd)

# Local modules.
from pymontecarlo.input.geometry import _Geometry
from pymontecarlo.input.material import VACUUM
from pymontecarlo.input.parameter import \
    (ParameterizedMetaClass, Parameter, UnitParameter, AngleParameter,
     FrozenParameter, SimpleValidator, CastValidator,
     ParameterizedMutableMapping, ParameterizedMutableSet)
from pymontecarlo.input.xmlmapper import \
    (mapper, Attribute, ParameterizedElement, ParameterizedElementDict,
     ParameterizedElementSet, ParameterizedAttribute, PythonType, UserType)

from pymontecarlo.program._penelope.input.body import Body

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

_rotation_validator = SimpleValidator(lambda x: 0.0 <= x <= 2 * math.pi)

class Rotation(object):
    
    __metaclass__ = ParameterizedMetaClass
    
    _KEYWORD_OMEGA = _Keyword('OMEGA=', ' DEG          (DEFAULT=0.0)')
    _KEYWORD_THETA = _Keyword('THETA=', ' DEG          (DEFAULT=0.0)')
    _KEYWORD_PHI = _Keyword('PHI=', ' DEG          (DEFAULT=0.0)')

    omega = AngleParameter(_rotation_validator,
                           "Rotation around the z-axis between 0 and 2pi.")
    theta = AngleParameter(_rotation_validator,
                           "Rotation around the y-axis between 0 and 2pi.")
    phi = AngleParameter(_rotation_validator,
                         "Rotation around the new z-axis between 0 and 2pi.")

    def __init__(self, omega_rad=0.0, theta_rad=0.0, phi_rad=0.0):
        """
        Represents a rotation using 3 Euler angles (YZY).
        
        :arg omega_rad: rotation around the z-axis (rad)
        :arg theta_rad: rotation around the y-axis (rad)
        :arg phi_rad: rotation around the new z-axis (rad)
        """
        self.omega_rad = omega_rad
        self.theta_rad = theta_rad
        self.phi_rad = phi_rad

    def __repr__(self):
        return "<Rotation(omega=%s, theta=%s, phi=%s)>" % \
                    (self.omega_rad, self.theta_rad, self.phi_rad)

    def __str__(self):
        return '(omega=%s, theta=%s, phi=%s)' % \
                    (self.omega_rad, self.theta_rad, self.phi_rad)

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

mapper.register(Rotation, '{http://pymontecarlo.sf.net/penelope}rotation',
                ParameterizedAttribute('omega_rad', PythonType(float), 'omega'),
                ParameterizedAttribute('theta_rad', PythonType(float), 'theta'),
                ParameterizedAttribute('phi_rad', PythonType(float), 'phi'))

class Shift(object):

    __metaclass__ = ParameterizedMetaClass

    _KEYWORD_X = _Keyword('X-SHIFT=', '              (DEFAULT=0.0)')
    _KEYWORD_Y = _Keyword('Y-SHIFT=', '              (DEFAULT=0.0)')
    _KEYWORD_Z = _Keyword('Z-SHIFT=', '              (DEFAULT=0.0)')

    x = UnitParameter('m', doc="translation along the x direction")
    y = UnitParameter('m', doc="translation along the y direction")
    z = UnitParameter('m', doc="translation along the z direction")

    def __init__(self, x_m=0.0, y_m=0.0, z_m=0.0):
        """
        Represents a translation in space.
        
        :arg x_m: translation along the x direction (m)
        :arg y_m: translation along the y direction (m)
        :arg z_m: translation along the z direction (m)
        """
        self.x_m = x_m
        self.y_m = y_m
        self.z_m = z_m

    def __repr__(self):
        return "<Shift(x=%s, y=%s, z=%s)>" % (self.x_m, self.y_m, self.z_m)

    def __str__(self):
        return "(x=%s, y=%s, z=%s)" % (self.x_m, self.y_m, self.z_m)

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

mapper.register(Shift, '{http://pymontecarlo.sf.net/penelope}shift',
                ParameterizedAttribute('x_m', PythonType(float), 'x'),
                ParameterizedAttribute('y_m', PythonType(float), 'y'),
                ParameterizedAttribute('z_m', PythonType(float), 'z'))

_scale_validator = SimpleValidator(lambda x: x != 0.0)

class Scale(object):

    __metaclass__ = ParameterizedMetaClass

    _KEYWORD_X = _Keyword('X-SCALE=', '              (DEFAULT=1.0)')
    _KEYWORD_Y = _Keyword('Y-SCALE=', '              (DEFAULT=1.0)')
    _KEYWORD_Z = _Keyword('Z-SCALE=', '              (DEFAULT=1.0)')

    x = Parameter(_scale_validator, "scaling along the x direction")
    y = Parameter(_scale_validator, "scaling along the y direction")
    z = Parameter(_scale_validator, "scaling along the z direction")

    def __init__(self, x=1.0, y=1.0, z=1.0):
        """
        Represents the scaling.
        
        :arg x: scaling along the x direction
        :arg y: scaling along the y direction
        :arg z: scaling along the z direction
        """
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return "<Shift(x=%s, y=%s, z=%s)>" % (self.x, self.y, self.z)

    def __str__(self):
        return "(x=%s, y=%s, z=%s)" % (self.x, self.y, self.z)

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

mapper.register(Scale, '{http://pymontecarlo.sf.net/penelope}scale',
                ParameterizedAttribute('x', PythonType(float)),
                ParameterizedAttribute('y', PythonType(float)),
                ParameterizedAttribute('z', PythonType(float)))

class _Surface(object):

    __metaclass__ = ParameterizedMetaClass

    _KEYWORD_SURFACE = _Keyword("SURFACE")
    _KEYWORD_INDICES = _Keyword('INDICES=')

    description = Parameter(CastValidator(str), 'Description')

    rotation = Parameter(doc="Rotation")

    shift = Parameter(doc="Shift")

    def __init__(self, description=''):
        self.description = description

        self.rotation = Rotation()
        self.shift = Shift()

    def to_geo(self):
        lines = []

        text = "%4i" % (self._index + 1,)
        comment = " %s" % self.description
        line = self._KEYWORD_SURFACE.create_line(text, comment)
        lines.append(line)

        lines.extend(self.rotation.to_geo())
        lines.extend(self.shift.to_geo())

        return lines

mapper.register(_Surface, '{http://pymontecarlo.sf.net/penelope}_surface',
                ParameterizedAttribute('description', PythonType(str)),
                ParameterizedElement('rotation', UserType(Rotation)),
                ParameterizedElement('shift', UserType(Shift)))

class implicit(namedtuple('implicit', ['axx', 'axy', 'axz', 'ayy', 'ayz',
                                       'azz', 'ax', 'ay', 'az', 'a0'])):
    pass

mapper.register(implicit,
                '{http://pymontecarlo.sf.net/penelope}implicit',
                Attribute('axx', PythonType(float)),
                Attribute('axy', PythonType(float)),
                Attribute('axz', PythonType(float)),
                Attribute('ayy', PythonType(float)),
                Attribute('ayz', PythonType(float)),
                Attribute('azz', PythonType(float)),
                Attribute('ax', PythonType(float)),
                Attribute('ay', PythonType(float)),
                Attribute('az', PythonType(float)),
                Attribute('a0', PythonType(float)),)

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

    coefficients = \
        Parameter(CastValidator(implicit),
                  "Coefficients for the implicit form of the quadratic equation.")

    def __init__(self, coefficients=None, description=''):
        _Surface.__init__(self, description)

        if coefficients is None:
            coefficients = implicit(0.0, 0.0, 0.0, 0.0, 0.0,
                                    0.0, 0.0, 0.0, 0.0, 0.0)
        self.coefficients = coefficients

    def __repr__(self):
        coeffs = ['%s=%s' % (key, value) \
                  for key, value in self.coefficients._asdict().iteritems()]
        return '<Surface(description=%s, %s, rotation=%s, shift=%s)>' % \
            (self.description, ', '.join(coeffs), str(self.rotation), str(self.shift))

    def to_geo(self):
        def create_coefficient_line(key):
            value = getattr(self.coefficients, key)
            keyword = getattr(self, "_KEYWORD_" + key.upper())
            return keyword.create_expline(value)

        lines = _Surface.to_geo(self)

        # Indices
        text = "%2i,%2i,%2i,%2i,%2i" % (0, 0, 0, 0, 0)
        line = self._KEYWORD_INDICES.create_line(text)
        lines.insert(1, line)

        # Coefficients
        lines.insert(2, create_coefficient_line('axx'))
        lines.insert(3, create_coefficient_line('axy'))
        lines.insert(4, create_coefficient_line('axz'))
        lines.insert(5, create_coefficient_line('ayy'))
        lines.insert(6, create_coefficient_line('ayz'))
        lines.insert(7, create_coefficient_line('azz'))
        lines.insert(8, create_coefficient_line('ax'))
        lines.insert(9, create_coefficient_line('ay'))
        lines.insert(10, create_coefficient_line('az'))
        lines.insert(11, create_coefficient_line('a0'))
        lines.insert(12, LINE_EXTRA)

        return lines

mapper.register(SurfaceImplicit,
                '{http://pymontecarlo.sf.net/penelope}surface_implicit',
                ParameterizedElement('coefficients', UserType(implicit)))

class indices(namedtuple('indices', ['a', 'b', 'c', 'd', 'e'])):

    def __new__(cls, a, b, c, d, e):
        for v in [a, b, c, d, e]:
            if v not in [-1, 0, 1]:
                raise ValueError, "Indices must either be -1, 0, or 1"
        return cls.__bases__[0].__new__(cls, a, b, c, d, e)

mapper.register(indices,
                '{http://pymontecarlo.sf.net/penelope}indices',
                Attribute('a', PythonType(int)),
                Attribute('b', PythonType(int)),
                Attribute('c', PythonType(int)),
                Attribute('d', PythonType(int)),
                Attribute('e', PythonType(int)))

class SurfaceReduced(_Surface):

    indices = Parameter(CastValidator(indices),
                        "Indices for the explicit form of the quadratic equation. The indices are defined by a :class:`tuple` containing 5 indices (-1, 0 or 1).")

    scale = Parameter(doc="Scale")

    def __init__(self, indices, description=''):
        _Surface.__init__(self, description)

        self.indices = indices
        self.scale = Scale()

    def __repr__(self):
        return '<Surface(description=%s, indices=%s, scale=%s, rotation=%s, shift=%s)>' % \
            (self.description, str(self.indices), str(self.scale),
             str(self.rotation), str(self.shift))

    def to_geo(self):
        lines = _Surface.to_geo(self)

        # Indices
        text = "%2i,%2i,%2i,%2i,%2i" % self.indices
        line = self._KEYWORD_INDICES.create_line(text)
        lines.insert(1, line)

        for i, line in enumerate(self.scale.to_geo()):
            lines.insert(2 + i, line)

        return lines

mapper.register(SurfaceReduced,
                '{http://pymontecarlo.sf.net/penelope}surface_reduced',
                ParameterizedElement('indices', UserType(indices)),
                ParameterizedElement('scale', UserType(Scale)))

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

    description = Parameter(CastValidator(str), 'Description')

    _surfaces = FrozenParameter(ParameterizedMutableMapping)

    _modules = FrozenParameter(ParameterizedMutableSet)

    rotation = Parameter(doc="Rotation")

    shift = Parameter(doc="Shift")

    def __init__(self, material, description=''):
        Body.__init__(self, material)

        self.description = description

        self._surfaces.clear()
        self._modules.clear()

        self.rotation = Rotation()
        self.shift = Shift()

    @classmethod
    def from_body(cls, body, description=''):
        """
        Creates a module from a :class:`PenelopeBody`.
        """
        module = cls(body.material, description)
        module.__dict__.update(body.__dict__)
        return module

    def __repr__(self):
        return '<Module(description=%s, material=%s, %i interaction forcing(s), dsmax=%s m, surfaces_count=%i, modules_count=%i, rotation=%s, shift=%s)>' % \
            (self.description, self.material, len(self.interaction_forcings),
             self.maximum_step_length_m, len(self._props['surfaces']),
             len(self._props['modules']), str(self.rotation), str(self.shift))

    def add_module(self, module):
        if module == self:
            raise ValueError, "Cannot add this module to this module."
        self._modules.add(module)

    def pop_module(self, module):
        self._modules.discard(module)

    def clear_modules(self):
        self._modules.clear()

    def get_modules(self):
        return list(self._modules)

    def add_surface(self, surface, pointer):
        if pointer not in [-1, 1]:
            raise ValueError, "Pointer (%s) must be either -1 or 1." % pointer
        if surface in self._surfaces:
            raise ValueError, "Module already contains this surface."
        self._surfaces[surface] = pointer

    def pop_surface(self, surface):
        self._surfaces.pop(surface)

    def clear_surfaces(self):
        self._surfaces.clear()

    def get_surface_pointer(self, surface):
        """
        Returns the surface pointer for the specified surface.
        """
        return self._surfaces[surface]

    def get_surfaces(self):
        return self._surfaces.keys()

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

mapper.register(Module, '{http://pymontecarlo.sf.net/penelope}module',
                ParameterizedAttribute('description', PythonType(str)),
                ParameterizedElementDict('_surfaces', UserType(_Surface), PythonType(int)),
                ParameterizedElementSet('_modules', UserType(Module)),
                ParameterizedElement('rotation', UserType(Rotation)),
                ParameterizedElement('shift', UserType(Shift)))

_title_validator = SimpleValidator(lambda t: len(t) <= (LINE_SIZE - 3))

class PenelopeGeometry(_Geometry):

    title = Parameter([CastValidator(str), _title_validator],
                      "Title of the geometry")

    modules = FrozenParameter(ParameterizedMutableSet)

    def __init__(self, title="Untitled"):
        """
        Creates a new PENELOPE geometry.
        """
        _Geometry.__init__(self)

        self.title = title
        self.modules.clear()

#    @classmethod
#    def _parse_xml_surfaces(cls, element):
#        children = list(element.find('surfaces'))
#        surfaces_lookup = {}
#        for child in children:
#            index = int(child.get('index'))
#            surfaces_lookup[index] = objectxml.from_xml(child)
#
#        return surfaces_lookup
#
#    @classmethod
#    def _parse_xml_modules(cls, element, materials_lookup, surfaces_lookup):
#        children = list(element.find('modules'))
#        modules_dep = {} # module dependencies
#        modules_element = {} # module xml element
#        for child in children:
#            index = int(child.get('index'))
#            modules_element[index] = child
#
#            modules_dep.setdefault(index, [])
#            for grandchild in list(child.find('modules')):
#                modules_dep[index].append(int(grandchild.get('index')))
#
#        modules_lookup = {}
#        for index in modules_dep:
#            for dep_index in topological_sort(modules_dep, index):
#                if dep_index in modules_lookup: continue # skip already loaded module
#
#                element = modules_element[dep_index]
#                modules_lookup[dep_index] = \
#                    objectxml.from_xml(element, materials_lookup,
#                                        surfaces_lookup, modules_lookup)
#
#        return modules_lookup
#
#    @classmethod
#    def __loadxml__(cls, element, *args, **kwargs):
#        materials_lookup = cls._parse_xml_materials(element)
#        surfaces_lookup = cls._parse_xml_surfaces(element)
#        modules_lookup = cls._parse_xml_modules(element, materials_lookup, surfaces_lookup)
#
#        title = str(element.get('title'))
#        obj = cls(title)
#
#        obj._props['modules'] |= set(modules_lookup.values())
#
#        obj.tilt_rad = float(element.get('tilt'))
#        obj.rotation_rad = float(element.get('rotation'))
#
#        return obj
#
#    def _surfaces_to_xml(self):
#        element = Element('surfaces')
#        for surface in self.get_surfaces():
#            element.append(surface.to_xml())
#
#        return element
#
#    def _modules_to_xml(self):
#        element = Element('modules')
#        for module in self.modules:
#            element.append(module.to_xml())
#
#        return element
#
#    def __savexml__(self, element, *args, **kwargs):
#        self._indexify()
#
#        element.set('title', self.title)
#        element.set('tilt', str(self.tilt_rad))
#        element.set('rotation', str(self.rotation_rad))
#
#        element.append(self._materials_to_xml())
#        element.append(self._surfaces_to_xml())
#        element.append(self._modules_to_xml())

    def get_bodies(self):
        return set(self.modules) # copy

    def get_surfaces(self):
        return set(chain(*map(_SURFACES_GETTER, self.modules)))

    def _indexify(self):
        VACUUM._index = 0

        count = 1
        for material in self.get_materials():
            material._index = count
            count += 1

        for i, body in enumerate(self.get_bodies()):
            body._index = i

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
        tilt_rad = self.tilt_rad
        while tilt_rad < 0:
            tilt_rad += 2.0 * math.pi
        extra.rotation.theta_rad = tilt_rad
        extra.rotation.phi_rad = math.pi / 2.0

        # Write module
        extra._index = len(self.modules)
        lines.extend(extra.to_geo())
        lines.append(LINE_SEPARATOR)

        # End of line
        lines.append(LINE_END)

        return lines

