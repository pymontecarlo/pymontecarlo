""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.base import HDF5Handler

# Globals and constants variables.

class ModelHDF5HandlerMixin:

    GROUP_MODELS = 'models'

    def _parse_model_internal(self, group, ref_model):
        group_model = group.file[ref_model]
        return self._parse_hdf5handlers(group_model)

    def _require_models_group(self, group):
        return group.file.require_group(self.GROUP_MODELS)

    def _convert_model_internal(self, model, group):
        group_models = self._require_models_group(group)

        name = '{} [{:d}]'.format(model.__class__.__name__, id(model))
        if name in group_models:
            return group_models[name]

        group_model = group_models.create_group(name)

        self._convert_hdf5handlers(model, group_model)

        return group_model

class ModelHDF5Handler(HDF5Handler):

    ATTR_NAME = 'name'

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_NAME in group.attrs

    def parse(self, group):
        name = group.attrs[self.ATTR_NAME]
        return self.CLASS.__members__[name]

    def convert(self, model, group):
        super().convert(model, group)
        group.attrs[self.ATTR_NAME] = model.name
