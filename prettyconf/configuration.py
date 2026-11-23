import copy
import sys
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, TypeVar, overload

from .casts import (
    JSON,
    AbstractCast,
    Base64,
    Boolean,
    Eval,
    Float,
    Integer,
    List,
    Option,
    Tuple,
    warn_unless_cast,
)
from .exceptions import InvalidConfigurationError, UnknownConfigurationError
from .loaders import Environment, RecursiveSearch
from .wrappers import SecretValue

MAGIC_FRAME_DEPTH = 2

T = TypeVar('T')
D = TypeVar('D')
W = TypeVar('W')


class _NotGiven:
    def __repr__(self):
        return '<not given>'


_NOT_GIVEN = _NotGiven()


def _unchanged(value):
    return value


def _caller_path():
    # MAGIC! Get the caller's module path.
    frame = sys._getframe(MAGIC_FRAME_DEPTH)  # noqa: SLF001
    return str(Path(frame.f_code.co_filename).resolve().parent)


class Configuration:
    # Shortcut for standard casts
    boolean = Boolean()
    int = Integer()
    float = Float()
    list = List()
    tuple = Tuple()
    eval = Eval()
    json = JSON()
    base64 = Base64()  # Base64('utf-8') decodes to str instead

    # Shortcut for standard wrappers
    secret = SecretValue

    @staticmethod
    def option(options: Mapping[str, T]) -> Option[T]:
        return Option(options)

    def __init__(self, loaders=None):
        self.prefix = ''
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

    def __getitem__(self, prefix: str) -> 'Configuration':
        namespace = copy.copy(self)
        namespace.prefix = self.prefix + prefix
        return namespace

    @overload
    def __call__(self, item: str) -> str: ...

    @overload
    def __call__(self, item: str, *, default: D) -> str | D: ...

    @overload
    def __call__(self, item: str, cast: AbstractCast[T], *, default: Any = ...) -> T: ...

    @overload
    def __call__(self, item: str, cast: Callable[..., T], *, default: Any = ...) -> T: ...

    @overload
    def __call__(self, item: str, *, wrapper: type[SecretValue[Any]]) -> SecretValue[str]: ...

    @overload
    def __call__(self, item: str, *, default: D, wrapper: type[SecretValue[Any]]) -> SecretValue[str | D]: ...

    @overload
    def __call__(
        self, item: str, cast: AbstractCast[T], *, default: Any = ..., wrapper: type[SecretValue[Any]]
    ) -> SecretValue[T]: ...

    @overload
    def __call__(
        self, item: str, cast: Callable[..., T], *, default: Any = ..., wrapper: type[SecretValue[Any]]
    ) -> SecretValue[T]: ...

    @overload
    def __call__(
        self, item: str, cast: Callable[..., Any] = ..., *, default: Any = ..., wrapper: Callable[..., W]
    ) -> W: ...

    def __call__(self, item, cast=_unchanged, *, default=_NOT_GIVEN, wrapper=_unchanged):
        if not callable(cast):
            raise TypeError('Cast must be callable')

        if not callable(wrapper):
            raise TypeError('Wrapper must be callable')

        if cast is not _unchanged:
            warn_unless_cast(cast)

        item = self.prefix + item

        if self._recursive_search:
            self._recursive_search.starting_path = _caller_path()

        for loader in self.loaders:
            try:
                value = loader[item]
            except KeyError:
                continue

            return wrapper(self._cast(item, cast, value))

        if default is _NOT_GIVEN:
            raise UnknownConfigurationError(f"Configuration '{item}' not found")

        return wrapper(self._cast(item, cast, default))

    @staticmethod
    def _cast(item, cast, value):
        try:
            return cast(value)
        except InvalidConfigurationError as ex:
            raise InvalidConfigurationError(f"Configuration '{item}' is invalid: {ex}") from ex
