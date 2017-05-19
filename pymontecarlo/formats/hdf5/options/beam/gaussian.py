""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.options.beam.cylindrical import \
    CylindricalBeamHDF5Handler
from pymontecarlo.options.beam.gaussian import GaussianBeam

# Globals and constants variables.

class GaussianBeamHDF5Handler(CylindricalBeamHDF5Handler):

    @property
    def CLASS(self):
        return GaussianBeam
