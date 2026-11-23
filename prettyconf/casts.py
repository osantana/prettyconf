import ast
import base64
import binascii
import json
import warnings
from collections.abc import Callable, Mapping
from typing import Any, ClassVar, Generic, TypeVar, overload

from .exceptions import InvalidConfigurationError

T = TypeVar('T')
U = TypeVar('U')
ContentT = TypeVar('ContentT', bytes, str)

# TODO: remove in the next major release, together with warn_unless_cast, when
# a cast that is not an AbstractCast instance stops being accepted.
NATIVE_TYPE_REPLACEMENTS = (
    (bool, 'config.boolean'),
    (int, 'config.int'),
    (float, 'config.float'),
    (list, 'config.list'),
    (tuple, 'config.tuple'),
    (dict, 'config.json'),
)


class AbstractCast(Generic[T]):
    def __call__(self, value) -> T:
        raise NotImplementedError  # pragma: no cover


def warn_unless_cast(cast, stacklevel=3):
    if isinstance(cast, AbstractCast):
        return

    replacement = 'a subclass of prettyconf.casts.AbstractCast'
    for native_type, shortcut in NATIVE_TYPE_REPLACEMENTS:
        if cast is native_type:
            replacement = shortcut

    warnings.warn(
        f'Passing {cast!r} as a cast is deprecated and will stop working in a future release. '
        f'Use {replacement} instead.',
        DeprecationWarning,
        stacklevel=stacklevel,
    )


class Integer(AbstractCast[int]):
    def __call__(self, value) -> int:
        try:
            return int(value)
        except (TypeError, ValueError) as ex:
            raise InvalidConfigurationError('Value is not a valid integer') from ex


class Float(AbstractCast[float]):
    def __call__(self, value) -> float:
        try:
            return float(value)
        except (TypeError, ValueError) as ex:
            raise InvalidConfigurationError('Value is not a valid float') from ex


class Eval(AbstractCast[Any]):
    def __call__(self, value) -> Any:
        try:
            return ast.literal_eval(value)
        except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError) as ex:
            raise InvalidConfigurationError('Value is not a valid Python literal') from ex


class Boolean(AbstractCast[bool]):
    default_values: ClassVar[dict[str, bool]] = {
        '1': True,
        'true': True,
        'yes': True,
        'y': True,
        'on': True,
        't': True,
        '0': False,
        'false': False,
        'no': False,
        'n': False,
        'off': False,
        'f': False,
    }

    def __init__(self, values=None):
        self.values = dict(self.default_values)
        if isinstance(values, dict):
            self.values.update(values)

    def __call__(self, value) -> bool:
        try:
            return self.values[str(value).lower()]
        except KeyError as ex:
            raise InvalidConfigurationError('Value is not a valid boolean') from ex


class DelimitedSequence(AbstractCast[T]):
    def __init__(self, delimiter=',', quotes='"\''):
        self.delimiter = delimiter
        self.quotes = quotes
        self.cast: Callable[..., Any] = str

    def _parse(self, string) -> list[Any]:
        elements = []
        element = []
        quote = ''
        for char in string:
            # open quote
            if char in self.quotes and not quote:
                quote = char
                element.append(char)
                continue

            # close quote
            if char in self.quotes and char == quote:
                quote = ''
                element.append(char)
                continue

            if quote:
                element.append(char)
                continue

            if char == self.delimiter:
                elements.append(''.join(element))
                element = []
                continue

            element.append(char)

        # remaining element
        if element:
            elements.append(''.join(element))

        return [self.cast(e.strip()) for e in elements]


class ListOf(DelimitedSequence[list[U]]):
    def __init__(self, cast: AbstractCast[U], delimiter=',', quotes='"\''):
        super().__init__(delimiter, quotes)
        self.cast = cast

    def __call__(self, value) -> list[U]:
        return list(self._parse(value))


class List(DelimitedSequence[list[str]]):
    def __getitem__(self, cast: AbstractCast[U]) -> ListOf[U]:
        warn_unless_cast(cast)
        return ListOf(cast, self.delimiter, self.quotes)

    def __call__(self, value) -> list[str]:
        return list(self._parse(value))


class TupleOf(DelimitedSequence[tuple[U, ...]]):
    def __init__(self, cast: AbstractCast[U], delimiter=',', quotes='"\''):
        super().__init__(delimiter, quotes)
        self.cast = cast

    def __call__(self, value) -> tuple[U, ...]:
        return tuple(self._parse(value))


class Tuple(DelimitedSequence[tuple[str, ...]]):
    def __getitem__(self, cast: AbstractCast[U]) -> TupleOf[U]:
        warn_unless_cast(cast)
        return TupleOf(cast, self.delimiter, self.quotes)

    def __call__(self, value) -> tuple[str, ...]:
        return tuple(self._parse(value))


class Option(AbstractCast[T]):
    """
    Example::
        _INSTALLED_APPS = ("foo", "bar")
        INSTALLED_APPS = config("ENVIRONMENT", default="production", cast=Option({
            "production": _INSTALLED_APPS,
            "local": _INSTALLED_APPS + ("baz",)
        }))
    """

    def __init__(self, options: Mapping[str, T]):
        self.options = options

    def __call__(self, value) -> T:
        try:
            return self.options[value]
        except KeyError as ex:
            choices = ', '.join(repr(option) for option in self.options)
            raise InvalidConfigurationError(f'Value is not one of the valid options: {choices}') from ex


class JSON(AbstractCast[Any]):
    def __call__(self, value) -> Any:
        try:
            return json.loads(value)
        except json.JSONDecodeError as ex:
            raise InvalidConfigurationError('Value is not valid JSON') from ex
        except TypeError:
            return value


class Base64(AbstractCast[ContentT]):
    @overload
    def __init__(self: 'Base64[bytes]', encoding: None = None) -> None: ...

    @overload
    def __init__(self: 'Base64[str]', encoding: str) -> None: ...

    def __init__(self, encoding=None):
        self.encoding = encoding

    def __repr__(self):
        return f'Base64(encoding={self.encoding!r})'

    @staticmethod
    def _join_lines(value):
        if isinstance(value, str):
            value = value.encode('ascii')

        return b''.join(value.split())

    def _decode(self, value) -> Any:
        try:
            data = self._join_lines(value)
            content = base64.b64decode(data, validate=True)
        except (binascii.Error, TypeError, AttributeError, UnicodeEncodeError) as ex:
            raise InvalidConfigurationError('Value is not a valid base64 encoded file') from ex

        if base64.b64encode(content) != data:
            raise InvalidConfigurationError('Value is not canonically encoded base64')

        if self.encoding is None:
            return content

        try:
            return content.decode(self.encoding)
        except (UnicodeDecodeError, LookupError) as ex:
            raise InvalidConfigurationError(f'Base64 encoded file is not valid {self.encoding}') from ex

    def __call__(self, value) -> ContentT:
        return self._decode(value)
