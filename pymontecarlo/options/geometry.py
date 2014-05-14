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

__all__ = ['VerticalLayers',
           'Inclusion',
           'HorizontalLayers',
           'Sphere',
           'Substrate']

# Standard library modules.
from operator import attrgetter
from math import pi

# Third party modules.
import numpy as np

# Local modules.
from pymontecarlo.util.parameter import \
    (ParameterizedMetaclass, Parameter, AngleParameter, UnitParameter,
     ParameterizedMutableSequence, range_validator)
from pymontecarlo.options.material import Material, VACUUM

# Globals and constants variables.
_MATERIAL_GETTER = attrgetter('material')
_THICKNESS_GETTER = attrgetter('thickness_m')

class _Body(object, metaclass=ParameterizedMetaclass):

    material = Parameter(Material, doc="Material of this body")

    def __init__(self, geometry, material):
        """
        Body of a geometry.

        :arg geometry: geometry of this body
        :type geometry: :class:`.Geometry`

        :arg material: material of this body
        :type material: :class:`Material`
        """
        self._geometry = geometry
        self.material = material

    def __repr__(self):
        return '<Body(material=%s)>' % str(self.material)

    @property
    def geometry(self):
        """
        Geometry containing this body.
        """
        return self._geometry

    @property
    def xmin_m(self):
        return float('-inf')

    @property
    def xmax_m(self):
        return float('inf')

    @property
    def ymin_m(self):
        return float('-inf')

    @property
    def ymax_m(self):
        return float('inf')

    @property
    def zmin_m(self):
        return float('-inf')

    @property
    def zmax_m(self):
        return float('inf')

class _Geometry(object, metaclass=ParameterizedMetaclass):
    """
    Base class for all geometry representations.

    A geometry is composed of bodies (:class:`Body`).
    Bodies may have some specific properties (e.g. thickness), but they must
    all be defined with a material.
    A geometry can only refer to a body once, but bodies can be defined using
    the same material.
    """

    tilt = AngleParameter(range_validator(-pi, pi),
                          doc="Specimen tilt in radians along the x-axis")
    rotation = AngleParameter(range_validator(-pi, pi),
                              doc="Specimen rotation in radians along the z-axis")

    def __init__(self, tilt_rad=0.0, rotation_rad=0.0):
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
        materials = list(map(_MATERIAL_GETTER, self.get_bodies()))
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

class _SubstrateBody(_Body):

    @property
    def zmax_m(self):
        return 0.0

class Substrate(_Geometry):

    body = Parameter(_SubstrateBody, doc="Body of this substrate")

    def __init__(self, material, tilt_rad=0.0, rotation_rad=0.0):
        _Geometry.__init__(self, tilt_rad, rotation_rad)
        self.body = _SubstrateBody(self, material)

        self.__parameters__['body'].freeze(self)

    def __repr__(self):
        return '<Substrate(material=%s)>' % str(self.body.material)

    def get_bodies(self):
        return set(np.array(self.body, ndmin=1))

class _InclusionBody(_Body):

    diameter = UnitParameter("m", range_validator(0.0, inclusive=False),
                             doc="Inclusion diameter")

    def __init__(self, geometry, material, diameter_m):
        _Body.__init__(self, geometry, material)
        self.diameter_m = diameter_m

    @property
    def xmin_m(self):
        return -self.diameter_m / 2.0

    @property
    def xmax_m(self):
        return self.diameter_m / 2.0

    @property
    def ymin_m(self):
        return -self.diameter_m / 2.0

    @property
    def ymax_m(self):
        return self.diameter_m / 2.0

    @property
    def zmin_m(self):
        return -self.diameter_m / 2.0

    @property
    def zmax_m(self):
        return 0.0

class Inclusion(_Geometry):

    substrate = Parameter(_SubstrateBody, doc="Body of the substrate")
    inclusion = Parameter(_InclusionBody, doc="Body of the inclusion")

    def __init__(self, substrate_material,
                 inclusion_material, inclusion_diameter_m,
                 tilt_rad=0.0, rotation_rad=0.0):
        _Geometry.__init__(self, tilt_rad, rotation_rad)

        self.substrate = _SubstrateBody(self, substrate_material)
        self.inclusion = _InclusionBody(self, inclusion_material, inclusion_diameter_m)

        self.__parameters__['substrate'].freeze(self)
        self.__parameters__['inclusion'].freeze(self)

    def __repr__(self):
        return '<Inclusion(substrate_material=%s, inclusion_material=%s, inclusion_diameter=%s m)>' % \
            (str(self.substrate.material), str(self.inclusion.material), self.inclusion.diameter_m)

    def get_bodies(self):
        bodies = set()
        bodies.update(np.array(self.substrate, ndmin=1))
        bodies.update(np.array(self.inclusion, ndmin=1))
        return bodies

class _Layer(_Body):

    thickness = UnitParameter("m", range_validator(0.0, inclusive=False),
                              doc="Thickness of this layer")

    def __init__(self, geometry, material, thickness_m):
        """
        Layer of a geometry.

        :arg material: material of the layer
        :type material: :class:`Material`

        :arg thickness_m: thickness of the layer in meters
        """
        _Body.__init__(self, geometry, material)

        self.thickness_m = thickness_m

    def __repr__(self):
        return '<Layer(material=%s, thickness=%s m)>' % \
                    (str(self.material), self.thickness_m)

class _Layers(ParameterizedMutableSequence):
    pass

class _HorizontalLayer(_Layer):

    @property
    def zmin_m(self):
        layers = np.array(self.geometry.layers, ndmin=1)
        indexbottom = len(layers) - np.where(layers[::-1] == self)[0][0]
        return -sum(map(_THICKNESS_GETTER, layers[:indexbottom]))

    @property
    def zmax_m(self):
        layers = np.array(self.geometry.layers, ndmin=1)
        indextop = np.where(layers == self)[0][0]
        return -sum(map(_THICKNESS_GETTER, layers[:indextop]))

class _HorizontalSubstrateBody(_SubstrateBody):

    @property
    def zmax_m(self):
        layers = np.array(self.geometry.layers, ndmin=1)
        return -sum(map(_THICKNESS_GETTER, layers))

class HorizontalLayers(_Geometry):

    substrate = Parameter(_HorizontalSubstrateBody, required=False,
                          doc="Body of the substrate")
    layers = Parameter(_Layers, required=False,
                       doc="Layers from top to bottom")

    def __init__(self, substrate_material=None, layers=None,
                 tilt_rad=0.0, rotation_rad=0.0):
        """
        Creates a multi-layers geometry.
        The layers are assumed to be in the x-y plane (normal parallel to z).
        The first layer starts at ``z = 0`` and extends towards the negative z
        axis.

        :arg substrate_material: material of the substrate.
            If ``None``, the geometry does not have a substrate, only layers
        :arg layers: :class:`list` of :class:`.Layer`
        """
        _Geometry.__init__(self, tilt_rad, rotation_rad)

        if not substrate_material:
            substrate_material = VACUUM
        self.substrate = _HorizontalSubstrateBody(self, substrate_material)

        # Hack because numpy converts MutableSequence to array
        layers = np.ndarray((1,), np.dtype(_Layers))
        layers[0] = _Layers(_HorizontalLayer)
        self.__dict__['layers'] = layers
        self.layers.extend(layers or [])

        self.__parameters__['substrate'].freeze(self)
        self.__parameters__['layers'].freeze(self)

    def __repr__(self):
        layers = np.array(self.layers, ndmin=1)
        if self.has_substrate():
            return '<MultiLayers(substrate_material=%s, layers_count=%i)>' % \
                (str(self.substrate.material), len(layers))
        else:
            return '<MultiLayers(No substrate, layers_count=%i)>' % len(layers)

    def has_substrate(self):
        """
        Returns ``True`` if a substrate material has been defined.
        """
        return self.substrate.material is not VACUUM

    def add_layer(self, material, thickness_m):
        """
        Adds a layer to the geometry.
        The layer is added after the previous layers.

        :arg material: material of the layer
        :type material: :class:`Material`

        :arg thickness: thickness of the layer in meters
        """
        layer = _HorizontalLayer(self, material, thickness_m)
        self.layers.append(layer)
        return layer

    def get_bodies(self):
        bodies = set()
        bodies.update(np.array(self.layers, ndmin=1))

        if self.has_substrate():
            bodies.add(self.substrate)

        return bodies

class _VerticalBody(_Body):

    def _calculate_positions(self):
        layers = np.array(self.geometry.layers, ndmin=1)
        thicknesses = list(map(_THICKNESS_GETTER, layers))

        positions = []
        if thicknesses: # simple couple
            middle = sum(thicknesses) / 2.0
            for i in range(len(thicknesses)):
                positions.append(sum(thicknesses[:i]) - middle)
            positions.append(positions[-1] + thicknesses[-1])
        else:
            positions.append(0.0)

        return positions

    @property
    def zmin_m(self):
        return -self.geometry.depth_m

class _VerticalLayer(_Layer, _VerticalBody):

    def __init__(self, geometry, material, thickness_m):
        _Layer.__init__(self, geometry, material, thickness_m)
        _VerticalBody.__init__(self, geometry, material)

    @property
    def xmin_m(self):
        layers = np.array(self.geometry.layers, ndmin=1)
        positions = self._calculate_positions()
        indexleft = np.where(layers == self)[0][0]
        return positions[indexleft]

    @property
    def xmax_m(self):
        layers = np.array(self.geometry.layers, ndmin=1)
        positions = self._calculate_positions()
        indexright = len(layers) - np.where(layers[::-1] == self)[0][0]
        return positions[indexright]

    @property
    def zmax_m(self):
        return 0.0

class _VerticalLeftSubstrateBody(_SubstrateBody, _VerticalBody):

    def __init__(self, geometry, material):
        _SubstrateBody.__init__(self, geometry, material)
        _VerticalBody.__init__(self, geometry, material)

    @property
    def xmax_m(self):
        positions = self._calculate_positions()
        return positions[0]

class _VerticalRightSubstrateBody(_SubstrateBody, _VerticalBody):

    def __init__(self, geometry, material):
        _SubstrateBody.__init__(self, geometry, material)
        _VerticalBody.__init__(self, geometry, material)

    @property
    def xmin_m(self):
        positions = self._calculate_positions()
        return positions[-1]

class VerticalLayers(_Geometry):

    left_substrate = Parameter(_VerticalLeftSubstrateBody,
                               doc="Body of left side")
    right_substrate = Parameter(_VerticalRightSubstrateBody,
                                doc="Body of right side")
    layers = Parameter(_Layers, required=False,
                       doc="Layers from left to right")
    depth = UnitParameter("m", range_validator(0.0, inclusive=False),
                          doc="Depth (z thickness)")

    def __init__(self, left_material, right_material, layers=None,
                 depth_m=float('inf'), tilt_rad=0.0, rotation_rad=0.0):
        """
        Creates a grain boundaries geometry.
        It consists of 0 or many layers in the y-z plane (normal parallel to x)
        simulating interfaces between different materials.
        If no layer is defined, the geometry is a couple.

        :arg left_material: material on the left side
        :arg right_material: material on the right side
        :arg layers: :class:`list` of :class:`.Layer`
        """
        _Geometry.__init__(self, tilt_rad, rotation_rad)

        self.left_substrate = _VerticalLeftSubstrateBody(self, left_material)
        self.right_substrate = _VerticalRightSubstrateBody(self, right_material)

        # Hack because numpy converts MutableSequence to array
        layers = np.ndarray((1,), np.dtype(_Layers))
        layers[0] = _Layers(_VerticalLayer)
        self.__dict__['layers'] = layers
        self.layers.extend(layers or [])

        self.depth_m = depth_m

        self.__parameters__['left_substrate'].freeze(self)
        self.__parameters__['layers'].freeze(self)
        self.__parameters__['right_substrate'].freeze(self)

    def __repr__(self):
        layers = np.array(self.layers, ndmin=1)
        return '<GrainBoundaries(left_material=%s, right_materials=%s, layers_count=%i)>' % \
            (str(self.left_substrate.material),
             str(self.right_substrate.material),
             len(layers))

    def add_layer(self, material, thickness):
        """
        Adds a layer to the geometry.
        The layer is added after the previous layers.

        :arg material: material of the layer
        :type material: :class:`Material`

        :arg thickness: thickness of the layer in meters
        """
        layer = _VerticalLayer(self, material, thickness)
        self.layers.append(layer)
        return layer

    def get_bodies(self):
        bodies = set()
        bodies.update(np.array(self.layers, ndmin=1))
        bodies.add(self.left_substrate)
        bodies.add(self.right_substrate)
        return bodies

class _SphereBody(_Body):

    diameter = UnitParameter("m", range_validator(0.0, inclusive=False),
                             doc="Diameter")

    def __init__(self, geometry, material, diameter_m):
        _Body.__init__(self, geometry, material)
        self.diameter_m = diameter_m

    @property
    def xmin_m(self):
        return -self.diameter_m / 2.0

    @property
    def xmax_m(self):
        return self.diameter_m / 2.0

    @property
    def ymin_m(self):
        return -self.diameter_m / 2.0

    @property
    def ymax_m(self):
        return self.diameter_m / 2.0

    @property
    def zmin_m(self):
        return -self.diameter_m

    @property
    def zmax_m(self):
        return 0.0

class Sphere(_Geometry):

    body = Parameter(_SphereBody, doc="Body of this sphere")

    def __init__(self, material, diameter_m, tilt_rad=0.0, rotation_rad=0.0):
        """
        Creates a geometry consisting of a sphere.
        The sphere is entirely located below the ``z=0`` plane.

        :arg material: material
        :arg diameter_m: diameter (in meters)
        """
        _Geometry.__init__(self, tilt_rad, rotation_rad)

        self.body = _SphereBody(self, material, diameter_m)

        self.__parameters__['body'].freeze(self)

    def __repr__(self):
        return '<Sphere(material=%s, diameter=%s m)>' % \
                    (str(self.body.material), self.diameter_m)

    def get_bodies(self):
        return set(np.array(self.body, ndmin=1))


# # #
# # # class Cuboids2D(_Geometry):
# # #
# # #    class __Cuboids2DBody(object):
# # #        def __init__(self, bodies):
# # #            self._bodies = bodies
# # #
# # #        def __getitem__(self, index):
# # #            if index not in self._bodies:
# # #                raise IndexError, 'No body at index (%i, %i)' % index
# # #            return self._bodies[index]
# # #
# # #    class __Cuboids2DMaterial(object):
# # #        def __init__(self, bodies):
# # #            self._bodies = bodies
# # #
# # #        def __getitem__(self, index):
# # #            if index not in self._bodies:
# # #                raise IndexError, 'No material at index (%i, %i)' % index
# # #            return self._bodies[index].material
# # #
# # #        def __setitem__(self, index, material):
# # #            if index not in self._bodies:
# # #                raise IndexError, 'No material at index (%i, %i)' % index
# # #            self._bodies[index].material = material
# # #
# # #    def __init__(self, nx, ny, xsize_m, ysize_m):
# # #        """
# # #        Creates a geometry made of *nx* by *ny* adjacent cuboids with
# # #        infinite depth.
# # #        Each cuboid was a size of *xsize* by *ysize*.
# # #        The number of cuboids in x and y-direction must be odd, so that the
# # #        cuboid (nx/2+1, ny/2+1) is located at the center.
# # #
# # #        The position (0, 0) is given to the center cuboid.
# # #        Cuboids on the upper-left quadrant have positive indexes whereas
# # #        cuboids on the bottom-right quadrant have negative indexes.
# # #
# # #        The material of each cuboid can be access as follows::
# # #
# # #            >>> print geometry.material[0,0] # center cuboid
# # #            >>> print geometry.material[1,0] # cuboid to the left of the center cuboid
# # #            >>> print geometry.material[0,1] # cuboid above the center cuboid
# # #            >>> print geometry.material[1,-2] # cuboid one up and 2 to the right of the center cuboid
# # #
# # #        .. note::
# # #
# # #           When the geometry is created, all cuboids have no material (i.e. vacuum).
# # #
# # #        :arg nx: number of cuboids in x-direction (odd number)
# # #        :type nx: :class:`int`
# # #
# # #        :arg ny: number of cuboids in y-direction (odd number)
# # #        :type ny: :class:`int`
# # #
# # #        :arg xsize_m: size of a cuboid in x-direction (in meters)
# # #        :type xsize_m: :class:`float`
# # #
# # #        :arg ysize_m: size of a cuboid in y-direction (in meters)
# # #        :type ysize_m: :class:`float`
# # #        """
# # #        _Geometry.__init__(self)
# # #
# # #        if nx < 1 and nx % 2 == 1:
# # #            raise ValueError, 'nx must be greater or equal to 1 and an odd number'
# # #        self._props['nx'] = nx
# # #
# # #        if ny < 1 and ny % 2 == 1:
# # #            raise ValueError, 'ny must be greater or equal to 1 and an odd number'
# # #        self._props['ny'] = ny
# # #
# # #        self.xsize_m = xsize_m
# # #        self.ysize_m = ysize_m
# # #
# # #        # Create empty bodies
# # #        self._bodies = {}
# # #
# # #        for position in itertools.product(range(-(nx / 2), nx / 2 + 1),
# # #                                          range(-(ny / 2), ny / 2 + 1)):
# # #            body = Body(VACUUM)
# # #            self._bodies[position] = body
# # #
# # #        self._body = self.__Cuboids2DBody(self._bodies)
# # #        self._material = self.__Cuboids2DMaterial(self._bodies)
# # #
# # #    @classmethod
# # #    def __loadxml__(cls, element, *args, **kwargs):
# # #        bodies_lookup, tilt_rad, rotation_rad = _Geometry._parse_xml(element)
# # #
# # #        nx = int(element.get('nx'))
# # #        ny = int(element.get('ny'))
# # #        xsize_m = float(element.get('xsize'))
# # #        ysize_m = float(element.get('ysize'))
# # #
# # #        obj = cls(nx, ny, xsize_m, ysize_m)
# # #        obj.tilt_rad = tilt_rad
# # #        obj.rotation_rad = rotation_rad
# # #
# # #        children = list(element.find('positions'))
# # #        for child in children:
# # #            index = int(child.get('index'))
# # #            position = int(child.get('x')), int(child.get('y'))
# # #            body = bodies_lookup[index]
# # #
# # #            obj._bodies[position] = body
# # #
# # #        return obj
# # #
# # #    def __savexml__(self, element, *args, **kwargs):
# # #        _Geometry.__savexml__(self, element, *args, **kwargs)
# # #
# # #        element.set('nx', str(self.nx))
# # #        element.set('ny', str(self.ny))
# # #        element.set('xsize', str(self.xsize_m))
# # #        element.set('ysize', str(self.ysize_m))
# # #
# # #        child = Element('positions')
# # #        for position, body in self._bodies.iteritems():
# # #            grandchild = Element('position')
# # #            grandchild.set('index', str(body._index))
# # #            grandchild.set('x', str(position[0]))
# # #            grandchild.set('y', str(position[1]))
# # #            child.append(grandchild)
# # #        element.append(child)
# # #
# # #    @property
# # #    def nx(self):
# # #        """
# # #        Number of cuboids in x-direction (read-only).
# # #        """
# # #        return self._props['nx']
# # #
# # #    @property
# # #    def ny(self):
# # #        """
# # #        Number of cuboids in y-direction (read-only).
# # #        """
# # #        return self._props['ny']
# # #
# # #    @property
# # #    def xsize_m(self):
# # #        """
# # #        Size of a cuboids in x-direction (in meters).
# # #        """
# # #        return self._props['xsize']
# # #
# # #    @xsize_m.setter
# # #    def xsize_m(self, size):
# # #        if size <= 0.0:
# # #            raise ValueError, 'size must be greater than 0'
# # #        self._props['xsize'] = size
# # #
# # #    @property
# # #    def ysize_m(self):
# # #        """
# # #        Size of a cuboids in y-direction (in meters).
# # #        """
# # #        return self._props['ysize']
# # #
# # #    @ysize_m.setter
# # #    def ysize_m(self, size):
# # #        if size <= 0.0:
# # #            raise ValueError, 'size must be greater than 0'
# # #        self._props['ysize'] = size
# # #
# # #    @property
# # #    def body(self):
# # #        return self._body
# # #
# # #    @property
# # #    def material(self):
# # #        return self._material
# # #
# # #    def get_bodies(self):
# # #        return set(self._bodies.values())
# # #
# # #    def get_dimensions(self, body):
# # #        reverse_lookup = dict(zip(self._bodies.values(), self._bodies.keys()))
# # #
# # #        try:
# # #            x, y = reverse_lookup[body]
# # #        except IndexError:
# # #            raise ValueError, "Unknown body: %s" % body
# # #
# # #        xsize = self.xsize_m
# # #        ysize = self.ysize_m
# # #
# # #        xmin = (x * xsize) - xsize / 2
# # #        xmax = (x * xsize) + xsize / 2
# # #        ymin = (y * ysize) - ysize / 2
# # #        ymax = (y * ysize) + ysize / 2
# # #
# # #        return _Dimension(xmin, xmax, ymin, ymax, zmax=0.0)
# # #
# # # XMLIO.register('{http://pymontecarlo.sf.net}cuboids2d', Cuboids2D)



