""""""

# Standard library modules.
import abc
import os

# Third party modules.

# Local modules.

# Globals and constants variables.

def FileType(path):
    if path is None:
        return path
    if not os.path.isfile(path):
        raise ValueError('Not a file')
    return os.path.abspath(path)

def DirectoryType(path):
    if path is None:
        return path
    if not os.path.isdir(path):
        raise ValueError('Not a directory')
    return os.path.abspath(path)

class Configurator:

    @abc.abstractmethod
    def prepare_parser(self, parser, program=None):
        pass

    @abc.abstractmethod
    def create_program(self, namespace, clasz):
        return clasz()

    @abc.abstractproperty
    def fullname(self):
        raise NotImplementedError
