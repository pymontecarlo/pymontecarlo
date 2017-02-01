"""
Horizontal layers sample.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from .base import _LayeredSample
from ..material import VACUUM

# Globals and constants variables.

class HorizontalLayers(_LayeredSample):

    def __init__(self, substrate_material=None, layers=None,
                 tilt_rad=0.0, rotation_rad=0.0):
        """
        Creates a multi-layers geometry.
        The layers are assumed to be in the x-y plane (normal parallel to z) at
        tilt of 0.0\u00b0.
        The first layer starts at ``z = 0`` and extends towards the negative z
        axis.

        :arg substrate_material: material of the substrate.
            If ``None``, the geometry does not have a substrate, only layers
        :arg layers: :class:`list` of :class:`.Layer`
        """
        super().__init__(layers, tilt_rad, rotation_rad)

        if substrate_material is None:
            substrate_material = VACUUM
        self.substrate_material = substrate_material

    def __repr__(self):
        if self.has_substrate():
            return '<{0:s}(substrate_material={1:s}, {2:d} layers)>' \
                .format(self.__class__.__name, self.substrate.material,
                        len(self.layers))
        else:
            return '<{0:s}(No substrate, {1:d} layers)>' \
                .format(self.__class__.__name, len(self.layers))

    def __eq__(self, other):
        return super().__eq__(other) and \
            self.substrate_material == other.substrate_material

    def has_substrate(self):
        """
        Returns ``True`` if a substrate material has been defined.
        """
        return self.substrate_material is not VACUUM

    @property
    def materials(self):
        return self._cleanup_materials(self.substrate_material,
                                       *super().materials)