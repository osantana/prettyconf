# coding: utf-8


import ast
import os
import sys

from .casts import Boolean, List, Option, Tuple
from .exceptions import UnknownConfiguration
from .loaders import Environment, RecursiveSearch

MAGIC_FRAME_DEPTH = 2


def _caller_path():
    # MAGIC! Get the caller's module path.
    # noinspection PyProtectedMember
    frame = sys._getframe(MAGIC_FRAME_DEPTH)
    path = os.path.dirname(frame.f_code.co_filename)
    return path


class Configuration(object):
    # Shortcut for standard casts
    boolean = Boolean()
    list = List()
    tuple = Tuple()
    option = Option
    eval = staticmethod(ast.literal_eval)

    def __init__(self, loaders=None):
        if loaders is None:
            loaders = [
                Environment(),
                RecursiveSearch(starting_path=_caller_path())
            ]
        self.loaders = loaders

    def __call__(self, item, cast=lambda v: v, **kwargs):
        if not callable(cast):
            raise TypeError("Cast must be callable")

        for loader in self.loaders:
            try:
                return cast(loader[item])
            except KeyError:
                continue

        if 'default' not in kwargs:
            raise UnknownConfiguration("Configuration '{}' not found".format(item))

        return cast(kwargs["default"])
