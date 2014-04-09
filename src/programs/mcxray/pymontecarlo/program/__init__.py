# This is required to create a namespace package.
# A namespace package allows programs to be located in different directories or
# eggs.

__import__('pkg_resources').declare_namespace(__name__)