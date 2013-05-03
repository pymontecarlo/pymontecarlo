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
           'Inclusion',
           'MultiLayers',
           'Sphere',
           'Substrate']

# Standard library modules.
from operator import attrgetter
from math import pi
import itertools

# Third party modules.

# Local modules.
from pymontecarlo.util.xmlutil import XMLIO, Element
from pymontecarlo.util.oset import oset

from pymontecarlo.input.option import Option
from pymontecarlo.input.body import Body, Layer
from pymontecarlo.input.material import VACUUM

# Globals and constants variables.
_MATERIAL_GETTER = attrgetter('material')
_THICKNESS_GETTER = attrgetter('thickness_m')
POSINF = float('inf')
NEGINF = float('-inf')

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

class _Geometry(Option):
    """
    Base class for all geometry representations.
    
    A geometry is composed of bodies (:class:`Body`).
    Bodies may have some specific properties (e.g. thickness), but they must
    all be defined with a material.
    A geometry can only refer to a body once, but bodies can be defined using
    the same material.
    """

    def __init__(self, tilt_rad=0, rotation_rad=0):
        Option.__init__(self)

        self.tilt_rad = tilt_rad
        self.rotation_rad = rotation_rad

    @classmethod
    def _parse_xml_materials(cls, element):
        children = list(element.find('materials'))
        materials_lookup = {0: VACUUM}
        for child in children:
            index = int(child.get('index'))
            materials_lookup[index] = XMLIO.from_xml(child)

        return materials_lookup

    @classmethod
    def _parse_xml_bodies(cls, element, materials_lookup):
        children = list(element.find('bodies'))
        bodies_lookup = {}
        for child in children:
            index = int(child.get('index'))
            material = materials_lookup[int(child.get('material'))]
            body = XMLIO.from_xml(child, material=material)
            body._index = index
            bodies_lookup[index] = body

        return bodies_lookup

    @classmethod
    def _parse_xml(cls, element):
        materials_lookup = cls._parse_xml_materials(element)
        bodies_lookup = cls._parse_xml_bodies(element, materials_lookup)

        tilt_rad = float(element.get('tilt'))
        rotation_rad = float(element.get('rotation'))

        return bodies_lookup, tilt_rad, rotation_rad

    def _indexify(self):
        count = 1
        for material in self.get_materials():
            if material is not VACUUM: # Vacuum has an index of 0
                material._index = count
                count += 1

        for i, body in enumerate(self.get_bodies()):
            body._index = i

    def _materials_to_xml(self):
        element = Element('materials')
        for material in self.get_materials():
            if material is VACUUM:
                continue
            child = material.to_xml()
            child.set('index', str(material._index))
            element.append(child)

        return element

    def _bodies_to_xml(self):
        element = Element('bodies')
        for body in self.get_bodies():
            child = body.to_xml()
            child.set('index', str(body._index))

            child.remove(child.find('material')) # remove material element
            child.set('material', str(body.material._index))

            element.append(child)

        return element

    def __savexml__(self, element, *args, **kwargs):
        self._indexify()

        element.append(self._materials_to_xml())
        element.append(self._bodies_to_xml())

        element.set('tilt', str(self.tilt_rad))
        element.set('rotation', str(self.rotation_rad))

    @property
    def tilt_rad(self):
        """
        Specimen tilt in radians along the x-axis.
        """
        return self._props['tilt']

    @tilt_rad.setter
    def tilt_rad(self, tilt):
        if tilt < -pi or tilt > pi:
            raise ValueError, "Tilt (%s) must be between [-pi, pi]." % tilt
        self._props['tilt'] = tilt

    @property
    def rotation_rad(self):
        """
        Specimen rotation in radians along the z-axis.
        """
        return self._props['rotation']

    @rotation_rad.setter
    def rotation_rad(self, rotation):
        if rotation < -pi or rotation > pi:
            raise ValueError, "Rotation (%s) must be between [-pi, pi]." % rotation
        self._props['rotation'] = rotation

    def get_materials(self):
        """
        Returns a :class:`set` of all materials inside this geometry.
        Since a :class:`set` is returned, even if the same material is used 
        more than once, it will only appear once.
        :obj:`VACUUM` is not considered as a material, so this object will
        not appear in this list.
        """
        materials = set(map(_MATERIAL_GETTER, self.get_bodies()))
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

class Substrate(_Geometry):
    def __init__(self, material):
        _Geometry.__init__(self)

        self._props['body'] = Body(material)

    def __repr__(self):
        return '<Substrate(material=%s)>' % str(self.material)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        bodies_lookup, tilt_rad, rotation_rad = _Geometry._parse_xml(element)

        index = int(element.get('substrate'))
        body = bodies_lookup[index]

        obj = cls(VACUUM)
        obj._props['body'] = body
        obj.tilt_rad = tilt_rad
        obj.rotation_rad = rotation_rad

        return obj

    def __savexml__(self, element, *args, **kwargs):
        _Geometry.__savexml__(self, element, *args, **kwargs)
        element.set('substrate', str(self.body._index))

    @property
    def material(self):
        return self.body.material

    @material.setter
    def material(self, m):
        self.body.material = m

    @property
    def body(self):
        return self._props['body']

    def get_bodies(self):
        return set([self.body])

    def get_dimensions(self, body):
        if body is self.body:
            return _Dimension(zmax=0.0)
        else:
            raise ValueError, "Unknown body: %s" % body

XMLIO.register('{http://pymontecarlo.sf.net}substrate', Substrate)

class Inclusion(_Geometry):
    def __init__(self, substrate_material, inclusion_material, inclusion_diameter_m):
        _Geometry.__init__(self)

        self._props['substrate'] = Body(substrate_material)
        self._props['inclusion'] = Body(inclusion_material)
        self.inclusion_diameter_m = inclusion_diameter_m

    def __repr__(self):
        return '<Inclusion(substrate_material=%s, inclusion_material=%s, inclusion_diameter=%s m)>' % \
            (str(self.substrate_material), str(self.inclusion_material), self.inclusion_diameter_m)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        bodies_lookup, tilt, rotation = _Geometry._parse_xml(element)

        index = int(element.get('substrate'))
        substrate = bodies_lookup[index]

        index = int(element.get('inclusion'))
        inclusion = bodies_lookup[index]

        diameter = float(element.get('diameter'))

        obj = cls(VACUUM, VACUUM, diameter)
        obj._props['substrate'] = substrate
        obj._props['inclusion'] = inclusion
        obj.tilt_rad = tilt
        obj.rotation_rad = rotation

        return obj

    def __savexml__(self, element, *args, **kwargs):
        _Geometry.__savexml__(self, element, *args, **kwargs)
        element.set('substrate', str(self.substrate_body._index))
        element.set('inclusion', str(self.inclusion_body._index))
        element.set('diameter', str(self.inclusion_diameter_m))

    @property
    def substrate_material(self):
        return self.substrate_body.material

    @substrate_material.setter
    def substrate_material(self, m):
        self.substrate_body.material = m

    @property
    def substrate_body(self):
        return self._props['substrate']

    @property
    def inclusion_material(self):
        return self.inclusion_body.material

    @inclusion_material.setter
    def inclusion_material(self, m):
        self.inclusion_body.material = m

    @property
    def inclusion_body(self):
        return self._props['inclusion']

    @property
    def inclusion_diameter_m(self):
        return self._props['inclusion diameter']

    @inclusion_diameter_m.setter
    def inclusion_diameter_m(self, diameter):
        if diameter <= 0:
            raise ValueError, "Diameter (%s) must be greater than 0.0." % diameter
        self._props['inclusion diameter'] = diameter

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

XMLIO.register('{http://pymontecarlo.sf.net}inclusion', Inclusion)

class _Layered(_Geometry):
    def __init__(self, layers=None):
        _Geometry.__init__(self)

        if layers is None: layers = []
        self._props['layers'] = oset(layers) # copy

    @classmethod
    def _parse_xml_layers(cls, element, bodies_lookup):
        layers_str = element.get('layers')
        if not layers_str:
            return []

        layer_indexes = map(int, layers_str.split(','))
        layers = map(bodies_lookup.get, layer_indexes)

        return layers

    @classmethod
    def _parse_xml(cls, element):
        bodies_lookup, tilt_rad, rotation_rad = _Geometry._parse_xml(element)
        layers = cls._parse_xml_layers(element, bodies_lookup)

        return bodies_lookup, layers, tilt_rad, rotation_rad

    def __savexml__(self, element, *args, **kwargs):
        _Geometry.__savexml__(self, element, *args, **kwargs)

        layer_indexes = []
        for layer in self.layers:
            layer_indexes.append(layer._index)
        element.set('layers', ','.join(map(str, layer_indexes)))

    @property
    def layers(self):
        """
        Layers from top to bottom (multi-layers) or from left to right 
        (grain boundaries).
        Layers are stored inside an ordered set (:class:`oset`) to ensure
        that a layer (:class:`Layer`) is only added once.
        """
        return self._props['layers']

    def add_layer(self, material, thickness):
        """
        Adds a layer to the geometry.
        The layer is added after the previous layers.
        
        This method is equivalent to::
        
            geometry.layers.add(Layer(material, thickness))
        
        :arg material: material of the layer
        :type material: :class:`Material`
        
        :arg thickness: thickness of the layer in meters
        """
        layer = Layer(material, thickness)
        self.layers.add(layer)
        return layer

    def clear(self):
        """
        Removes all layers.
        """
        del self.layers[:]

    def get_bodies(self):
        return set(self.layers) # copy

class MultiLayers(_Layered):
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
        _Layered.__init__(self, layers)

        if substrate_material is not None:
            self._props['substrate'] = Body(substrate_material)
        else:
            self._props['substrate'] = None

    def __repr__(self):
        if self.has_substrate():
            return '<MultiLayers(substrate_material=%s, layers_count=%i)>' % \
                (str(self.substrate_material), len(self.layers))
        else:
            return '<MultiLayers(No substrate, layers_count=%i)>' % len(self.layers)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        bodies_lookup, layers, tilt_rad, rotation_rad = _Layered._parse_xml(element)

        if element.get('substrate') is not None:
            index = int(element.get('substrate'))
            substrate = bodies_lookup[index]
        else:
            substrate = None

        obj = cls(VACUUM, layers)
        obj._props['substrate'] = substrate
        obj.tilt_rad = tilt_rad
        obj.rotation_rad = rotation_rad

        return obj

    def __savexml__(self, element, *args, **kwargs):
        _Layered.__savexml__(self, element, *args, **kwargs)

        if self.has_substrate():
            element.set('substrate', str(self.substrate_body._index))

    @property
    def substrate_material(self):
        """
        Material of the substrate. 
        Raises ``RuntimeError` if the multi-layers does not have a substrate.
        To remove the substrate, set the material to ``None``.
        """
        if not self.has_substrate():
            raise RuntimeError, "Multi-layers does not have a substrate"
        return self.substrate_body.material

    @substrate_material.setter
    def substrate_material(self, m):
        if m is None:
            self._props['substrate'] = None
        else:
            if self._props['substrate'] is None:
                self._props['substrate'] = Body(m)
            else:
                self._props['substrate'].material = m

    def has_substrate(self):
        """
        Returns ``True`` if a substrate material has been defined.
        """
        return self.substrate_body is not None

    @property
    def substrate_body(self):
        return self._props['substrate']

    def get_bodies(self):
        bodies = _Layered.get_bodies(self)

        if self.has_substrate():
            bodies.add(self.substrate_body)

        return bodies

    def get_dimensions(self, body):
        if body is self.substrate_body and body is not None:
            zmax = -sum(map(_THICKNESS_GETTER, self.layers))
            return _Dimension(zmax=zmax)
        elif body in self.layers:
            index = self.layers.index(body)
            zmax = -sum(map(_THICKNESS_GETTER, self.layers[:index]))
            zmin = zmax - body.thickness_m
            return _Dimension(zmin=zmin, zmax=zmax)
        else:
            raise ValueError, "Unknown body: %s" % body

XMLIO.register('{http://pymontecarlo.sf.net}multiLayers', MultiLayers)

class GrainBoundaries(_Layered):
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
        _Layered.__init__(self, layers)

        self._props['left'] = Body(left_material)
        self._props['right'] = Body(right_material)

    def __repr__(self):
        return '<GrainBoundaries(left_material=%s, right_materials=%s, layers_count=%i)>' % \
            (str(self.left_material), str(self.right_material), len(self.layers))

    @classmethod
    def __loadxml__(cls, element):
        bodies_lookup, layers, tilt_rad, rotation_rad = _Layered._parse_xml(element)

        index = int(element.get('left_substrate'))
        left = bodies_lookup[index]

        index = int(element.get('right_substrate'))
        right = bodies_lookup[index]

        obj = cls(VACUUM, VACUUM, layers)
        obj._props['left'] = left
        obj._props['right'] = right
        obj.tilt_rad = tilt_rad
        obj.rotation_rad = rotation_rad

        return obj

    def __savexml__(self, element, *args, **kwargs):
        _Layered.__savexml__(self, element, *args, **kwargs)

        element.set('left_substrate', str(self.left_body._index))
        element.set('right_substrate', str(self.right_body._index))

    @property
    def left_material(self):
        """
        Material of the left substrate. 
        """
        return self.left_body.material

    @left_material.setter
    def left_material(self, m):
        self.left_body.material = m

    @property
    def left_body(self):
        return self._props['left']

    @property
    def right_material(self):
        """
        Material of the right substrate. 
        """
        return self.right_body.material

    @right_material.setter
    def right_material(self, m):
        self.right_body.material = m

    @property
    def right_body(self):
        return self._props['right']

    def get_bodies(self):
        bodies = _Layered.get_bodies(self)

        bodies.add(self.left_body)
        bodies.add(self.right_body)

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
            index = self.layers.index(body)
            return _Dimension(xmin=positions[index], xmax=positions[index + 1], zmax=0)
        else:
            raise ValueError, "Unknown body: %s" % body

XMLIO.register('{http://pymontecarlo.sf.net}grainBoundaries', GrainBoundaries)

class ThinGrainBoundaries(GrainBoundaries):
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

    @classmethod
    def __loadxml__(cls, element):
        gb = GrainBoundaries.__loadxml__(element)
        thickness_m = float(element.get('thickness'))

        obj = cls(VACUUM, VACUUM, thickness_m, gb.layers)
        obj._props['left'] = gb.left_body
        obj._props['right'] = gb.right_body
        obj.tilt_rad = gb.tilt_rad
        obj.rotation_rad = gb.rotation_rad

        return obj

    def __savexml__(self, element, *args, **kwargs):
        GrainBoundaries.__savexml__(self, element, *args, **kwargs)

        element.set('thickness', str(self.thickness_m))

    @property
    def thickness_m(self):
        """
        Thickness of geometry (in meters).
        """
        return self._props['thickness']

    @thickness_m.setter
    def thickness_m(self, thickness_m):
        if thickness_m <= 0:
            raise ValueError, 'Thickness must be greater than 0'
        self._props['thickness'] = thickness_m

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

        zmin = -self.thickness_m

        if body is self.left_body:
            return _Dimension(xmax=positions[0], zmax=0, zmin=zmin)
        elif body is self.right_body:
            return _Dimension(xmin=positions[-1], zmax=0, zmin=zmin)
        elif body in self.layers:
            index = self.layers.index(body)
            return _Dimension(xmin=positions[index], xmax=positions[index + 1], 
                              zmax=0, zmin=zmin)
        else:
            raise ValueError, "Unknown body: %s" % body

XMLIO.register('{http://pymontecarlo.sf.net}thinGrainBoundaries', ThinGrainBoundaries)

class Sphere(_Geometry):

    def __init__(self, material, diameter_m):
        """
        Creates a geometry consisting of a sphere.
        The sphere is entirely located below the ``z=0`` plane.
        
        :arg material: material
        :arg diameter_m: diameter (in meters)
        """
        _Geometry.__init__(self)

        self._props['body'] = Body(material)
        self.diameter_m = diameter_m

    def __repr__(self):
        return '<Sphere(material=%s, diameter=%s m)>' % \
                    (str(self.material), self.diameter_m)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        bodies_lookup, tilt_rad, rotation_rad = _Geometry._parse_xml(element)

        index = int(element.get('substrate'))
        body = bodies_lookup[index]

        diameter_m = float(element.get('diameter'))

        obj = cls(VACUUM, diameter_m)
        obj._props['body'] = body
        obj.tilt_rad = tilt_rad
        obj.rotation_rad = rotation_rad

        return obj

    def __savexml__(self, element, *args, **kwargs):
        _Geometry.__savexml__(self, element, *args, **kwargs)
        element.set('substrate', str(self.body._index))
        element.set('diameter', str(self.diameter_m))

    @property
    def material(self):
        return self.body.material

    @material.setter
    def material(self, m):
        self.body.material = m

    @property
    def diameter_m(self):
        return self._props['diameter']

    @diameter_m.setter
    def diameter_m(self, diameter_m):
        if diameter_m <= 0:
            raise ValueError, 'Diameter must be greater than 0.'
        self._props['diameter'] = diameter_m

    @property
    def body(self):
        return self._props['body']

    def get_bodies(self):
        return set([self.body])

    def get_dimensions(self, body):
        if body is self.body:
            d = self.diameter_m
            r = d / 2.0
            return _Dimension(xmin= -r, xmax=r,
                              ymin= -r, ymax=r,
                              zmin= -d, zmax=0.0)
        else:
            raise ValueError, "Unknown body: %s" % body

XMLIO.register('{http://pymontecarlo.sf.net}sphere', Sphere)

class Cuboids2D(_Geometry):

    class __Cuboids2DBody(object):
        def __init__(self, bodies):
            self._bodies = bodies

        def __getitem__(self, index):
            if index not in self._bodies:
                raise IndexError, 'No body at index (%i, %i)' % index
            return self._bodies[index]

    class __Cuboids2DMaterial(object):
        def __init__(self, bodies):
            self._bodies = bodies

        def __getitem__(self, index):
            if index not in self._bodies:
                raise IndexError, 'No material at index (%i, %i)' % index
            return self._bodies[index].material

        def __setitem__(self, index, material):
            if index not in self._bodies:
                raise IndexError, 'No material at index (%i, %i)' % index
            self._bodies[index].material = material

    def __init__(self, nx, ny, xsize_m, ysize_m):
        """
        Creates a geometry made of *nx* by *ny* adjacent cuboids with 
        infinite depth. 
        Each cuboid was a size of *xsize* by *ysize*.
        The number of cuboids in x and y-direction must be odd, so that the
        cuboid (nx/2+1, ny/2+1) is located at the center.
        
        The position (0, 0) is given to the center cuboid. 
        Cuboids on the upper-left quadrant have positive indexes whereas
        cuboids on the bottom-right quadrant have negative indexes.
        
        The material of each cuboid can be access as follows::
        
            >>> print geometry.material[0,0] # center cuboid
            >>> print geometry.material[1,0] # cuboid to the left of the center cuboid
            >>> print geometry.material[0,1] # cuboid above the center cuboid
            >>> print geometry.material[1,-2] # cuboid one up and 2 to the right of the center cuboid
            
        .. note:: 
        
           When the geometry is created, all cuboids have no material (i.e. vacuum).
        
        :arg nx: number of cuboids in x-direction (odd number)
        :type nx: :class:`int`
        
        :arg ny: number of cuboids in y-direction (odd number)
        :type ny: :class:`int`
        
        :arg xsize_m: size of a cuboid in x-direction (in meters)
        :type xsize_m: :class:`float`
        
        :arg ysize_m: size of a cuboid in y-direction (in meters)
        :type ysize_m: :class:`float`
        """
        _Geometry.__init__(self)

        if nx < 1 and nx % 2 == 1:
            raise ValueError, 'nx must be greater or equal to 1 and an odd number'
        self._props['nx'] = nx

        if ny < 1 and ny % 2 == 1:
            raise ValueError, 'ny must be greater or equal to 1 and an odd number'
        self._props['ny'] = ny

        self.xsize_m = xsize_m
        self.ysize_m = ysize_m

        # Create empty bodies
        self._bodies = {}

        for position in itertools.product(range(-(nx / 2), nx / 2 + 1),
                                          range(-(ny / 2), ny / 2 + 1)):
            body = Body(VACUUM)
            self._bodies[position] = body

        self._body = self.__Cuboids2DBody(self._bodies)
        self._material = self.__Cuboids2DMaterial(self._bodies)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        bodies_lookup, tilt_rad, rotation_rad = _Geometry._parse_xml(element)

        nx = int(element.get('nx'))
        ny = int(element.get('ny'))
        xsize_m = float(element.get('xsize'))
        ysize_m = float(element.get('ysize'))

        obj = cls(nx, ny, xsize_m, ysize_m)
        obj.tilt_rad = tilt_rad
        obj.rotation_rad = rotation_rad

        children = list(element.find('positions'))
        for child in children:
            index = int(child.get('index'))
            position = int(child.get('x')), int(child.get('y'))
            body = bodies_lookup[index]

            obj._bodies[position] = body

        return obj

    def __savexml__(self, element, *args, **kwargs):
        _Geometry.__savexml__(self, element, *args, **kwargs)

        element.set('nx', str(self.nx))
        element.set('ny', str(self.ny))
        element.set('xsize', str(self.xsize_m))
        element.set('ysize', str(self.ysize_m))

        child = Element('positions')
        for position, body in self._bodies.iteritems():
            grandchild = Element('position')
            grandchild.set('index', str(body._index))
            grandchild.set('x', str(position[0]))
            grandchild.set('y', str(position[1]))
            child.append(grandchild)
        element.append(child)

    @property
    def nx(self):
        """
        Number of cuboids in x-direction (read-only).
        """
        return self._props['nx']

    @property
    def ny(self):
        """
        Number of cuboids in y-direction (read-only).
        """
        return self._props['ny']

    @property
    def xsize_m(self):
        """
        Size of a cuboids in x-direction (in meters).
        """
        return self._props['xsize']

    @xsize_m.setter
    def xsize_m(self, size):
        if size <= 0.0:
            raise ValueError, 'size must be greater than 0'
        self._props['xsize'] = size

    @property
    def ysize_m(self):
        """
        Size of a cuboids in y-direction (in meters).
        """
        return self._props['ysize']

    @ysize_m.setter
    def ysize_m(self, size):
        if size <= 0.0:
            raise ValueError, 'size must be greater than 0'
        self._props['ysize'] = size

    @property
    def body(self):
        return self._body

    @property
    def material(self):
        return self._material

    def get_bodies(self):
        return set(self._bodies.values())

    def get_dimensions(self, body):
        reverse_lookup = dict(zip(self._bodies.values(), self._bodies.keys()))

        try:
            x, y = reverse_lookup[body]
        except IndexError:
            raise ValueError, "Unknown body: %s" % body

        xsize = self.xsize_m
        ysize = self.ysize_m

        xmin = (x * xsize) - xsize / 2
        xmax = (x * xsize) + xsize / 2
        ymin = (y * ysize) - ysize / 2
        ymax = (y * ysize) + ysize / 2

        return _Dimension(xmin, xmax, ymin, ymax, zmax=0.0)

XMLIO.register('{http://pymontecarlo.sf.net}cuboids2d', Cuboids2D)
