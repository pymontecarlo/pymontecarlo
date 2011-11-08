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
from pymontecarlo.util.xmlobj import XMLObject
from pymontecarlo.input.base.body import Body, Layer
from pymontecarlo.input.base.material import Material

# Globals and constants variables.
_MATERIAL_GETTER = attrgetter('material')
_THICKNESS_GETTER = attrgetter('thickness')

class _Geometry(XMLObject):

    def __init__(self, tilt=0, rotation=0):
        XMLObject.__init__(self)

        self.tilt = tilt
        self.rotation = rotation

    @classmethod
    def from_xml(cls, element):
        tilt = float(element.get('tilt'))
        rotation = float(element.get('rotation'))

        return cls(tilt, rotation)

    @property
    def tilt(self):
        """
        Specimen tilt in radians.
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
        Specimen rotation in radians
        """
        return self._rotation

    @rotation.setter
    def rotation(self, rotation):
        if rotation < -pi or rotation > pi:
            raise ValueError, "Rotation (%s) must be between [-pi, pi]." % rotation
        self._rotation = rotation

    def get_materials(self):
        return map(_MATERIAL_GETTER, self.get_bodies())

    def get_bodies(self):
        raise NotImplementedError

    def get_dimensions(self, body):
        """
        Returns a tuple of 6 values: (xmin, xmax, ymin, ymax, zmin, zmax) 
        corresponding to the dimensions of the body inside the geometry.
        All dimensions are in meters.
        
        :arg body: body to get the dimensions for
        """
        raise NotImplementedError

    def to_xml(self):
        element = XMLObject.to_xml(self)

        element.set('tilt', str(self.tilt))
        element.set('rotation', str(self.rotation))

        return element

class Substrate(_Geometry):

    def __init__(self, material):
        _Geometry.__init__(self)

        self._body = Body(material)

    def __repr__(self):
        return '<Substrate(material=%s)>' % str(self.material)

    @classmethod
    def from_xml(cls, element):
        geometry = _Geometry.from_xml(element)

        child = list(element.find("material"))[0]
        material = Material.from_xml(child)

        obj = cls(material)
        obj.tilt = geometry.tilt
        obj.rotation = geometry.rotation

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
        return [self._body]

    def get_dimensions(self, body):
        if body is self.body:
            return (float('-inf'), float('inf'),
                    float('-inf'), float('inf'),
                    float('-inf'), 0.0)
        else:
            raise ValueError, "Unknown body: %s" % body


    def to_xml(self):
        element = _Geometry.to_xml(self)

        child = Element('material')
        child.append(self.material.to_xml())
        element.append(child)

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
        geometry = _Geometry.from_xml(element)

        child = list(element.find("substrateMaterial"))[0]
        substrate_material = Material.from_xml(child)

        child = list(element.find("inclusionMaterial"))[0]
        inclusion_material = Material.from_xml(child)

        inclusion_diameter = float(element.get('inclusionDiameter'))

        obj = cls(substrate_material, inclusion_material, inclusion_diameter)
        obj.tilt = geometry.tilt
        obj.rotation = geometry.rotation

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
        return [self._substrate, self._inclusion]

    def get_dimensions(self, body):
        if body is self.substrate_body:
            return (float('-inf'), float('inf'),
                    float('-inf'), float('inf'),
                    float('-inf'), 0.0)
        elif body is self.inclusion_body:
            radius = self.inclusion_diameter / 2.0
            return (-radius, radius, -radius, radius, -radius, 0.0)
        else:
            raise ValueError, "Unknown body: %s" % body

    def to_xml(self):
        element = _Geometry.to_xml(self)

        child = Element('substrateMaterial')
        child.append(self.substrate_material.to_xml())
        element.append(child)

        child = Element('inclusionMaterial')
        child.append(self.inclusion_material.to_xml())
        element.append(child)

        element.set('inclusionDiameter', str(self.inclusion_diameter))

        return element

class _Layered(_Geometry):
    def __init__(self, layers=[]):
        _Geometry.__init__(self)

        self._layers = list(layers) # copy

    @classmethod
    def from_xml(cls, element):
        geometry = _Geometry.from_xml(element)

        children = list(element.find("layers"))
        layers = []
        for child in children:
            layers.append(Layer.from_xml(child))

        obj = cls(layers)
        obj.tilt = geometry.tilt
        obj.rotation = geometry.rotation

        return obj

    @property
    def layers(self):
        """
        Layers from top to bottom (multi-layers) or left to right (grain boundaries).
        See :class:`Layer`.
        """
        return self._layers

    def add_layer(self, mat, thickness):
        layer = Layer(mat, thickness)
        self._layers.append(layer)
        return layer

    def clear(self):
        """
        Removes all layers.
        """
        del self._layers[:]

    def get_bodies(self):
        return list(self.layers)

    def to_xml(self):
        element = _Geometry.to_xml(self)

        child = Element('layers')
        for layer in self.layers:
            child.append(layer.to_xml())
        element.append(child)

        return element

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
        geometry = _Layered.from_xml(element)

        children = list(element.find("substrateMaterial"))
        if children:
            substrate_material = Material.from_xml(children[0])
        else:
            substrate_material = None

        obj = cls(substrate_material, geometry.layers)
        obj.tilt = geometry.tilt
        obj.rotation = geometry.rotation

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
            bodies.append(self._substrate)

        return bodies

    def get_dimensions(self, body):
        if body is self.substrate_body and body is not None:
            zmax = -sum(map(_THICKNESS_GETTER, self.layers))
            return (float('-inf'), float('inf'),
                    float('-inf'), float('inf'),
                    float('-inf'), zmax)
        elif body in self.layers:
            index = self.layers.index(body)
            zmax = -sum(map(_THICKNESS_GETTER, self.layers[:index]))
            zmin = zmax - body.thickness
            return (float('-inf'), float('inf'),
                    float('-inf'), float('inf'),
                    zmin, zmax)
        else:
            raise ValueError, "Unknown body: %s" % body

    def to_xml(self):
        element = _Layered.to_xml(self)

        child = Element('substrateMaterial')
        if self.has_substrate():
            child.append(self.substrate_material.to_xml())
        element.append(child)

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
        geometry = _Layered.from_xml(element)

        child = list(element.find("leftMaterial"))[0]
        left_material = Material.from_xml(child)

        child = list(element.find("rightMaterial"))[0]
        right_material = Material.from_xml(child)

        obj = cls(left_material, right_material, geometry.layers)
        obj.tilt = geometry.tilt
        obj.rotation = geometry.rotation

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
        bodies = []

        bodies.append(self._left)
        bodies.extend(_Layered.get_bodies(self))
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
            positions.append[0.0]

        if body is self.left_body:
            return (float('-inf'), positions[0],
                    float('-inf'), float('inf'),
                    float('-inf'), float('inf'))
        elif body is self.right_body:
            return (positions[-1], float('inf'),
                    float('-inf'), float('inf'),
                    float('-inf'), float('inf'))
        elif body in self.layers:
            index = self.layers.index(body)
            return (positions[index], positions[index + 1],
                    float('-inf'), float('inf'),
                    float('-inf'), float('inf'))
        else:
            raise ValueError, "Unknown body: %s" % body

    def to_xml(self):
        element = _Layered.to_xml(self)

        child = Element('leftMaterial')
        child.append(self.left_material.to_xml())
        element.append(child)

        child = Element('rightMaterial')
        child.append(self.right_material.to_xml())
        element.append(child)

        return element
