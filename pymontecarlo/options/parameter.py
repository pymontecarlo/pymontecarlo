"""
"""

# Standard library modules.
import enum
import abc
from collections import defaultdict

# Third party modules.
import pyxray

# Local modules.
from pymontecarlo.options.composition import process_wildcard
from pymontecarlo.exceptions import ParameterError

# Globals and constants variables.


class ParameterType(enum.Enum):
    FIXED = "fixed"
    UNKNOWN = "unknown"
    DIFFERENCE = "difference"


class ParameterBase(metaclass=abc.ABCMeta):
    def __init__(self, name, minimum_value=float("-inf"), maximum_value=float("inf")):
        self._name = name
        self.type_ = ParameterType.FIXED
        self.minimum_value = minimum_value
        self.maximum_value = maximum_value

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.name}, {self.type_.value})>"

    @abc.abstractmethod
    def get_value(self, options):
        raise NotImplementedError

    @abc.abstractmethod
    def set_value(self, options, value):
        if self.type_ == ParameterType.FIXED:
            raise ValueError(
                f'Parameter "{self.name}" is not UNKNOWN. It cannot be changed'
            )

    def validate(self, options):
        return []

    @property
    def name(self):
        return self._name


class SimpleParameter(ParameterBase):
    def __init__(
        self,
        name,
        getter,
        setter,
        minimum_value=float("-inf"),
        maximum_value=float("inf"),
    ):
        super().__init__(name, minimum_value=minimum_value, maximum_value=maximum_value)
        self._getter = getter
        self._setter = setter

    def get_value(self, options):
        return self._getter(options)

    def set_value(self, options, value):
        super().set_value(options, value)

        if self.type_ == ParameterType.DIFFERENCE:
            raise ValueError(f'Parameter "{self.name}" does not support DIFFERENCE')

        value = max(self.minimum_value, min(value, self.maximum_value))
        self._setter(options, value)


class MaterialParameterGroup:
    def __init__(self):
        self.parameters = []

    def register(self, parameter):
        self.parameters.append(parameter)

    def validate(self, parameter):
        parameter_count = len(self.parameters)
        parameter_types = defaultdict(list)
        for p in self.parameters:
            parameter_types.setdefault(p.type_, []).append(p.atomic_number)

        # Cannot be all unknowns or difference
        if parameter_count == len(parameter_types[ParameterType.UNKNOWN]):
            return [ParameterError("All concentrations are set to UNKNOWN")]

        if parameter_count == len(parameter_types[ParameterType.DIFFERENCE]):
            return [ParameterError("All concentrations are set to DIFFERENCE")]

        # If one unknown parameter, at least one difference
        if (
            len(parameter_types[ParameterType.UNKNOWN]) > 0
            and len(parameter_types[ParameterType.DIFFERENCE]) == 0
        ):
            unknowns = parameter_types[ParameterType.UNKNOWN]
            unknowns_str = ", ".join(map(pyxray.element_symbol, unknowns))
            if len(unknowns) == 1:
                error = ParameterError(
                    f"Concentration {unknowns_str} is UNKNOWN, at least one other concentration must be DIFFERENCE"
                )
            else:
                error = ParameterError(
                    f"Concentrations {unknowns_str} are UNKNOWN, at least one other concentration must be DIFFERENCE"
                )

            return [error]

        # If one difference parameter, at least one unknown
        if (
            len(parameter_types[ParameterType.DIFFERENCE]) > 0
            and len(parameter_types[ParameterType.UNKNOWN]) == 0
        ):
            differences = parameter_types[ParameterType.DIFFERENCE]
            differences_str = ", ".join(map(pyxray.element_symbol, differences))
            if len(differences) == 1:
                error = ParameterError(
                    f"Concentration {differences_str} is DIFFERENCE, at least one other concentration must be UNKNOWN"
                )
            else:
                error = ParameterError(
                    f"Concentrations {differences_str} are DIFFERENCE, at least one other concentration must be UNKNOWN"
                )

            return [error]

        return []

    def update(self, material):
        for parameter in self.parameters:
            if parameter.type_ != ParameterType.DIFFERENCE:
                continue

            material.composition[parameter.atomic_number] = "?"

        material.composition = process_wildcard(material.composition)


class ConcentrationParameter(ParameterBase):
    def __init__(self, parameter_group, material_getter, material_name, atomic_number):
        super().__init__(
            name=f"Material {material_name} - {pyxray.element_symbol(atomic_number)}",
            minimum_value=0.0,
            maximum_value=1.0,
        )

        parameter_group.register(self)

        self._parameter_group = parameter_group
        self._material_getter = material_getter
        self._atomic_number = atomic_number

    def get_value(self, options):
        material = self._material_getter(options)
        return material.composition.get(self._atomic_number)

    def set_value(self, options, value):
        super().set_value(options, value)

        if self.type_ == ParameterType.UNKNOWN:
            material = self._material_getter(options)

            value = max(self.minimum_value, min(value, self.maximum_value))
            material.composition[self._atomic_number] = value

            self._parameter_group.update(material)

    def validate(self, options):
        errors = super().validate(options)
        errors += self._parameter_group.validate(self)
        return errors

    @property
    def atomic_number(self):
        return self._atomic_number
