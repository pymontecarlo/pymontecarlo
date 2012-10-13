#!/usr/bin/env python
"""
================================================================================
:mod:`geometry` -- Controls for geometry
================================================================================

.. module:: geometry
   :synopsis: Controls for geometry

.. inheritance-diagram:: pymontecarlo.ui.gui.input.geometry

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import math

# Third party modules.
from OpenGL import GL
from OpenGL import GLU

# Local modules.
from pymontecarlo.input.geometry import \
    Substrate, Inclusion, MultiLayers, GrainBoundaries, Sphere

# Globals and constants variables.

class _GeometryGLManager(object):

    def __init__(self):
        self._geometries = {}

    def register(self, geometry, geometrygl):
        """
        Associates a :class:`_Geometry` class with a :class:`_GeometryGL` class. 
        
        Raises :exc:`ValueError` if the specified :class:`_Geometry` is already 
        associated with a different class. 
        
        :arg geometry: geometry class
        :arg geometrygl: geometry GL class
        """
        if geometry in self._geometries and self._geometries.get(geometry) != geometrygl:
            raise ValueError, 'A geometry GL (%s) is already registered with the geometry (%s).' % \
                (self._geometries[geometry].__name__, geometry.__name__)

        self._geometries[geometry] = geometrygl

    def get(self, geometry):
        """
        Returns a :class:`_GeometrGL` object for the specified geometry.
        """
        if geometry.__class__ not in self._geometries:
            raise ValueError, 'No geometry GL found for geometry (%s). Please register it first.' % \
                geometry.__class__.__name__
        return self._geometries[geometry.__class__](geometry)

GeometryGLManager = _GeometryGLManager()

# Colors from PENELOPE
COLORS = \
[(0.000000, 0.000000, 0.000000), # Black
(0.000000, 0.000000, 1.000000), # Blue
(0.000000, 1.000000, 0.000000), # Green
(1.000000, 0.000000, 0.000000), # Red
(0.000000, 1.000000, 1.000000), # Cyan
(1.000000, 0.000000, 1.000000), # Magenta
(1.000000, 1.000000, 0.000000), # Yellow
(1.000000, 0.600000, 0.800000), # Pink
(1.000000, 0.400000, 0.000000), # Orange
(1.000000, 1.000000, 1.000000), # White
(0.600000, 0.000000, 0.800000), # Purple
(0.800000, 0.400000, 0.200000), # Red Brown
(0.200000, 0.000000, 0.800000), # Deep Blue
(0.000000, 0.600000, 0.200000), # Grass Green
(0.600000, 0.000000, 0.000000), # Ruby Red
(0.400000, 0.400000, 1.000000), # Electric Blue
(0.600000, 0.600000, 0.200000), # Olive
(0.200000, 0.400000, 0.600000), # Desert Blue
(0.800000, 0.400000, 0.800000), # Violet
(0.000000, 0.400000, 0.200000), # Forest Green
(1.000000, 0.800000, 0.000000), # Deep Yellow
(0.600000, 0.600000, 0.400000), # Khaki
(0.400000, 1.000000, 0.800000), # Turquoise
(0.800000, 0.200000, 0.400000), # Regal Red
(0.600000, 0.400000, 0.200000), # Brown
(1.000000, 0.400000, 0.600000), # Deep Pink
(0.200000, 0.600000, 0.400000), # Kentucky Green
(1.000000, 0.600000, 0.200000), # Light Orange
(0.200000, 0.800000, 0.600000), # Sea Green
(1.000000, 1.000000, 0.400000), # Light Yellow
(0.000000, 0.200000, 0.600000), # Navy Blue
(0.600000, 1.000000, 0.000000), # Chartreuse
(0.200000, 0.200000, 0.000000), # Murky Green
(0.800000, 0.600000, 0.200000), # Gold
(0.600000, 0.200000, 0.400000), # Crimson
(0.400000, 0.400000, 0.800000), # Twilight Blue
(1.000000, 1.000000, 0.600000), # Chalk
(0.600000, 0.800000, 0.800000), # Light BlueGreen
(0.400000, 0.600000, 0.400000), # Army Green
(0.400000, 0.200000, 0.200000), # Dark Brown
(1.000000, 0.600000, 1.000000), # Light Violet
(0.000000, 0.000000, 0.400000), # Deep Navy Blue
(0.400000, 0.200000, 0.600000), # Grape
(0.800000, 0.200000, 0.600000), # Deep Rose
(1.000000, 0.800000, 0.800000), # Faded Pink
(1.000000, 0.600000, 0.400000), # Peach
(0.600000, 0.800000, 0.200000), # Martian Green
(0.400000, 0.600000, 0.600000), # Ocean Green
(1.000000, 0.800000, 0.600000), # Sand
(0.800000, 0.400000, 1.000000), # Light Purple
(0.400000, 0.600000, 1.000000), # Baby Blue
(0.800000, 0.200000, 0.000000), # Brick Red
(1.000000, 0.400000, 0.400000), # Tropical Pink
(0.600000, 0.000000, 0.600000), # Deep Violet
(0.200000, 0.800000, 0.400000), # Light Green
(0.000000, 0.200000, 0.200000), # Dark Green
(1.000000, 0.600000, 0.600000), # Soft Pink
(0.400000, 0.200000, 1.000000), # Deep Azure
(0.600000, 0.400000, 0.600000), # Dusty Plum
(1.000000, 0.400000, 0.200000), # Autumn Orange
(1.000000, 1.000000, 0.800000), # Pale Yellow
(0.000000, 0.800000, 1.000000), # Sky Blue
(0.600000, 0.800000, 0.400000), # Dull Green
(1.000000, 0.200000, 0.600000), # Hot Pink
(0.200000, 0.000000, 0.600000), # Storm Blue
(0.800000, 0.400000, 0.600000), # Dusty Rose
(0.400000, 0.000000, 0.400000), # Plum
(0.600000, 1.000000, 0.600000), # Mint Green
(0.400000, 0.600000, 0.200000), # Avocado Green
(0.400000, 0.000000, 0.800000), # Deep River
(0.800000, 0.800000, 1.000000), # Powder Blue
(1.000000, 0.000000, 0.400000), # Neon Red
(0.800000, 0.600000, 0.800000), # Pale Purple
(0.400000, 0.400000, 0.200000), # Olive Drab
(0.600000, 0.200000, 0.800000), # Majestic Purple
(0.800000, 1.000000, 0.800000), # Ghost Green
(0.200000, 0.800000, 0.200000), # Spring Green
(0.800000, 0.200000, 1.000000), # Neon Purple
(0.400000, 0.200000, 0.000000), # Walnut
(0.600000, 0.400000, 0.800000), # Twilight Violet
(0.200000, 0.400000, 0.400000), # Moss Green
(0.800000, 0.600000, 1.000000), # Easter Purple
(0.200000, 0.000000, 0.400000), # Deep Purple
(0.600000, 0.600000, 1.000000), # Pastel Blue
(0.800000, 0.800000, 0.200000), # Banana Yellow
(0.600000, 1.000000, 1.000000), # Ice Blue
(0.600000, 0.800000, 0.600000), # Faded Green
(0.600000, 0.400000, 1.000000), # Blue Violet
(0.800000, 1.000000, 0.400000), # Moon Green
(0.600000, 0.000000, 1.000000), # Blue Purple
(0.050980, 0.050980, 0.050980), # 95% Black
(0.101961, 0.101961, 0.101961), # 90% Black
(0.149020, 0.149020, 0.149020), # 85% Black
(0.200000, 0.200000, 0.200000), # 80% Black
(0.250980, 0.250980, 0.250980), # 75% Black
(0.301961, 0.301961, 0.301961), # 70% Black
(0.352941, 0.352941, 0.352941), # 65% Black
(0.400000, 0.400000, 0.400000), # 60% Black
(0.450980, 0.450980, 0.450980), # 55% Black
(0.501961, 0.501961, 0.501961), # 50% Black
(0.552941, 0.552941, 0.552941), # 45% Black
(0.603922, 0.603922, 0.603922), # 40% Black
(0.650980, 0.650980, 0.650980), # 35% Black
(0.701961, 0.701961, 0.701961), # 30% Black
(0.752941, 0.752941, 0.752941), # 25% Black
(0.803922, 0.803922, 0.803922), # 20% Black
(0.854902, 0.854902, 0.854902), # 15% Black
(0.901961, 0.901961, 0.901961), # 10% Black
(0.952941, 0.952941, 0.952941), #  5% Black
(1.000000, 1.000000, 1.000000)] # White

class _GeometryGL(object):

    def __init__(self, geometry, **kwargs):
        self._geometry = geometry

    @property
    def geometry(self):
        return self._geometry

    def initgl(self):
        raise NotImplementedError

    def drawgl(self):
        GL.glPushMatrix()

        GL.glRotate(math.degrees(self.geometry.tilt_rad), 1.0, 0.0, 0.0)
        GL.glRotate(math.degrees(self.geometry.rotation_rad), 0.0, 0.0, 1.0)

        self._drawgl()

        GL.glPopMatrix()

    def _drawgl(self):
        raise NotImplementedError

    def destroygl(self):
        pass

class SubstrateGL(_GeometryGL):

    def initgl(self):
        # Dimensions
        substrate_radius = 1.0

        # Colors
        color = COLORS[10] + (0.5,)

        # Objects
        self._qobj = GLU.gluNewQuadric()

        self._substrate_top = GL.glGenLists(1)
        GL.glNewList(self._substrate_top, GL.GL_COMPILE)
        GL.glColor(*color)
        GLU.gluDisk(self._qobj, 0, substrate_radius, 36, 1)
        GL.glEndList()

    def _drawgl(self):
        GL.glCallList(self._substrate_top)

    def destroygl(self):
        GLU.gluDeleteQuadric(self._qobj)

GeometryGLManager.register(Substrate, SubstrateGL)

class InclusionGL(_GeometryGL):

    def initgl(self):
        # Dimensions
        substrate_radius = 1.0
        inclusion_radius = self.geometry.inclusion_diameter_m * 1e6 / 2.0

        # Colors
        substrate_color = COLORS[10] + (0.5,)
        inclusion_color = COLORS[11] + (0.5,)

        # Objects
        self._qobj = GLU.gluNewQuadric()

        self._substrate_top = GL.glGenLists(1)
        GL.glNewList(self._substrate_top, GL.GL_COMPILE)
        GL.glColor(*substrate_color)
        GLU.gluDisk(self._qobj, inclusion_radius, substrate_radius, 36, 1)
        GL.glEndList()

        self._inclusion_top = GL.glGenLists(1)
        GL.glNewList(self._inclusion_top, GL.GL_COMPILE)
        GL.glColor(*inclusion_color)
        GLU.gluDisk(self._qobj, 0, inclusion_radius, 36, 1)
        GL.glEndList()

        self._inclusion_sphere = GL.glGenLists(1)
        GL.glNewList(self._inclusion_sphere, GL.GL_COMPILE)
        GL.glColor(*inclusion_color)
        GLU.gluSphere(self._qobj, inclusion_radius, 36, 36)
        GL.glEndList()

    def _drawgl(self):
        GL.glCallList(self._substrate_top)
        GL.glCallList(self._inclusion_top)

        GL.glClipPlane(GL.GL_CLIP_PLANE1, [0, 0, -1.0, 0.0])
        GL.glEnable(GL.GL_CLIP_PLANE1)
        GL.glCallList(self._inclusion_sphere)
        GL.glDisable(GL.GL_CLIP_PLANE1)

    def destroygl(self):
        GLU.gluDeleteQuadric(self._qobj)

GeometryGLManager.register(Inclusion, InclusionGL)

class MultiLayersGL(_GeometryGL):

    def initgl(self):
        # Dimensions
        substrate_radius = 1.0

        # Objects
        self._qobj = GLU.gluNewQuadric()
        self._disk = GL.glGenLists(1)
        GL.glNewList(self._disk, GL.GL_COMPILE)
        GLU.gluDisk(self._qobj, 0, substrate_radius, 36, 1)
        GL.glEndList()

    def _drawgl(self):
        for i, layer in enumerate(self.geometry.layers):
            color = COLORS[10 + (i % 80)] + (0.5,)
            dims = self.geometry.get_dimensions(layer)

            GL.glPushMatrix()
            GL.glTranslate(0.0, 0.0, dims.zmax_m * 1e6)
            GL.glColor(*color)
            GL.glCallList(self._disk)
            GL.glPopMatrix()

        GL.glPushMatrix()
        GL.glTranslate(0.0, 0.0, dims.zmin_m * 1e6)
        color = COLORS[10 + (i + 1 % 80)] + (0.5,)
        GL.glColor(*color)
        GL.glCallList(self._disk)
        GL.glPopMatrix()

    def destroygl(self):
        GLU.gluDeleteQuadric(self._qobj)

GeometryGLManager.register(MultiLayers, MultiLayersGL)

class GrainBoundariesGL(_GeometryGL):

    def initgl(self):
        # Dimensions
        substrate_radius = 1.0

        # Color
        color_substrate = COLORS[10] + (0.5,)

        # Objects
        self._qobj = GLU.gluNewQuadric()

        self._top = GL.glGenLists(1)
        GL.glNewList(self._top, GL.GL_COMPILE)
        GL.glColor(*color_substrate)
        GLU.gluDisk(self._qobj, 0, substrate_radius, 36, 1)
        GL.glEndList()

        self._planes = []
        self._planes.append(self._create_plane(self.geometry.left_body, substrate_radius))

        for layer in self.geometry.layers:
            self._planes.append(self._create_plane(layer, substrate_radius))

    def _create_plane(self, body, radius):
        dims = self.geometry.get_dimensions(body)
        glist = GL.glGenLists(1)

        GL.glNewList(glist, GL.GL_COMPILE)
        GL.glBegin(GL.GL_QUADS)
        GL.glNormal(1.0, 0.0, 0.0)
        GL.glVertex(dims.xmax_m * 1e6, -radius, 0.0)
        GL.glVertex(dims.xmax_m * 1e6, -radius, -radius)
        GL.glVertex(dims.xmax_m * 1e6, radius, -radius)
        GL.glVertex(dims.xmax_m * 1e6, radius, 0.0)
        GL.glEnd()
        GL.glEndList()

        return glist

    def _drawgl(self):
        GL.glCallList(self._top)

        for i, plane in enumerate(self._planes):
            color = COLORS[11 + (i % 80)] + (0.5,)
            GL.glColor(*color)
            GL.glCallList(plane)

    def destroygl(self):
        GLU.gluDeleteQuadric(self._qobj)

GeometryGLManager.register(GrainBoundaries, GrainBoundariesGL)

class SphereGL(_GeometryGL):

    def initgl(self):
        # Dimensions
        radius = self.geometry.diameter_m * 1e6 / 2.0

        # Colors
        color = COLORS[10] + (0.5,)

        # Objects
        self._qobj = GLU.gluNewQuadric()
        self._inclusion_sphere = GL.glGenLists(1)
        GL.glNewList(self._inclusion_sphere, GL.GL_COMPILE)
        GL.glColor(*color)
        GLU.gluSphere(self._qobj, radius, 36, 36)
        GL.glEndList()

    def _drawgl(self):
        GL.glPushMatrix()
        GL.glTranslate(0.0, 0.0, -self.geometry.diameter_m * 1e6 / 2.0)
        GL.glCallList(self._inclusion_sphere)
        GL.glPopMatrix()

    def destroygl(self):
        GLU.gluDeleteQuadric(self._qobj)

GeometryGLManager.register(Sphere, SphereGL)
