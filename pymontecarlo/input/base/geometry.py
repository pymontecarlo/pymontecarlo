"""
================================================================================
:mod:`geometry` -- Base class of all geometries
================================================================================

.. module:: geometry
   :synopsis: Base class of all geometries

.. inheritance-diagram:: geometry

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from operator import attrgetter
from xml.etree.ElementTree import Element
from math import pi

# Third party modules.

# Local modules.
from pymontecarlo.util.xmlutil import objectxml, from_xml_choices
from pymontecarlo.util.oset import oset
from pymontecarlo.input.base.body import Body, Layer
from pymontecarlo.input.base.material import Material, VACUUM

# Globals and constants variables.
_MATERIAL_GETTER = attrgetter('material')
_THICKNESS_GETTER = attrgetter('thickness')
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
            (self.xmin, self.xmax, self.ymin, self.ymax, self.zmin, self.zmax)

    def __str__(self):
        return '(xmin=%s, xmax=%s, ymin=%s, ymax=%s, zmin=%s, zmax=%s)' % \
            (self.xmin, self.xmax, self.ymin, self.ymax, self.zmin, self.zmax)

    @property
    def xmin(self):
        return self._xmin

    @property
    def xmax(self):
        return self._xmax

    @property
    def ymin(self):
        return self._ymin

    @property
    def ymax(self):
        return self._ymax

    @property
    def zmin(self):
        return self._zmin

    @property
    def zmax(self):
        return self._zmax

    def to_tuple(self):
        return self.xmin, self.xmax, self.ymin, self.ymax, self.zmin, self.zmax

class _Geometry(objectxml):
    """
    Base class for all geometry representations.
    
    A geometry is composed of bodies (:class:`Body`).
    Bodies may have some specific properties (e.g. thickness), but they must
    all be defined with a material.
    A geometry can only refer to a body once, but bodies can be defined using
    the same material.
    """

    BODIES = [Body]
    MATERIALS = [Material]

    def __init__(self, tilt=0, rotation=0):
        self.tilt = tilt
        self.rotation = rotation

    @classmethod
    def _parse_xml_materials(cls, element):
        children = list(element.find('materials'))
        materials_lookup = {}
        for child in children:
            index = int(child.get('index'))
            materials_lookup[index] = from_xml_choices(child, cls.MATERIALS)

        return materials_lookup

    @classmethod
    def _parse_xml_bodies(cls, element, materials_lookup):
        children = list(element.find('bodies'))
        bodies_lookup = {}
        for child in children:
            index = int(child.get('index'))
            material = materials_lookup[int(child.get('material'))]
            bodies_lookup[index] = \
                from_xml_choices(child, cls.BODIES, material=material)

        return bodies_lookup

    @classmethod
    def _parse_xml(cls, element):
        materials_lookup = cls._parse_xml_materials(element)
        bodies_lookup = cls._parse_xml_bodies(element, materials_lookup)

        tilt = float(element.get('tilt'))
        rotation = float(element.get('rotation'))

        return bodies_lookup, tilt, rotation

    @property
    def tilt(self):
        """
        Specimen tilt in radians along the x-axis.
        """
        return self._tilt

    @tilt.setter
    def tilt(self, tilt):
        if tilt < -pi or tilt > pi:
            raise ValueError, "Tilt (%s) must be between [-pi, pi]." % tilt
        self._tilt = tilt

    @property
    def rotation(self):
        """
        Specimen rotation in radians along the z-axis.
        """
        return self._rotation

    @rotation.setter
    def rotation(self, rotation):
        if rotation < -pi or rotation > pi:
            raise ValueError, "Rotation (%s) must be between [-pi, pi]." % rotation
        self._rotation = rotation

    def get_materials(self):
        """
        Returns a :class:`set` of all materials inside this geometry.
        Since a :class:`set` is returned, even if the same material is used 
        more than once, it will only appear once.
        """
        return set(map(_MATERIAL_GETTER, self.get_bodies()))

    def get_bodies(self):
        """
        Returns a :class:`set` of all bodies inside this geometry.
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

    def to_xml(self):
        element = objectxml.to_xml(self)
        materials_lookup, bodies_lookup = self._create_lookups()

        element.append(self._materials_to_xml(materials_lookup))
        element.append(self._bodies_to_xml(materials_lookup, bodies_lookup))

        element.set('tilt', str(self.tilt))
        element.set('rotation', str(self.rotation))

        return element, bodies_lookup

    def _create_lookups(self):
        materials_lookup = {}
        count = 1
        for material in self.get_materials():
            if isinstance(material, type(VACUUM)):
                materials_lookup[material] = 0
            else:
                materials_lookup[material] = count
                count += 1

        bodies = self.get_bodies()
        bodies_lookup = dict(zip(bodies, range(len(bodies))))

        return materials_lookup, bodies_lookup

    def _materials_to_xml(self, materials_lookup):
        element = Element('materials')
        for material, index in materials_lookup.iteritems():
            child = material.to_xml()
            child.set('index', str(index))
            element.append(child)

        return element

    def _bodies_to_xml(self, materials_lookup, bodies_lookup):
        element = Element('bodies')
        for body, index in bodies_lookup.iteritems():
            child = body.to_xml()
            child.set('index', str(index))

            child.remove(child.find('material')) # remove material element
            child.set('material', str(materials_lookup[body.material]))

            element.append(child)

        return element

class Substrate(_Geometry):

    def __init__(self, material):
        _Geometry.__init__(self)

        self._body = Body(material)

    def __repr__(self):
        return '<Substrate(material=%s)>' % str(self.material)

    @classmethod
    def from_xml(cls, element):
        bodies_lookup, tilt, rotation = super(Substrate, cls)._parse_xml(element)

        index = int(element.get('substrate'))
        body = bodies_lookup[index]

        obj = cls(body.material)
        obj.tilt = tilt
        obj.rotation = rotation

        return obj

    @property
    def material(self):
        return self._body.material

    @material.setter
    def material(self, m):
        self._body.material = m

    @property
    def body(self):
        return self._body

    def get_bodies(self):
        return set([self._body])

    def get_dimensions(self, body):
        if body is self.body:
            return _Dimension(zmax=0.0)
        else:
            raise ValueError, "Unknown body: %s" % body

    def to_xml(self):
        element, bodies_lookup = _Geometry.to_xml(self)

        element.set('substrate', str(bodies_lookup[self.body]))

        return element

class Inclusion(_Geometry):

    def __init__(self, substrate_material, inclusion_material, inclusion_diameter):
        _Geometry.__init__(self)

        self._substrate = Body(substrate_material)
        self._inclusion = Body(inclusion_material)
        self.inclusion_diameter = inclusion_diameter

    def __repr__(self):
        return '<Inclusion(substrate_material=%s, inclusion_material=%s, inclusion_diameter=%s m)>' % \
            (str(self.substrate_material), str(self.inclusion_material), self.inclusion_diameter)

    @classmethod
    def from_xml(cls, element):
        bodies_lookup, tilt, rotation = super(Inclusion, cls)._parse_xml(element)

        index = int(element.get('substrate'))
        substrate = bodies_lookup[index]

        index = int(element.get('inclusion'))
        inclusion = bodies_lookup[index]

        diameter = float(element.get('diameter'))

        obj = cls(substrate.material, inclusion.material, diameter)
        obj.tilt = tilt
        obj.rotation = rotation

        return obj

    @property
    def substrate_material(self):
        return self._substrate.material

    @substrate_material.setter
    def substrate_material(self, m):
        self._substrate.material = m

    @property
    def substrate_body(self):
        return self._substrate

    @property
    def inclusion_material(self):
        return self._inclusion.material

    @inclusion_material.setter
    def inclusion_material(self, m):
        self._inclusion.material = m

    @property
    def inclusion_body(self):
        return self._inclusion

    @property
    def inclusion_diameter(self):
        return self._inclusion_diameter

    @inclusion_diameter.setter
    def inclusion_diameter(self, diameter):
        if diameter <= 0:
            raise ValueError, "Diameter (%s) must be greater than 0.0." % diameter
        self._inclusion_diameter = diameter

    def get_bodies(self):
        return set([self._substrate, self._inclusion])

    def get_dimensions(self, body):
        if body is self.substrate_body:
            return _Dimension(zmax=0.0)
        elif body is self.inclusion_body:
            radius = self.inclusion_diameter / 2.0
            return _Dimension(-radius, radius, -radius, radius, -radius, 0.0)
        else:
            raise ValueError, "Unknown body: %s" % body

    def to_xml(self):
        element, bodies_lookup = _Geometry.to_xml(self)

        element.set('substrate', str(bodies_lookup[self.substrate_body]))
        element.set('inclusion', str(bodies_lookup[self.inclusion_body]))
        element.set('diameter', str(self.inclusion_diameter))

        return element

class _Layered(_Geometry):
    BODIES = [Body, Layer]

    def __init__(self, layers=[]):
        _Geometry.__init__(self)

        self._layers = oset(layers) # copy

    @classmethod
    def _parse_xml_layers(cls, element, bodies_lookup):
        layer_indexes = map(int, element.get('layers').split(','))
        layers = map(bodies_lookup.get, layer_indexes)

        return layers

    @classmethod
    def _parse_xml(cls, element):
        bodies_lookup, tilt, rotation = super(_Layered, cls)._parse_xml(element)
        layers = cls._parse_xml_layers(element, bodies_lookup)

        return bodies_lookup, layers, tilt, rotation

    @property
    def layers(self):
        """
        Layers from top to bottom (multi-layers) or from left to right 
        (grain boundaries).
        Layers are stored inside an ordered set (:class:`oset`) to ensure
        that a layer (:class:`Layer`) is only added once.
        """
        return self._layers

    def add_layer(self, mat, thickness):
        layer = Layer(mat, thickness)
        self._layers.add(layer)
        return layer

    def clear(self):
        """
        Removes all layers.
        """
        del self._layers[:]

    def get_bodies(self):
        return oset(self.layers) # copy

    def to_xml(self):
        element, bodies_lookup = _Geometry.to_xml(self)

        layer_indexes = self._layers_to_xml(bodies_lookup)
        element.set('layers', ','.join(map(str, layer_indexes)))

        return element, bodies_lookup

    def _layers_to_xml(self, bodies_lookup):
        layer_indexes = []
        for layer in self.layers:
            layer_indexes.append(bodies_lookup[layer])

        return layer_indexes

class MultiLayers(_Layered):
    def __init__(self, substrate_material=None, layers=[]):
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
            self._substrate = Body(substrate_material)
        else:
            self._substrate = None

    def __repr__(self):
        if self.has_substrate():
            return '<MultiLayers(substrate_material=%s, layers_count=%i)>' % \
                (str(self.substrate_material), len(self.layers))
        else:
            return '<MultiLayers(No substrate, layers_count=%i)>' % len(self.layers)

    @classmethod
    def from_xml(cls, element):
        bodies_lookup, layers, tilt, rotation = super(MultiLayers, cls)._parse_xml(element)

        if element.get('substrate') is not None:
            index = int(element.get('substrate'))
            substrate_material = bodies_lookup[index].material
        else:
            substrate_material = None

        obj = cls(substrate_material, layers)
        obj.tilt = tilt
        obj.rotation = rotation

        return obj

    @property
    def substrate_material(self):
        """
        Material of the substrate. 
        Raises ``RuntimeError` if the multi-layers does not have a substrate.
        To remove the substrate, set the material to ``None``.
        """
        if self._substrate is None:
            raise RuntimeError, "Multi-layers does not have a substrate"
        return self._substrate.material

    @substrate_material.setter
    def substrate_material(self, m):
        if m is None:
            self._substrate = None
        else:
            if self._substrate is None:
                self._substrate = Body(m)
            else:
                self._substrate.material = m

    def has_substrate(self):
        """
        Returns ``True`` if a substrate material has been defined.
        """
        return self._substrate is not None

    @property
    def substrate_body(self):
        return self._substrate

    def get_bodies(self):
        bodies = _Layered.get_bodies(self)

        if self._substrate is not None:
            bodies.add(self._substrate)

        return bodies

    def get_dimensions(self, body):
        if body is self.substrate_body and body is not None:
            zmax = -sum(map(_THICKNESS_GETTER, self.layers))
            return _Dimension(zmax=zmax)
        elif body in self.layers:
            index = self.layers.index(body)
            zmax = -sum(map(_THICKNESS_GETTER, self.layers[:index]))
            zmin = zmax - body.thickness
            return _Dimension(zmin=zmin, zmax=zmax)
        else:
            raise ValueError, "Unknown body: %s" % body

    def to_xml(self):
        element, bodies_lookup = _Layered.to_xml(self)

        if self.has_substrate():
            element.set('substrate', str(bodies_lookup[self.substrate_body]))

        return element

class GrainBoundaries(_Layered):
    def __init__(self, left_material, right_material, layers=[]):
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

        self._left = Body(left_material)
        self._right = Body(right_material)

    def __repr__(self):
        return '<GrainBoundaries(left_material=%s, right_materials=%s, layers_count=%i)>' % \
            (str(self.left_material), str(self.right_material), len(self.layers))

    @classmethod
    def from_xml(cls, element):
        bodies_lookup, layers, tilt, rotation = \
            super(GrainBoundaries, cls)._parse_xml(element)

        index = int(element.get('left_material'))
        left_material = bodies_lookup[index].material

        index = int(element.get('right_material'))
        right_material = bodies_lookup[index].material

        obj = cls(left_material, right_material, layers)
        obj.tilt = tilt
        obj.rotation = rotation

        return obj

    @property
    def left_material(self):
        """
        Material of the left substrate. 
        """
        return self._left.material

    @left_material.setter
    def left_material(self, m):
        self._left.material = m

    @property
    def left_body(self):
        return self._left

    @property
    def right_material(self):
        """
        Material of the right substrate. 
        """
        return self._right.material

    @right_material.setter
    def right_material(self, m):
        self._right.material = m

    @property
    def right_body(self):
        return self._right

    def get_bodies(self):
        bodies = _Layered.get_bodies(self)

        bodies.insert(0, self._left)
        bodies.append(self._right)

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

    def to_xml(self):
        element, bodies_lookup = _Layered.to_xml(self)

        element.set('left_material', str(bodies_lookup[self.left_body]))
        element.set('right_material', str(bodies_lookup[self.right_body]))

        return element
