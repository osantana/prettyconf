import ast
import os
import sys

from .casts import Boolean, List, Option, Tuple
from .exceptions import UnknownConfiguration
from .loaders import Environment, RecursiveSearch, NOT_SET

MAGIC_FRAME_DEPTH = 2


def _caller_path():
    # MAGIC! Get the caller's module path.
    # noinspection PyProtectedMember
    frame = sys._getframe(MAGIC_FRAME_DEPTH)
    path = os.path.dirname(os.path.abspath(frame.f_code.co_filename))
    return path


def identity(val):
    """Default noop cast"""
    return val


class Configuration(object):
    # Shortcut for standard casts
    boolean = Boolean()
    list = List()
    tuple = Tuple()
    option = Option
    eval = staticmethod(ast.literal_eval)

    def __init__(self, loaders=None):
        self._recursive_search = None
        if loaders is None:
            self._recursive_search = RecursiveSearch()
            loaders = [
                Environment(),
                self._recursive_search,
            ]

        self.loaders = loaders

    def __repr__(self):
        loaders = ', '.join([repr(l) for l in self.loaders])
        return 'Configuration(loaders=[{}])'.format(loaders)

    def __call__(self, item, default=NOT_SET, cast=None):
        # Look for a sensible default cast if one is not provided
        if callable(cast):
            cast = cast
        elif callable(default) or default is NOT_SET:
            cast = identity
        elif isinstance(default, bool):
            cast = self.boolean
        elif cast is None:
            cast = type(default)
        else:
            raise TypeError("Cast must be callable")

        if self._recursive_search:
            self._recursive_search.starting_path = _caller_path()

        for loader in self.loaders:
            try:
                return cast(loader[item])
            except KeyError:
                continue

        if default is NOT_SET:
            raise UnknownConfiguration("Configuration '{}' not found".format(item))

        if callable(default):
            default = default()

        return cast(default)
