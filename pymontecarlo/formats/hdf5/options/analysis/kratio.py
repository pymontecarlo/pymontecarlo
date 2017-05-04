""""""

# Standard library modules.

# Third party modules.
import numpy as np

import h5py

# Local modules.
from pymontecarlo.formats.hdf5.options.analysis.photon import PhotonAnalysisHDF5Handler
from pymontecarlo.formats.hdf5.options.material import MaterialHDF5HandlerMixin
from pymontecarlo.options.analysis.kratio import KRatioAnalysis

# Globals and constants variables.

class KRatioAnalysisHDF5Handler(PhotonAnalysisHDF5Handler, MaterialHDF5HandlerMixin):

    DATASET_ATOMIC_NUMBER = 'atomic number'
    DATASET_STANDARDS = 'standards'

    def _parse_standard_materials(self, group):
        ds_z = group[self.DATASET_ATOMIC_NUMBER]
        ds_standard = group[self.DATASET_STANDARDS]
        return dict((z, self._parse_material_internal(group, ref_material))
                    for z, ref_material in zip(ds_z, ds_standard))

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.DATASET_ATOMIC_NUMBER in group and \
            self.DATASET_STANDARDS in group

    def parse(self, group):
        photon_detector = self._parse_photon_detector(group)
        standard_materials = self._parse_standard_materials(group)
        return self.CLASS(photon_detector, standard_materials)

    def _convert_standard_materials(self, standard_materials, group):
        shape = (len(standard_materials),)
        ref_dtype = h5py.special_dtype(ref=h5py.Reference)
        ds_z = group.create_dataset(self.DATASET_ATOMIC_NUMBER, shape=shape, dtype=np.byte)
        ds_standard = group.create_dataset(self.DATASET_STANDARDS, shape=shape, dtype=ref_dtype)

        ds_standard.dims.create_scale(ds_z)
        ds_standard.dims[0].attach_scale(ds_z)

        for i, (z, material) in enumerate(standard_materials.items()):
            group_material = self._convert_material_internal(material, group)
            ds_z[i] = z
            ds_standard[i] = group_material.ref

    def convert(self, analysis, group):
        super().convert(analysis, group)
        self._convert_standard_materials(analysis.standard_materials, group)

    @property
    def CLASS(self):
        return KRatioAnalysis
