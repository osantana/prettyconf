# coding: utf-8
import ast
import os
import sys

from .casts import Boolean, List, Option, Tuple
from .exceptions import UnknownConfiguration
from .loaders import EnvFile, Environment


MAGIC_FRAME_DEPTH = 2


class Configuration(object):
    # Shortcut for standard casts
    boolean = Boolean()
    list = List()
    tuple = Tuple()
    option = Option
    eval = staticmethod(ast.literal_eval)

    def __init__(self, strategies=None):
        if strategies is None:
            dot_env_file = '{path}.env'.format(path=self._caller_path())
            print(self._caller_path())
            strategies = [Environment(), EnvFile(filename=dot_env_file)]
        self.strategies = strategies

    @staticmethod
    def _caller_path():
        # MAGIC! Get the caller's module path.
        # noinspection PyProtectedMember
        frame = sys._getframe(MAGIC_FRAME_DEPTH)
        path = os.path.dirname(frame.f_code.co_filename)
        return path

    def __call__(self, item, cast=lambda v: v, **kwargs):
        if not callable(cast):
            raise InvalidConfigurationCast("Cast must be callable")

        for loader in self.strategies:
            try:
                return cast(loader[item])
            except KeyError:
                continue

        if 'default' not in kwargs:
            raise UnknownConfiguration("Configuration '{}' not found".format(item))

        return cast(kwargs["default"])
