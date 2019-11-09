"""
Base program
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
import pymontecarlo.options.base as base

# Globals and constants variables.


class ProgramBase(base.OptionBase):
    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return "<{classname}({name})>".format(
            classname=self.__class__.__name__, name=self.name
        )

    def __eq__(self, other):
        return super().__eq__(other) and base.isclose(self.name, other.name)

    @property
    def name(self):
        return self._name

    @abc.abstractproperty
    def expander(self):
        raise NotImplementedError

    @abc.abstractproperty
    def exporter(self):
        raise NotImplementedError

    @abc.abstractproperty
    def worker(self):
        raise NotImplementedError

    @abc.abstractproperty
    def importer(self):
        raise NotImplementedError

    # region Series

    def convert_series(self, builder):
        super().convert_series(builder)
        builder.add_column("program", "prog", self.name)

    # endregion

    # region Document

    DESCRIPTION_PROGRAM = "program"

    def convert_document(self, builder):
        super().convert_document(builder)

        builder.add_title(self.name)


# endregion


class ProgramBuilderBase(base.OptionBuilderBase):
    pass
