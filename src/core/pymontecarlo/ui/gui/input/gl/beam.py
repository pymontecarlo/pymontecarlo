#!/usr/bin/env python
"""
================================================================================
:mod:`beam` -- Draw beam in OpenGL
================================================================================

.. module:: beam
   :synopsis: Draw beam in OpenGL

.. inheritance-diagram:: pymontecarlo.ui.gui.input.gl.beam

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.
from OpenGL import GL
from OpenGL import GLU

# Local modules.
from pymontecarlo.input.beam import PencilBeam, GaussianBeam
from pymontecarlo.util.manager import ClassManager

# Globals and constants variables.

BeamGLManager = ClassManager()

class _BeamGL(object):

    def __init__(self, beam, **kwargs):
        self._beam = beam

    @property
    def beam(self):
        return self._beam

    def initgl(self):
        raise NotImplementedError

    def drawgl(self):
        origin = self.beam.origin_m
        x = origin[0] * 1e6
        y = origin[1] * 1e6

        GL.glPushMatrix()
        GL.glTranslate(x, y, 0.0)
        #TODO: Update direction of beam
        self._drawgl()
        GL.glPopMatrix()

    def _drawgl(self):
        raise NotImplementedError

    def destroygl(self):
        pass

class PencilBeamGL(_BeamGL):

    def initgl(self):
        self._list = GL.glGenLists(1)
        GL.glNewList(self._list, GL.GL_COMPILE)
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)

        GL.glColor(0.0, 0.0, 1.0, 0.5) # semi-transparent blue
        GL.glLineWidth(2)

        vertices = [0, 0, 0.5, 0, 0, 0]
        GL.glVertexPointer(3, GL.GL_FLOAT, 0, vertices)
        GL.glDrawArrays(GL.GL_LINE_STRIP, 0, len(vertices) / 3)

        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEndList()

    def _drawgl(self):
        GL.glCallList(self._list)

BeamGLManager.register(PencilBeam, PencilBeamGL)

class GaussianBeamGL(_BeamGL):

    def initgl(self):
        radius = self.beam.diameter_m * 1e6 / 2.0
        z = self.beam.origin_m[2] * 1e6

        self._qobj = GLU.gluNewQuadric()
        self._cylinder = GL.glGenLists(1)
        GL.glNewList(self._cylinder, GL.GL_COMPILE)
        GL.glColor(0.0, 0.0, 1.0, 0.5) # semi-transparent blue
        GLU.gluCylinder(self._qobj, radius, radius, z, 36, 1)
        GL.glEndList()

    def _drawgl(self):
        GL.glCallList(self._cylinder)

    def destroygl(self):
        GLU.gluDeleteQuadric(self._qobj)

BeamGLManager.register(GaussianBeam, GaussianBeamGL)
