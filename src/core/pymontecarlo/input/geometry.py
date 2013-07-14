"""
================================================================================
:mod:`geometry` -- Sample geometries
================================================================================

.. module:: geometry
   :synopsis: Sample geometries

.. inheritance-diagram:: pymontecarlo.input.geometry

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

__all__ = ['Cuboids2D',
           'GrainBoundaries',
           'ThinGrainBoundaries',
           'Inclusion',
           'MultiLayers',
           'Sphere',
           'Substrate']

# Standard library modules.
from operator import attrgetter
from math import pi
#import itertools
from xml.etree import ElementTree

# Third party modules.
import numpy as np

# Local modules.
from pymontecarlo.input.parameter import \
    (ParameterizedMetaClass, Parameter, UnitParameter, AngleParameter,
     FrozenParameter, ParameterAlias, SimpleValidator, ParameterizedMutableSequence)
from pymontecarlo.input.body import Body, Layer
from pymontecarlo.input.material import VACUUM
from pymontecarlo.input.xmlmapper import mapper, ParameterizedElement, ParameterizedElementSequence, ParameterizedAttribute, PythonType, UserType, _XMLItem

# Globals and constants variables.
_MATERIAL_GETTER = attrgetter('material')
_THICKNESS_GETTER = attrgetter('thickness_m')
POSINF = float('inf')
NEGINF = float('-inf')

class _MaterialParameterAlias(ParameterAlias):

    def __get__(self, obj, objtype=None):
        body = ParameterAlias.__get__(self, obj, objtype)
        return body.material

    def __set__(self, obj, value):
        body = ParameterAlias.__get__(self, obj)
        body.material = value

class _Dimension(object):
    """
    Dimensions in x, y and z of a body.
    """

    def __init__(self,
                 xmin=NEGINF, xmax=POSINF,
                 ymin=NEGINF, ymax=POSINF,
                 zmin=NEGINF, zmax=POSINF):
        self._xmin = xmin
        self._xmax = xmax
        self._ymin = ymin
        self._ymax = ymax
        self._zmin = zmin
        self._zmax = zmax

    def __repr__(self):
        return '<Dimension(xmin=%s, xmax=%s, ymin=%s, ymax=%s, zmin=%s, zmax=%s)>' % \
            (self.xmin_m, self.xmax_m, self.ymin_m, self.ymax_m, self.zmin_m, self.zmax_m)

    def __str__(self):
        return '(xmin=%s, xmax=%s, ymin=%s, ymax=%s, zmin=%s, zmax=%s)' % \
            (self.xmin_m, self.xmax_m, self.ymin_m, self.ymax_m, self.zmin_m, self.zmax_m)

    @property
    def xmin_m(self):
        return self._xmin

    @property
    def xmax_m(self):
        return self._xmax

    @property
    def ymin_m(self):
        return self._ymin

    @property
    def ymax_m(self):
        return self._ymax

    @property
    def zmin_m(self):
        return self._zmin

    @property
    def zmax_m(self):
        return self._zmax

    def to_tuple(self):
        return self.xmin_m, self.xmax_m, \
               self.ymin_m, self.ymax_m, \
               self.zmin_m, self.zmax_m

_tilt_validator = SimpleValidator(lambda t:-pi <= t <= pi,
                                  "Tilt must be between [-pi, pi]")
_rotation_validator = SimpleValidator(lambda r:-pi <= r <= pi,
                                      "Rotation must be between [-pi, pi]")

class _BodyXMLElement(_XMLItem):

    def __init__(self, *args, **kwargs):
        _XMLItem.__init__(self, None, None)

    def _get_object_values(self, obj, manager):
        # Bodies
        bodies_lookup = {}
        for i, body in enumerate(obj.get_bodies()):
            bodies_lookup[body] = i

        # Materials
        materials_lookup = {}
        for i, material in enumerate(obj.get_materials()):
            materials_lookup[material] = i + 1

        return bodies_lookup, materials_lookup
    
    def _update_element(self, element, values, manager):
        bodies_lookup, materials_lookup = values
        
        # Materials
        subelement = ElementTree.Element('materials')

        for material, index in materials_lookup.iteritems():
            subsubelement = manager.to_xml(material)
            subsubelement.set('index', str(index))
            subelement.append(subsubelement)

        element.append(subelement)

        # Bodies
        subelement = ElementTree.Element('bodies')
        
        for body, index in bodies_lookup.iteritems():
            subsubelement = manager.to_xml(body)
            subsubelement.set('index', str(index))
            
            subsubelement.remove(subsubelement.find('material')) # remove material element

            material = body.__dict__['material'].get_list()
            subsubelement.set('material', str(materials_lookup[body.material]))
            
            subelement.append(subsubelement)
            
        element.append(subelement)

    def _update_element_bodies(self, obj, element, bodies_lookup):
        raise NotImplementedError

    def dump(self, obj, element, manager):
        values = self._get_object_values(obj, manager)
        self._update_element(element, values, manager)
        self._update_element_bodies(obj, element, values[0])

    def _extract_values(self, element, manager):
        # Materials
        materials_lookup = {0: VACUUM}
        for subelement in element.find('materials'):
            index = int(subelement.get('index'))
            material = manager.from_xml(subelement)
            materials_lookup[index] = material

        # Bodies
        bodies_lookup = {}
        for subelement in element.find('bodies'):
            index = int(subelement.get('index'))
            body = manager.from_xml(subelement)

            material_index = int(subelement.get('material'))
            body.material = materials_lookup[material_index]

            bodies_lookup[index] = body

        return bodies_lookup

    def _set_object_bodies(self, obj, element, bodies_lookup):
        raise NotImplementedError

    def load(self, obj, element, manager):
        bodies_lookup = self._extract_values(element, manager)
        self._set_object_bodies(obj, element, bodies_lookup)

class _Geometry(object):
    """
    Base class for all geometry representations.
    
    A geometry is composed of bodies (:class:`Body`).
    Bodies may have some specific properties (e.g. thickness), but they must
    all be defined with a material.
    A geometry can only refer to a body once, but bodies can be defined using
    the same material.
    """

    __metaclass__ = ParameterizedMetaClass

    tilt = AngleParameter(_tilt_validator,
                          "Specimen tilt in radians along the x-axis")
    rotation = AngleParameter(_rotation_validator,
                              "Specimen rotation in radians along the z-axis")

    def __init__(self, tilt_rad=0, rotation_rad=0):
        self.tilt_rad = tilt_rad
        self.rotation_rad = rotation_rad

    def get_materials(self):
        """
        Returns a :class:`set` of all materials inside this geometry.
        Since a :class:`set` is returned, even if the same material is used 
        more than once, it will only appear once.
        :obj:`VACUUM` is not considered as a material, so this object will
        not appear in this list.
        """
        materials = map(_MATERIAL_GETTER, self.get_bodies())
        materials = np.array(materials).flatten()
        materials = set(materials)
        materials.discard(VACUUM)
        return materials

    def get_bodies(self):
        """
        Returns a :class:`set` of all bodies inside this geometry. 
        The bodies are returned in no particular order.
        """
        raise NotImplementedError

    def get_dimensions(self, body):
        """
        Returns a class:`Dimension <._Dimension>` corresponding to the 
        dimensions of the body inside the geometry.
        All dimensions are in meters.
        
        :arg body: body to get the dimensions for
        """
        raise NotImplementedError

mapper.register(_Geometry, 'geometry',
                ParameterizedAttribute('tilt_rad', PythonType(float), 'tilt'),
                ParameterizedAttribute('rotation_rad', PythonType(float), 'rotation'))

class Substrate(_Geometry):

    body = Parameter(doc="Body of this substrate")
    material = _MaterialParameterAlias(body, doc="Material of this substrate")

    def __init__(self, material):
        _Geometry.__init__(self)
        self.body = Body(material)

    def __repr__(self):
        return '<Substrate(material=%s)>' % str(self.material)

    def get_bodies(self):
        bodies = self.__dict__['body'].get_list()
        return set(bodies)

    def get_dimensions(self, body):
        if body is self.body:
            return _Dimension(zmax=0.0)
        else:
            raise ValueError, "Unknown body: %s" % body

mapper.register(Substrate, '{http://pymontecarlo.sf.net}substrate',
                ParameterizedElement('body', UserType(Body), 'substrate'))

_diameter_validator = SimpleValidator(lambda d: d > 0.0,
                                      "Diameter must be greater than 0.0")

class Inclusion(_Geometry):

    substrate_body = Parameter(doc="Body of the substrate")
    substrate_material = _MaterialParameterAlias(substrate_body,
                                                doc="Material of the substrate")

    inclusion_body = Parameter(doc="Body of the inclusion")
    inclusion_material = _MaterialParameterAlias(inclusion_body,
                                                doc="Material of the inclusion")

    inclusion_diameter = UnitParameter("m", _diameter_validator,
                                       "Inclusion diameter (in meters)")

    def __init__(self, substrate_material, inclusion_material, inclusion_diameter_m):
        _Geometry.__init__(self)

        self.substrate_body = Body(substrate_material)
        self.inclusion_body = Body(inclusion_material)
        self.inclusion_diameter_m = inclusion_diameter_m

    def __repr__(self):
        return '<Inclusion(substrate_material=%s, inclusion_material=%s, inclusion_diameter=%s m)>' % \
            (str(self.substrate_material), str(self.inclusion_material), self.inclusion_diameter_m)

    def get_bodies(self):
        return set([self.substrate_body, self.inclusion_body])

    def get_dimensions(self, body):
        if body is self.substrate_body:
            return _Dimension(zmax=0.0)
        elif body is self.inclusion_body:
            radius = self.inclusion_diameter_m / 2.0
            return _Dimension(-radius, radius, -radius, radius, -radius, 0.0)
        else:
            raise ValueError, "Unknown body: %s" % body

mapper.register(Inclusion, '{http://pymontecarlo.sf.net}inclusion',
                ParameterizedElement('substrate_body', UserType(Body), 'substrate'),
                ParameterizedElement('inclusion_body', UserType(Body), 'inclusion'),
                ParameterizedAttribute('inclusion_diameter_m', PythonType(float), 'diameter'))

class _Layers(ParameterizedMutableSequence):
    pass

class _LayeredGeometry(_Geometry):

    layers = FrozenParameter(_Layers, "Layers from top to bottom (multi-layers) or from left to right (grain boundaries).")

    def __init__(self, layers=None):
        _Geometry.__init__(self)

        if layers is not None:
            self.layers.extend(layers)

    def add_layer(self, material, thickness):
        """
        Adds a layer to the geometry.
        The layer is added after the previous layers.

        This method is equivalent to::

            geometry.layers.append(Layer(material, thickness))

        :arg material: material of the layer
        :type material: :class:`Material`

        :arg thickness: thickness of the layer in meters
        """
        layer = Layer(material, thickness)
        self.layers.append(layer)
        return layer

    def clear(self):
        """
        Removes all layers.
        """
        del self.layers[:]

    def get_bodies(self):
        return list(self.layers) # copy

mapper.register(_LayeredGeometry, '{http://pymontecarlo.sf.net}layeredGeometry',
                ParameterizedElementSequence('layers', UserType(Layer)))

class MultiLayers(_LayeredGeometry):

    substrate_body = Parameter(doc="Body of the substrate")
    substrate_material = \
        _MaterialParameterAlias(substrate_body, doc="Material of the substrate")

    def __init__(self, substrate_material=None, layers=None):
        """
        Creates a multi-layers geometry.
        The layers are assumed to be in the x-y plane (normal parallel to z).
        The first layer starts at ``z = 0`` and extends towards the negative z
        axis.

        :arg substrate_material: material of the substrate.
            If ``None``, the geometry does not have a substrate, only layers
        :arg layers: :class:`list` of :class:`.Layer`
        """
        _LayeredGeometry.__init__(self, layers)

        if substrate_material is None:
            substrate_material = VACUUM
        self.substrate_body = Body(substrate_material)

    def __repr__(self):
        if self.has_substrate():
            return '<MultiLayers(substrate_material=%s, layers_count=%i)>' % \
                (str(self.substrate_material), len(self.layers))
        else:
            return '<MultiLayers(No substrate, layers_count=%i)>' % len(self.layers)

    def has_substrate(self):
        """
        Returns ``True`` if a substrate material has been defined.
        """
        return self.substrate_body.material is not VACUUM

    def get_bodies(self):
        bodies = _LayeredGeometry.get_bodies(self)

        if self.has_substrate():
            bodies.append(self.substrate_body)

        return bodies

    def get_dimensions(self, body):
        if body is self.substrate_body and body is not None:
            zmax = -sum(map(_THICKNESS_GETTER, self.layers))
            return _Dimension(zmax=zmax)
        elif body in self.layers:
            indextop = self.layers.index(body)
            indexbottom = len(self.layers) - self.layers[::-1].index(body)
            zmax = -sum(map(_THICKNESS_GETTER, self.layers[:indextop]))
            zmin = -sum(map(_THICKNESS_GETTER, self.layers[:indexbottom]))
            return _Dimension(zmin=zmin, zmax=zmax)
        else:
            raise ValueError, "Unknown body: %s" % body

mapper.register(MultiLayers, '{http://pymontecarlo.sf.net}multiLayers',
                ParameterizedElement('substrate_body', UserType(Body), 'substrate'))

class GrainBoundaries(_LayeredGeometry):

    left_body = Parameter(doc="Body of left side")
    left_material = _MaterialParameterAlias(left_body, doc="Material of left side")

    right_body = Parameter(doc="Body of right side")
    right_material = _MaterialParameterAlias(right_body, doc="Material of right side")

    def __init__(self, left_material, right_material, layers=None):
        """
        Creates a grain boundaries geometry.
        It consists of 0 or many layers in the y-z plane (normal parallel to x)
        simulating interfaces between different materials.
        If no layer is defined, the geometry is a couple.

        :arg left_material: material on the left side
        :arg right_material: material on the right side
        :arg layers: :class:`list` of :class:`.Layer`
        """
        _LayeredGeometry.__init__(self, layers)

        self.left_body = Body(left_material)
        self.right_body = Body(right_material)

    def __repr__(self):
        return '<GrainBoundaries(left_material=%s, right_materials=%s, layers_count=%i)>' % \
            (str(self.left_material), str(self.right_material), len(self.layers))

    def get_bodies(self):
        bodies = _LayeredGeometry.get_bodies(self)

        bodies.append(self.left_body)
        bodies.append(self.right_body)

        return bodies

    def get_dimensions(self, body):
        thicknesses = map(_THICKNESS_GETTER, self.layers)

        positions = []
        if thicknesses: # simple couple
            middle = sum(thicknesses) / 2.0
            for i in range(len(thicknesses)):
                positions.append(sum(thicknesses[:i]) - middle)
            positions.append(positions[-1] + thicknesses[-1])
        else:
            positions.append(0.0)

        if body is self.left_body:
            return _Dimension(xmax=positions[0], zmax=0)
        elif body is self.right_body:
            return _Dimension(xmin=positions[-1], zmax=0)
        elif body in self.layers:
            indexleft = self.layers.index(body)
            indexright = len(self.layers) - self.layers[::-1].index(body)
            return _Dimension(xmin=positions[indexleft],
                              xmax=positions[indexright],
                              zmax=0)
        else:
            raise ValueError, "Unknown body: %s" % body

mapper.register(GrainBoundaries, '{http://pymontecarlo.sf.net}grainBoundaries',
                ParameterizedElement('left_body', UserType(Body), 'left'),
                ParameterizedElement('right_body', UserType(Body), 'right'))

_thickness_validator = SimpleValidator(lambda t: t> 0,
                                       'Thickness must be greater than 0')

class ThinGrainBoundaries(GrainBoundaries):
    
    thickness = UnitParameter("m", _thickness_validator,
                              "Thickness of geometry (in meters)")
    
    def __init__(self, left_material, right_material, thickness_m, layers=None):
        """
        Creates a thin film consisting of a grain boundaries geometry.
        It consists of 0 or many layers in the y-z plane (normal parallel to x)
        simulating interfaces between different materials.
        If no layer is defined, the geometry is a couple.

        :arg left_material: material on the left side
        :arg right_material: material on the right side
        :arg thickness_m: thickness of the geometry (in meters)
        :arg layers: :class:`list` of :class:`.Layer`
        """
        GrainBoundaries.__init__(self, left_material, right_material, layers)
        self.thickness_m = thickness_m

    def __repr__(self):
        return '<ThinGrainBoundaries(left_material=%s, right_materials=%s, layers_count=%i, thickness=%s m)>' % \
            (str(self.left_material), str(self.right_material),
             len(self.layers), self.thickness_m)

    def get_dimensions(self, body):
        dim = GrainBoundaries.get_dimensions(self, body)
        dim._zmin = -self.thickness_m
        return dim

mapper.register(ThinGrainBoundaries, '{http://pymontecarlo.sf.net}thinGrainBoundaries',
                ParameterizedAttribute('thickness_m', PythonType(float), 'thickness'))

class Sphere(_Geometry):

    body = Parameter(doc="Body of this sphere")
    material = _MaterialParameterAlias(body, doc="Material of this sphere")

    diameter = UnitParameter("m", _diameter_validator,
                             "Diameter of this sphere (in meters)")

    def __init__(self, material, diameter_m):
        """
        Creates a geometry consisting of a sphere.
        The sphere is entirely located below the ``z=0`` plane.

        :arg material: material
        :arg diameter_m: diameter (in meters)
        """
        _Geometry.__init__(self)

        self.body = Body(material)
        self.diameter_m = diameter_m

    def __repr__(self):
        return '<Sphere(material=%s, diameter=%s m)>' % \
                    (str(self.material), self.diameter_m)

    def get_bodies(self):
        return set([self.body])

    def get_dimensions(self, body):
        if body is self.body:
            d = self.diameter_m
            r = d / 2.0
            return _Dimension(xmin=-r, xmax=r,
                              ymin=-r, ymax=r,
                              zmin=-d, zmax=0.0)
        else:
            raise ValueError, "Unknown body: %s" % body

mapper.register(Sphere, '{http://pymontecarlo.sf.net}sphere',
                ParameterizedElement('body', UserType(Body), 'body'),
                ParameterizedAttribute('diameter_m', PythonType(float), 'diameter'))
#
#class Cuboids2D(_Geometry):
#
#    class __Cuboids2DBody(object):
#        def __init__(self, bodies):
#            self._bodies = bodies
#
#        def __getitem__(self, index):
#            if index not in self._bodies:
#                raise IndexError, 'No body at index (%i, %i)' % index
#            return self._bodies[index]
#
#    class __Cuboids2DMaterial(object):
#        def __init__(self, bodies):
#            self._bodies = bodies
#
#        def __getitem__(self, index):
#            if index not in self._bodies:
#                raise IndexError, 'No material at index (%i, %i)' % index
#            return self._bodies[index].material
#
#        def __setitem__(self, index, material):
#            if index not in self._bodies:
#                raise IndexError, 'No material at index (%i, %i)' % index
#            self._bodies[index].material = material
#
#    def __init__(self, nx, ny, xsize_m, ysize_m):
#        """
#        Creates a geometry made of *nx* by *ny* adjacent cuboids with
#        infinite depth.
#        Each cuboid was a size of *xsize* by *ysize*.
#        The number of cuboids in x and y-direction must be odd, so that the
#        cuboid (nx/2+1, ny/2+1) is located at the center.
#
#        The position (0, 0) is given to the center cuboid.
#        Cuboids on the upper-left quadrant have positive indexes whereas
#        cuboids on the bottom-right quadrant have negative indexes.
#
#        The material of each cuboid can be access as follows::
#
#            >>> print geometry.material[0,0] # center cuboid
#            >>> print geometry.material[1,0] # cuboid to the left of the center cuboid
#            >>> print geometry.material[0,1] # cuboid above the center cuboid
#            >>> print geometry.material[1,-2] # cuboid one up and 2 to the right of the center cuboid
#
#        .. note::
#
#           When the geometry is created, all cuboids have no material (i.e. vacuum).
#
#        :arg nx: number of cuboids in x-direction (odd number)
#        :type nx: :class:`int`
#
#        :arg ny: number of cuboids in y-direction (odd number)
#        :type ny: :class:`int`
#
#        :arg xsize_m: size of a cuboid in x-direction (in meters)
#        :type xsize_m: :class:`float`
#
#        :arg ysize_m: size of a cuboid in y-direction (in meters)
#        :type ysize_m: :class:`float`
#        """
#        _Geometry.__init__(self)
#
#        if nx < 1 and nx % 2 == 1:
#            raise ValueError, 'nx must be greater or equal to 1 and an odd number'
#        self._props['nx'] = nx
#
#        if ny < 1 and ny % 2 == 1:
#            raise ValueError, 'ny must be greater or equal to 1 and an odd number'
#        self._props['ny'] = ny
#
#        self.xsize_m = xsize_m
#        self.ysize_m = ysize_m
#
#        # Create empty bodies
#        self._bodies = {}
#
#        for position in itertools.product(range(-(nx / 2), nx / 2 + 1),
#                                          range(-(ny / 2), ny / 2 + 1)):
#            body = Body(VACUUM)
#            self._bodies[position] = body
#
#        self._body = self.__Cuboids2DBody(self._bodies)
#        self._material = self.__Cuboids2DMaterial(self._bodies)
#
#    @classmethod
#    def __loadxml__(cls, element, *args, **kwargs):
#        bodies_lookup, tilt_rad, rotation_rad = _Geometry._parse_xml(element)
#
#        nx = int(element.get('nx'))
#        ny = int(element.get('ny'))
#        xsize_m = float(element.get('xsize'))
#        ysize_m = float(element.get('ysize'))
#
#        obj = cls(nx, ny, xsize_m, ysize_m)
#        obj.tilt_rad = tilt_rad
#        obj.rotation_rad = rotation_rad
#
#        children = list(element.find('positions'))
#        for child in children:
#            index = int(child.get('index'))
#            position = int(child.get('x')), int(child.get('y'))
#            body = bodies_lookup[index]
#
#            obj._bodies[position] = body
#
#        return obj
#
#    def __savexml__(self, element, *args, **kwargs):
#        _Geometry.__savexml__(self, element, *args, **kwargs)
#
#        element.set('nx', str(self.nx))
#        element.set('ny', str(self.ny))
#        element.set('xsize', str(self.xsize_m))
#        element.set('ysize', str(self.ysize_m))
#
#        child = Element('positions')
#        for position, body in self._bodies.iteritems():
#            grandchild = Element('position')
#            grandchild.set('index', str(body._index))
#            grandchild.set('x', str(position[0]))
#            grandchild.set('y', str(position[1]))
#            child.append(grandchild)
#        element.append(child)
#
#    @property
#    def nx(self):
#        """
#        Number of cuboids in x-direction (read-only).
#        """
#        return self._props['nx']
#
#    @property
#    def ny(self):
#        """
#        Number of cuboids in y-direction (read-only).
#        """
#        return self._props['ny']
#
#    @property
#    def xsize_m(self):
#        """
#        Size of a cuboids in x-direction (in meters).
#        """
#        return self._props['xsize']
#
#    @xsize_m.setter
#    def xsize_m(self, size):
#        if size <= 0.0:
#            raise ValueError, 'size must be greater than 0'
#        self._props['xsize'] = size
#
#    @property
#    def ysize_m(self):
#        """
#        Size of a cuboids in y-direction (in meters).
#        """
#        return self._props['ysize']
#
#    @ysize_m.setter
#    def ysize_m(self, size):
#        if size <= 0.0:
#            raise ValueError, 'size must be greater than 0'
#        self._props['ysize'] = size
#
#    @property
#    def body(self):
#        return self._body
#
#    @property
#    def material(self):
#        return self._material
#
#    def get_bodies(self):
#        return set(self._bodies.values())
#
#    def get_dimensions(self, body):
#        reverse_lookup = dict(zip(self._bodies.values(), self._bodies.keys()))
#
#        try:
#            x, y = reverse_lookup[body]
#        except IndexError:
#            raise ValueError, "Unknown body: %s" % body
#
#        xsize = self.xsize_m
#        ysize = self.ysize_m
#
#        xmin = (x * xsize) - xsize / 2
#        xmax = (x * xsize) + xsize / 2
#        ymin = (y * ysize) - ysize / 2
#        ymax = (y * ysize) + ysize / 2
#
#        return _Dimension(xmin, xmax, ymin, ymax, zmax=0.0)
#
#XMLIO.register('{http://pymontecarlo.sf.net}cuboids2d', Cuboids2D)
