import ast
import sys
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, TypeVar, overload

from .casts import JSON, Base64, Boolean, List, Option, Tuple
from .exceptions import InvalidConfigurationError, UnknownConfigurationError
from .loaders import Environment, RecursiveSearch

MAGIC_FRAME_DEPTH = 2

T = TypeVar('T')
D = TypeVar('D')


class _NotGiven:
    def __repr__(self):
        return '<not given>'


_NOT_GIVEN = _NotGiven()


def _caller_path():
    # MAGIC! Get the caller's module path.
    # noinspection PyProtectedMember
    frame = sys._getframe(MAGIC_FRAME_DEPTH)  # noqa: SLF001
    return str(Path(frame.f_code.co_filename).resolve().parent)


class Configuration:
    # Shortcut for standard casts
    boolean = Boolean()
    list = List()
    tuple = Tuple()
    eval = staticmethod(ast.literal_eval)
    json = JSON()
    base64 = Base64()  # Base64('utf-8') decodes to str instead

    @staticmethod
    def option(options: Mapping[str, T]) -> Option[T]:
        return Option(options)

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
        loaders = ', '.join([repr(loader) for loader in self.loaders])
        return f'{self.__class__.__name__}(loaders=[{loaders}])'

    @overload
    def __call__(self, item: str) -> str: ...

    @overload
    def __call__(self, item: str, *, default: D) -> str | D: ...

    @overload
    def __call__(self, item: str, cast: Callable[..., T]) -> T: ...

    @overload
    def __call__(self, item: str, cast: Callable[..., T], *, default: Any) -> T: ...

    def __call__(self, item, cast=lambda v: v, *, default=_NOT_GIVEN):
        if not callable(cast):
            raise TypeError('Cast must be callable')

        if self._recursive_search:
            self._recursive_search.starting_path = _caller_path()

        for loader in self.loaders:
            try:
                value = loader[item]
            except KeyError:
                continue

            return self._cast(item, cast, value)

        if default is _NOT_GIVEN:
            raise UnknownConfigurationError(f"Configuration '{item}' not found")

        return self._cast(item, cast, default)

    @staticmethod
    def _cast(item, cast, value):
        try:
            return cast(value)
        except InvalidConfigurationError as ex:
            raise InvalidConfigurationError(f"Configuration '{item}' is invalid: {ex}") from ex
