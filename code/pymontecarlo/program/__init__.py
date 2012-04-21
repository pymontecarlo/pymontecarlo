# This is required to create a namespace package.
# A namespace package allows programs to be located in different directories or
# eggs.
#
# See http://stackoverflow.com/questions/1675734/how-do-i-create-a-namespace-package-in-python
# or http://docs.python.org/library/pkgutil.html#pkgutil.extend_path
# for more information

from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)
