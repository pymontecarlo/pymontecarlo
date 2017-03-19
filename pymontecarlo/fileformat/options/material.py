""""""

# Standard library modules.

# Third party modules.
import numpy as np

# Local modules.
from pymontecarlo.fileformat.base import HDF5Handler
from pymontecarlo.options.material import Material

# Globals and constants variables.

class MaterialHDF5Handler(HDF5Handler):

    ATTR_NAME = 'name'
    DATASET_ATOMIC_NUMBER = 'atomic_number'
    DATASET_WEIGHT_FRACTION = 'weight_fraction'
    ATTR_DENSITY = 'density_kg_per_m3'

    def _parse_name(self, group):
        return str(group.attrs[self.ATTR_NAME])

    def _parse_composition(self, group):
        zs = group[self.DATASET_ATOMIC_NUMBER]
        wfs = group[self.DATASET_WEIGHT_FRACTION]
        return dict((int(z), float(wf)) for z, wf in zip(zs, wfs))

    def _parse_density_kg_per_m3(self, group):
        return float(group.attrs[self.ATTR_DENSITY])

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_NAME in group.attrs and \
            self.DATASET_ATOMIC_NUMBER in group and \
            self.DATASET_WEIGHT_FRACTION in group and \
            self.ATTR_DENSITY in group.attrs

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

    def convert(self, material, group):
        super().convert(material, group)
        self._convert_name(material, group)
        self._convert_composition(material, group)
        self._convert_density_kg_per_m3(material, group)

    @property
    def CLASS(self):
        return Material
