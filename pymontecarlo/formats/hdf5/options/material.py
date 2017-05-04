""""""

# Standard library modules.

# Third party modules.
import numpy as np

import matplotlib.colors

# Local modules.
from pymontecarlo.formats.hdf5.base import HDF5Handler
from pymontecarlo.options.material import Material, VACUUM

# Globals and constants variables.

class MaterialHDF5HandlerMixin:

    GROUP_MATERIALS = 'materials'

    def _parse_material_internal(self, group, ref_material):
        group_material = group.file[ref_material]
        return self._parse_hdf5handlers(group_material)

    def _require_materials_group(self, group):
        return group.file.require_group(self.GROUP_MATERIALS)

    def _convert_material_internal(self, material, group):
        group_materials = self._require_materials_group(group)

        name = '{} [{:d}]'.format(material.name, id(material))
        if name in group_materials:
            return group_materials[name]

        group_material = group_materials.create_group(name)

        self._convert_hdf5handlers(material, group_material)

        return group_material

class MaterialHDF5Handler(HDF5Handler):

    ATTR_NAME = 'name'
    DATASET_ATOMIC_NUMBER = 'atomic number'
    DATASET_WEIGHT_FRACTION = 'weight fraction'
    ATTR_DENSITY = 'density (kg/m3)'
    ATTR_COLOR = 'color'

    def _parse_name(self, group):
        return str(group.attrs[self.ATTR_NAME])

    def _parse_composition(self, group):
        zs = group[self.DATASET_ATOMIC_NUMBER]
        wfs = group[self.DATASET_WEIGHT_FRACTION]
        return dict((int(z), float(wf)) for z, wf in zip(zs, wfs))

    def _parse_density_kg_per_m3(self, group):
        return float(group.attrs[self.ATTR_DENSITY])

    def _parse_color(self, group):
        return tuple(group.attrs[self.ATTR_COLOR])

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_NAME in group.attrs and \
            self.DATASET_ATOMIC_NUMBER in group and \
            self.DATASET_WEIGHT_FRACTION in group and \
            self.ATTR_DENSITY in group.attrs and \
            self.ATTR_COLOR in group.attrs

    def parse(self, group):
        name = self._parse_name(group)
        composition = self._parse_composition(group)
        density_kg_per_m3 = self._parse_density_kg_per_m3(group)
        return self.CLASS(name, composition, density_kg_per_m3)

    def _convert_name(self, material, group):
        group.attrs[self.ATTR_NAME] = material.name

    def _convert_composition(self, material, group):
        zs = sorted(material.composition.keys())
        ds_z = group.create_dataset(self.DATASET_ATOMIC_NUMBER, data=zs, dtype=np.int)

        wfs = [material.composition[z] for z in zs]
        ds_wf = group.create_dataset(self.DATASET_WEIGHT_FRACTION, data=wfs)

        ds_wf.dims.create_scale(ds_z)
        ds_wf.dims[0].attach_scale(ds_z)

    def _convert_density_kg_per_m3(self, material, group):
        group.attrs[self.ATTR_DENSITY] = material.density_kg_per_m3

    def _convert_color(self, material, group):
        rgba = matplotlib.colors.to_rgba(material.color)
        group.attrs[self.ATTR_COLOR] = rgba

    def convert(self, material, group):
        super().convert(material, group)
        self._convert_name(material, group)
        self._convert_composition(material, group)
        self._convert_density_kg_per_m3(material, group)
        self._convert_color(material, group)

    @property
    def CLASS(self):
        return Material

class VacuumHDF5Handler(HDF5Handler):

    def parse(self, group):
        return VACUUM

    def convert(self, vacuum, group):
        super().convert(vacuum, group)

    @property
    def CLASS(self):
        return type(VACUUM)
