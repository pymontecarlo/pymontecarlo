#!/usr/bin/env python
"""
================================================================================
:mod:`exporter` -- Base exporter for all PENELOPE main programs
================================================================================

.. module:: exporter
   :synopsis: Base exporter for all PENELOPE main programs

.. inheritance-diagram:: pymontecarlo.program._penelope.options.exporter

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
from operator import attrgetter
import itertools

# Third party modules.
import numpy as np

# Local modules.
from pymontecarlo.options.geometry import \
    Substrate, Inclusion, HorizontalLayers, VerticalLayers, Sphere #, Cuboids2D
from pymontecarlo.options.material import VACUUM

from pymontecarlo.program._penelope.options.geometry import \
    PenelopeGeometry, Module, xplane, yplane, zplane, cylinder, sphere

from pymontecarlo.program.exporter import \
    Exporter as _Exporter, ExporterException, ExporterWarning #@UnusedImport

import penelopelib.material as penmaterial

# Globals and constants variables.
from pymontecarlo.options.particle import ELECTRON, PHOTON, POSITRON

def _pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

class Keyword(object):

    LINE_KEYWORDS_SIZE = 6
    LINE_SIZE = 80

    def __init__(self, name, comment=""):
        self._name = name
        self._comment = comment

    @property
    def name(self):
        return self._name

    @property
    def comment(self):
        return self._comment

    def __call__(self, text=''):
        """
        Creates an input line of this keyword from the specified text.
        The white space between the items is automatically adjusted to fit the
        line size.
        The keyword and the total length of the line is checked not to exceed
        their respective maximum size.

        :arg text: value of the keyword
        """
        keyword = self.name.ljust(self.LINE_KEYWORDS_SIZE)
        assert len(keyword) == self.LINE_KEYWORDS_SIZE

        # Convert list to a single string
        if isinstance(text, (tuple, list)):
            text = ' '.join(map(str, text))

        line = "%s %s" % (keyword.upper(), text)
        if len(self.comment) > 0:
            line = line.ljust(self.LINE_SIZE - (len(self.comment) + 2))
            line += '[%s]' % self.comment

        assert len(line) <= self.LINE_SIZE

        return line

class Comment(Keyword):

    def __init__(self, comment):
        Keyword.__init__(self, ' ' * self.LINE_KEYWORDS_SIZE, comment)

    def __call__(self, text=''):
        text = text or self.comment

        line = "%s %s" % (self.name, text)

        assert len(line) <= self.LINE_SIZE

        return line

class Exporter(_Exporter):

    def __init__(self, pendbase_dir):
        """
        Creates a exporter to PENELOPE main programs.
        """
        _Exporter.__init__(self)

        self._geometry_exporters[Substrate] = self._export_geometry_substrate
        self._geometry_exporters[Inclusion] = self._export_geometry_inclusion
        self._geometry_exporters[HorizontalLayers] = self._export_geometry_horizontal_layers
        self._geometry_exporters[VerticalLayers] = self._export_geometry_vertical_layers
        self._geometry_exporters[Sphere] = self._export_geometry_sphere
#        self._geometry_exporters[Cuboids2D] = self._export_geometry_cuboids2d

        self._pendbase_dir = pendbase_dir

    def _export(self, options, outputdir, *args):
        # Export geometry
        geoinfo, matinfos = self.export_geometry(options.geometry, outputdir)

        # Create input file
        filepath = self._create_input_file(options, outputdir, geoinfo, matinfos)

        return filepath

    def _create_input_file(self, options, outputdir, geoinfo, matinfos, *args):
        """
        Creates .in file for the specific PENELOPE main program.

        :arg options: options to be exported
        :arg outputdir: output directory where to save the .in file
        :arg geoinfo: class:`tuple` containing :class:`PenelopeGeometry`
            object used to create the *geo* file and the full path of this
            *geo* file.
        :arg matinfos: :class:`list` of :class:`tuple` where each :class:`tuple`
            contains :class:`PenelopeMaterial` object and its associated *mat*
            filepath. The order of the materials is the same as they appear in
            the geometry file.

        :return: path to the .in file
        """
        raise NotImplementedError

    def _append_material_data(self, lines, options, geoinfo, matinfos, *args):
        lines.append(self._COMMENT_MATERIALDATA())

        for material, matfilepath in matinfos:
            text = os.path.basename(matfilepath)
            line = self._KEYWORD_MFNAME(text)
            lines.append(line)

            text = [material.absorption_energy_eV[ELECTRON],
                    material.absorption_energy_eV[PHOTON],
                    material.absorption_energy_eV[POSITRON],
                    material.elastic_scattering[0],
                    material.elastic_scattering[1],
                    material.cutoff_energy_inelastic_eV,
                    material.cutoff_energy_bremsstrahlung_eV]
            line = self._KEYWORD_MSIMPA(text)
            lines.append(line)

        lines.append(self._COMMENT_SKIP())

    def _append_geometry(self, lines, options, geoinfo, matinfos, *args):
        lines.append(self._COMMENT_GEOMETRY())

        pengeom, geofilepath = geoinfo

        text = os.path.basename(geofilepath)
        line = self._KEYWORD_GEOMFN(text)
        lines.append(line)

        bodies = sorted(pengeom.get_bodies(), key=attrgetter('_index'))
        for body in bodies:
            if body.material is VACUUM:
                continue
            text = [body._index + 1,
                    body.material.maximum_step_length_m * 1e2]
            line = self._KEYWORD_DSMAX(text)
            lines.append(line)

        lines.append(self._COMMENT_SKIP())

    def export_geometry(self, geometry, outputdir):
        """
        Exports geometry to a *geo* file and all materials to *mat* files.

        :arg geometry: :geometry object

        :arg outputdir: full path to a directory where the files will be saved.
            Note that any conflicting files will be overwritten without warnings.

        :return: a :class:`tuple` and a list of :class:`tuple`.
            The class:`tuple` contains 2 items: the :class:`PenelopeGeometry`
            object used to create the *geo* file and the full path of this
            *geo* file.
            Each :class:`tuple` in the list contains 2 items: the
            :class:`PenelopeMaterial` object and its associated *mat* filepath.
            The order of the materials is the same as they appear in the
            geometry file.
            In other words, the first material has an index of 1 in the
            geometry file.
        """
        # Save geometry
        title = geometry.__class__.__name__.lower()
        pengeom = PenelopeGeometry(title)
        pengeom.tilt_rad = geometry.tilt_rad
        pengeom.rotation_rad = geometry.rotation_rad

        self._export_geometry(geometry, pengeom)

        lines = pengeom.to_geo()
        geofilepath = os.path.join(outputdir, title + ".geo")
        with open(geofilepath, 'w') as f:
            for line in lines:
                f.write(line + '\n')

        # Save materials
        matinfos = []
        for material in pengeom.get_materials():
            if material is VACUUM: continue
            index = material._index

            filepath = os.path.join(outputdir, 'mat%i.mat' % index)

            penmaterial.create(material.name, dict(material.composition),
                               material.density_kg_m3, filepath,
                               self._pendbase_dir)

            matinfos.append((material, filepath))

        return (pengeom, geofilepath), matinfos

    def _export_geometry(self, geometry, *args):
        clasz = geometry.__class__
        method = self._geometry_exporters.get(clasz)

        if method:
            method(geometry, *args)
        else:
            raise ExporterException("Could not export geometry '%s'" % clasz.__name__)

    def _export_geometry_substrate(self, geometry, pengeom):
        surface_cylinder = cylinder(0.1) # 10 cm radius
        surface_top = zplane(0.0) # z = 0
        surface_bottom = zplane(-0.1) # z = -10 cm

        module = Module(pengeom, geometry.body.material, 'Substrate')
        module.add_surface(surface_cylinder, -1)
        module.add_surface(surface_top, -1)
        module.add_surface(surface_bottom, 1)

        pengeom.modules.add(module)

    def _export_geometry_inclusion(self, geometry, pengeom):
        surface_cylinder = cylinder(0.1) # 10 cm radius
        surface_top = zplane(0.0) # z = 0
        surface_bottom = zplane(-0.1) # z = -10 cm
        surface_sphere = sphere(geometry.inclusion.diameter_m / 2.0)

        module_inclusion = Module(pengeom, geometry.inclusion.material, 'Inclusion')
        module_inclusion.add_surface(surface_top, -1)
        module_inclusion.add_surface(surface_sphere, -1)

        module_substrate = Module(pengeom, geometry.substrate.material, 'Substrate')
        module_substrate.add_surface(surface_cylinder, -1)
        module_substrate.add_surface(surface_top, -1)
        module_substrate.add_surface(surface_bottom, 1)
        module_substrate.add_module(module_inclusion)

        pengeom.modules.add(module_substrate)
        pengeom.modules.add(module_inclusion)

    def _export_geometry_horizontal_layers(self, geometry, pengeom):
        layers = np.array(geometry.layers, ndmin=1)

        # Surfaces
        surface_cylinder = cylinder(0.1) # 10 cm radius

        surface_layers = [zplane(0.0)]
        for layer in layers:
            surface_layers.append(zplane(layer.zmin_m))

        # Modules
        tmpgrouping = []
        for i, surfaces in enumerate(_pairwise(surface_layers)):
            surface_top, surface_bottom = surfaces

            module = Module(pengeom, layers[i].material, 'Layer %i' % (i + 1,))
            module.add_surface(surface_cylinder, -1)
            module.add_surface(surface_top, -1)
            module.add_surface(surface_bottom, 1)

            pengeom.modules.add(module)
            tmpgrouping.append((module, surface_bottom))

        if geometry.has_substrate():
            surface_top = surface_layers[-1]
            surface_bottom = zplane(surface_top.shift.z_m - 0.1) # 10 cm below last layer

            module = Module(pengeom, geometry.substrate.material, 'Substrate')
            module.add_surface(surface_cylinder, -1)
            module.add_surface(surface_top, -1)
            module.add_surface(surface_bottom, 1)

            pengeom.modules.add(module)
            tmpgrouping.append((module, surface_bottom))

        # Grouping
        # G0: s0, s2, m0, m1
        # G1: s0, s3, m2, g0
        # G2: s0, s4, m3, g1
        # etc.

        if len(tmpgrouping) <= 2: # no grouping required if only 2 modules
            return

        module, surface_bottom = tmpgrouping[1]

        group = Module(pengeom, VACUUM, 'grouping')
        group.add_surface(surface_cylinder, -1)
        group.add_surface(surface_layers[0], -1) # top z = 0.0
        group.add_surface(surface_bottom, 1)
        group.add_module(tmpgrouping[0][0]) # m0
        group.add_module(module) #m1

        pengeom.modules.add(group)

        for module, surface_bottom in tmpgrouping[2:]:
            oldgroup = group

            group = Module(pengeom, VACUUM, 'grouping')
            group.add_surface(surface_cylinder, -1)
            group.add_surface(surface_layers[0], -1) # top z = 0.0
            group.add_surface(surface_bottom, 1)
            group.add_module(module)
            group.add_module(oldgroup)

            pengeom.modules.add(group)

    def _export_geometry_vertical_layers(self, geometry, pengeom):
        layers = np.array(geometry.layers, ndmin=1)

        # Surfaces
        surface_top = zplane(0.0) # z = 0
        surface_bottom = zplane(-0.1) # z = -10 cm

        surface_layers = []
        for layer in layers:
            surface_layers.append(xplane(layer.xmin_m))
        surface_layers.append(xplane(layer.xmax_m))

        diameter_m = sum(map(attrgetter('thickness_m'), layers))
        surface_cylinder = cylinder(0.1 + 3.0 * diameter_m) # 10 cm radius

        # Modules
        ## Left substrate
        module = Module(pengeom, geometry.left_substrate.material, 'Left substrate')
        module.add_surface(surface_cylinder, -1)
        module.add_surface(surface_top, -1)
        module.add_surface(surface_bottom, 1)
        module.add_surface(surface_layers[0], -1)

        pengeom.modules.add(module)

        ## Layers
        for i, surfaces in enumerate(_pairwise(surface_layers)):
            surface_left, surface_right = surfaces

            module = Module(pengeom, layers[i].material, 'Layer %i' % (i + 1,))
            module.add_surface(surface_cylinder, -1)
            module.add_surface(surface_top, -1)
            module.add_surface(surface_bottom, 1)
            module.add_surface(surface_left, 1)
            module.add_surface(surface_right, -1)

            pengeom.modules.add(module)

        ## Right substrate
        module = Module(pengeom, geometry.right_substrate.material, 'Right substrate')
        module.add_surface(surface_cylinder, -1)
        module.add_surface(surface_top, -1)
        module.add_surface(surface_bottom, 1)
        module.add_surface(surface_layers[-1], 1)

        pengeom.modules.add(module)

    def _export_geometry_sphere(self, geometry, pengeom):
        radius_m = geometry.body.diameter_m / 2.0
        surface_sphere = sphere(radius_m)

        module = Module(pengeom, geometry.body.material, 'Sphere')
        module.add_surface(surface_sphere, -1)
        module.shift.z_m = -radius_m
        pengeom.modules.add(module)

    def _export_geometry_cuboids2d(self, geometry, pengeom):
        # Surfaces
        surface_top = zplane(0.0) # z = 0
        surface_bottom = zplane(-0.1) # z = -10 cm

        ## Vertical planes
        nx = geometry.nx
        ny = geometry.ny

        xsurfaces = {}
        for x in range(-(nx / 2), nx / 2 + 1):
            xsurfaces[x] = xplane(geometry.body[x, 0].xmin_m)
        xsurfaces[x + 1] = xplane(geometry.body[x, 0].xmax_m)

        ysurfaces = {}
        for y in range(-(ny / 2), ny / 2 + 1):
            ysurfaces[y] = yplane(geometry.body[0, y].ymin_m)
        ysurfaces[y + 1] = yplane(geometry.body[0, y].ymax_m)

        # Modules
        for position, body in geometry.get_bodies.items():
            x, y = position

            module = Module(pengeom, body.material,
                            description='Position (%i, %i)' % position)

            module.add_surface(surface_bottom, 1) # zmin
            module.add_surface(surface_top, -1) # zmax
            module.add_surface(xsurfaces[x], 1) # xmin
            module.add_surface(xsurfaces[x + 1], -1) # xmax
            module.add_surface(ysurfaces[y], 1) # ymin
            module.add_surface(ysurfaces[y + 1], -1) # ymax

            pengeom.modules.add(module)

