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
from math import pi

# Third party modules.
from lxml.etree import Element

# Local modules.
from pymontecarlo.util.xmlutil import XMLIO
from pymontecarlo.input.base.option import Option
from pymontecarlo.util.oset import oset
from pymontecarlo.input.base.body import Body, Layer
from pymontecarlo.input.base.material import VACUUM

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
        materials_lookup = {}
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
            bodies_lookup[index] = XMLIO.from_xml(child, material=material)

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
            if isinstance(material, type(VACUUM)):
                material._index = 0
            else:
                material._index = count
                count += 1

        for i, body in enumerate(self.get_bodies()):
            body._index = i

    def _materials_to_xml(self):
        element = Element('materials')
        for material in self.get_materials():
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
        """
        return set(map(_MATERIAL_GETTER, self.get_bodies()))

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

        obj = cls(body.material)
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

XMLIO.register('substrate', Substrate)
XMLIO.register_loader('pymontecarlo.input.base.geometry.Substrate', Substrate)

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

        obj = cls(substrate.material, inclusion.material, diameter)
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

XMLIO.register('inclusion', Inclusion)
XMLIO.register_loader('pymontecarlo.input.base.geometry.Inclusion', Inclusion)

class _Layered(_Geometry):
    def __init__(self, layers=[]):
        _Geometry.__init__(self)

        self._props['layers'] = oset(layers) # copy

    @classmethod
    def _parse_xml_layers(cls, element, bodies_lookup):
        layer_indexes = map(int, element.get('layers').split(','))
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
            substrate_material = bodies_lookup[index].material
        else:
            substrate_material = None

        obj = cls(substrate_material, layers)
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

XMLIO.register('multiLayers', MultiLayers)
XMLIO.register_loader('pymontecarlo.input.base.geometry.MultiLayers', MultiLayers)

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

        self._props['left'] = Body(left_material)
        self._props['right'] = Body(right_material)

    def __repr__(self):
        return '<GrainBoundaries(left_material=%s, right_materials=%s, layers_count=%i)>' % \
            (str(self.left_material), str(self.right_material), len(self.layers))

    @classmethod
    def __loadxml__(cls, element):
        bodies_lookup, layers, tilt_rad, rotation_rad = _Layered._parse_xml(element)

        index = int(element.get('left_substrate'))
        left_material = bodies_lookup[index].material

        index = int(element.get('right_substrate'))
        right_material = bodies_lookup[index].material

        obj = cls(left_material, right_material, layers)
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

XMLIO.register('grainBoundaries', GrainBoundaries)
XMLIO.register_loader('pymontecarlo.input.base.geometry.GrainBoundaries', GrainBoundaries)
