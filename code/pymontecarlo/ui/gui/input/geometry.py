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
from pymontecarlo.util.manager import ClassManager

# Globals and constants variables.
from pymontecarlo.ui.gui.color import COLORS

GeometryGLManager = ClassManager()

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
