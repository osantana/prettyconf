import base64
import binascii
import json
from collections.abc import Mapping
from typing import Any, ClassVar, Generic, TypeVar, overload

from .exceptions import InvalidConfigurationError

T = TypeVar('T')
ContentT = TypeVar('ContentT', bytes, str)


class AbstractCast:
    def __call__(self, value):
        raise NotImplementedError  # pragma: no cover


class Boolean(AbstractCast):
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


class DelimitedSequence(AbstractCast):
    def __init__(self, delimiter=',', quotes='"\''):
        self.delimiter = delimiter
        self.quotes = quotes

    def _parse(self, string):
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

        return [e.strip() for e in elements]


class List(DelimitedSequence):
    def __call__(self, value) -> list[str]:
        return list(self._parse(value))


class Tuple(DelimitedSequence):
    def __call__(self, value) -> tuple[str, ...]:
        return tuple(self._parse(value))


class Option(AbstractCast, Generic[T]):
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


class JSON(AbstractCast):
    def __call__(self, value) -> Any:
        try:
            return json.loads(value)
        except json.JSONDecodeError as ex:
            raise InvalidConfigurationError('Value is not valid JSON') from ex
        except TypeError:
            return value


class Base64(AbstractCast, Generic[ContentT]):
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
        if isinstance(value, bytes):
            return b''.join(value.split())

        return ''.join(value.split())

    def _decode(self, value) -> Any:
        try:
            data = self._join_lines(value)
            if len(data) % 4:
                raise binascii.Error('Invalid base64 padding')
            content = base64.b64decode(data, validate=True)
        except (binascii.Error, TypeError, AttributeError) as ex:
            raise InvalidConfigurationError('Value is not a valid base64 encoded file') from ex

        if self.encoding is None:
            return content

        try:
            return content.decode(self.encoding)
        except (UnicodeDecodeError, LookupError) as ex:
            raise InvalidConfigurationError(f'Base64 encoded file is not valid {self.encoding}') from ex

    def __call__(self, value) -> ContentT:
        return self._decode(value)
