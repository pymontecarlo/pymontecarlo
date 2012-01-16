#!/usr/bin/env python
"""
================================================================================
:mod:`exporter` -- Exporter to PENELOPE files
================================================================================

.. module:: exporter
   :synopsis: Exporter to PENELOPE files

.. inheritance-diagram:: pymontecarlo.input.penelope.exporter

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
from itertools import tee, izip

# Third party modules.

# Local modules.
from pymontecarlo.input.base.geometry import \
    Substrate, Inclusion, MultiLayers, GrainBoundaries
from pymontecarlo.input.penelope.geometry import \
    PenelopeGeometry, Module, xplane, zplane, cylinder, sphere
from pymontecarlo.io.base.exporter import Exporter as _Exporter
from pymontecarlo.lib.penelope.wrapper import create_material

# Globals and constants variables.
from pymontecarlo.input.penelope.material import VACUUM

def _pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

class Exporter(_Exporter):

    def __init__(self, pendbase_dir):
        """
        Creates a exporter to PENELOPE.
        
        :arg pendbase_dir: location of the PENELOPE's pendbase directory.
            The directory shall contains the ``pdffiles`` folder.
        """
        _Exporter.__init__(self)

        self._geometry_exporters[Substrate] = self._export_geometry_substrate
        self._geometry_exporters[Inclusion] = self._export_geometry_inclusion
        self._geometry_exporters[MultiLayers] = self._export_geometry_multilayers
        self._geometry_exporters[GrainBoundaries] = self._export_geometry_grainboundaries

        self._pendbase_dir = pendbase_dir

    def export(self, options):
        raise NotImplementedError

    def export_geometry(self, options, dirpath):
        """
        Exports geometry to a *geo* file and all materials to *mat* files.
        
        :arg options: PENELOPE options
        
        :arg dirpath: full path to a directory where the files will be saved.
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
        title = options.geometry.__class__.__name__.lower()
        pengeom = PenelopeGeometry(title)
        pengeom.tilt = options.geometry.tilt
        pengeom.rotation = options.geometry.rotation

        self._export_geometry(options, pengeom)

        lines = pengeom.to_geo()
        geofilepath = os.path.join(dirpath, title + ".geo")
        with open(geofilepath, 'w') as f:
            for line in lines:
                f.write(line + '\n')

        # Save materials
        cwd = os.getcwd()
        os.chdir(self._pendbase_dir)

        matinfos = []
        for material in pengeom.get_materials():
            index = material._index
            if index == 0: continue

            filepath = os.path.join(dirpath, 'mat%i.mat' % index)
            create_material(material.composition, material.density,
                            material.name, filepath)

            matinfos.append((material, filepath))

        os.chdir(cwd)

        return (pengeom, geofilepath), matinfos

    def _export_geometry_substrate(self, options, geometry, pengeom):
        surface_cylinder = cylinder(0.1) # 10 cm radius
        surface_top = zplane(0.0) # z = 0
        surface_bottom = zplane(-0.1) # z = -10 cm

        module = Module.from_body(geometry.body)
        module.add_surface(surface_cylinder, -1)
        module.add_surface(surface_top, -1)
        module.add_surface(surface_bottom, 1)

        pengeom.modules.add(module)

    def _export_geometry_inclusion(self, options, geometry, pengeom):
        surface_cylinder = cylinder(0.1) # 10 cm radius
        surface_top = zplane(0.0) # z = 0
        surface_bottom = zplane(-0.1) # z = -10 cm
        surface_sphere = sphere(geometry.inclusion_diameter / 2.0)

        module_inclusion = Module.from_body(geometry.inclusion_body, 'Inclusion')
        module_inclusion.add_surface(surface_top, -1)
        module_inclusion.add_surface(surface_sphere, -1)

        module_substrate = Module.from_body(geometry.substrate_body, 'Substrate')
        module_substrate.add_surface(surface_cylinder, -1)
        module_substrate.add_surface(surface_top, -1)
        module_substrate.add_surface(surface_bottom, 1)
        module_substrate.add_module(module_inclusion)

        pengeom.modules.add(module_substrate)
        pengeom.modules.add(module_inclusion)

    def _export_geometry_multilayers(self, options, geometry, pengeom):
        # Surfaces
        surface_cylinder = cylinder(0.1) # 10 cm radius

        surface_layers = [zplane(0.0)]
        for layer in geometry.layers:
            dim = geometry.get_dimensions(layer)
            surface_layers.append(zplane(dim.zmin))

        # Modules
        tmpgrouping = []
        for i, surfaces in enumerate(_pairwise(surface_layers)):
            surface_top, surface_bottom = surfaces
            layer = geometry.layers[i]

            module = Module.from_body(layer, 'Layer %i' % (i + 1,))
            module.add_surface(surface_cylinder, -1)
            module.add_surface(surface_top, -1)
            module.add_surface(surface_bottom, 1)

            pengeom.modules.add(module)
            tmpgrouping.append((module, surface_bottom))

        if geometry.has_substrate():
            surface_top = surface_layers[-1]
            surface_bottom = zplane(surface_top.shift.z - 0.1) # 10 cm below last layer

            module = Module.from_body(geometry.substrate_body, 'Substrate')
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

        group = Module(VACUUM, 'grouping')
        group.add_surface(surface_cylinder, -1)
        group.add_surface(surface_layers[0], -1) # top z = 0.0
        group.add_surface(surface_bottom, 1)
        group.add_module(tmpgrouping[0][0]) # m0
        group.add_module(module) #m1

        pengeom.modules.add(group)

        for module, surface_bottom in tmpgrouping[2:]:
            oldgroup = group

            group = Module(VACUUM, 'grouping')
            group.add_surface(surface_cylinder, -1)
            group.add_surface(surface_layers[0], -1) # top z = 0.0
            group.add_surface(surface_bottom, 1)
            group.add_module(module)
            group.add_module(oldgroup)

            pengeom.modules.add(group)

    def _export_geometry_grainboundaries(self, options, geometry, pengeom):
        # Surfaces
        surface_top = zplane(0.0) # z = 0
        surface_bottom = zplane(-0.1) # z = -10 cm

        surface_layers = []
        for layer in geometry.layers:
            dim = geometry.get_dimensions(layer)
            surface_layers.append(xplane(dim.xmin))
        surface_layers.append(xplane(dim.xmax))

        diameter = sum(map(attrgetter('thickness'), geometry.layers))
        surface_cylinder = cylinder(0.1 + 3.0 * diameter) # 10 cm radius

        # Modules
        ## Left substrate
        module = Module.from_body(geometry.left_body, 'Left substrate')
        module.add_surface(surface_cylinder, -1)
        module.add_surface(surface_top, -1)
        module.add_surface(surface_bottom, 1)
        module.add_surface(surface_layers[0], -1)

        pengeom.modules.add(module)

        ## Layers
        for i, surfaces in enumerate(_pairwise(surface_layers)):
            surface_left, surface_right = surfaces
            layer = geometry.layers[i]

            module = Module.from_body(layer, 'Layer %i' % (i + 1,))
            module.add_surface(surface_cylinder, -1)
            module.add_surface(surface_top, -1)
            module.add_surface(surface_bottom, 1)
            module.add_surface(surface_left, 1)
            module.add_surface(surface_right, -1)

            pengeom.modules.add(module)

        ## Right substrate
        module = Module.from_body(geometry.right_body, 'Right substrate')
        module.add_surface(surface_cylinder, -1)
        module.add_surface(surface_top, -1)
        module.add_surface(surface_bottom, 1)
        module.add_surface(surface_layers[-1], 1)

        pengeom.modules.add(module)

