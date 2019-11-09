""""""

# Standard library modules.
import abc
import enum

# Third party modules.
import h5py
import pyxray

# Local modules.
from pymontecarlo.exceptions import ParseError, ConvertError
from pymontecarlo.util.xrayline import convert_xrayline

# Globals and constants variables.


class EntityBase(metaclass=abc.ABCMeta):

    _subclasses = []

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._subclasses.append(cls)


class EntityHDF5Mixin(metaclass=abc.ABCMeta):

    ATTR_CLASS = "_class"
    ATTR_VERSION = "_version"

    VERSION = 1

    @classmethod
    def can_parse_hdf5(cls, group):
        return (
            group.attrs.get(cls.ATTR_CLASS) == cls.__name__
            and group.attrs.get(cls.ATTR_VERSION) == cls.VERSION
        )

    @classmethod
    @abc.abstractmethod
    def parse_hdf5(cls, group):
        raise NotImplementedError

    @classmethod
    def _parse_hdf5(cls, group, attr_name, type_=None):
        if attr_name not in group.attrs:
            raise ParseError("Group {!r} has no attribute {}".format(group, attr_name))

        attr_value = group.attrs[attr_name]
        if isinstance(attr_value, h5py.Reference):
            return cls._parse_hdf5_reference(group, attr_value)

        elif issubclass(type_, enum.Enum):
            if attr_value not in type_.__members__:
                raise ParseError(
                    "Value for attribute {} ({}) does not exist in enum {}".format(
                        attr_name, attr_value, type_
                    )
                )
            return type_.__members__[attr_value]

        elif type_ == pyxray.XrayLine:
            return convert_xrayline(attr_value.split(maxsplit=1))

        elif type_ == str:
            return attr_value

        elif type_ is not None:
            return type_(attr_value)

        else:
            return attr_value

    @classmethod
    def _parse_hdf5_reference(cls, group, reference):
        group_obj = group.file[reference]
        return cls._parse_hdf5_object(group_obj)

    @classmethod
    def _parse_hdf5_object(cls, group):
        for subclass in cls._subclasses:
            if subclass.can_parse_hdf5(group):
                return subclass.parse_hdf5(group)

        raise ParseError("No handler found for {}".format(group))

    @abc.abstractmethod
    def convert_hdf5(self, group):
        self._convert_hdf5(group, self.ATTR_CLASS, self.__class__.__name__)
        self._convert_hdf5(group, self.ATTR_VERSION, self.VERSION)

    def _convert_hdf5(self, group, attr_name, obj):
        if isinstance(obj, (int, float)):
            attr_value = obj

        elif isinstance(obj, str):
            attr_value = str(obj)

        elif isinstance(obj, enum.Enum):
            attr_value = str(obj.name)

        elif issubclass(obj.__class__, tuple(self._subclasses)):
            attr_value = self._convert_hdf5_reference(group, obj)

        elif isinstance(obj, pyxray.XrayLine):
            attr_value = obj.iupac

        else:
            raise ConvertError(
                "No handler found for object {!r} and group {!r}".format(obj, group)
            )

        group.attrs[attr_name] = attr_value

    def _convert_hdf5_reference(self, group, obj):
        group_option = group.file.require_group("_option")

        name = "{} [{:d}]".format(obj.__class__.__name__, id(obj))
        group_obj = group_option.get(name)
        if group_obj is None:
            group_obj = group_option.create_group(name)
            obj.convert_hdf5(group_obj)

        return group_obj.ref


class EntryHDF5IOMixin(EntityHDF5Mixin):
    @classmethod
    def read(cls, filepath):
        with h5py.File(filepath, "r") as f:
            if not cls.can_parse_hdf5(f):
                raise IOError("Cannot open file")
            return cls.parse_hdf5(f)

    def write(self, filepath):
        with h5py.File(filepath, "w") as f:
            self.convert_hdf5(f)


class EntitySeriesMixin(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def convert_series(self, builder):
        pass


class EntityDocumentMixin(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def convert_document(self, builder):
        pass
