from typing import Generic, TypeVar

T = TypeVar('T')


class SecretValue(Generic[T]):
    __slots__ = ('_value',)

    def __init__(self, value: T):
        self._value = value

    def __repr__(self):
        return 'SecretValue(***)'

    def __str__(self):
        return '***'

    def __bool__(self):
        return bool(self._value)

    def __eq__(self, other):
        if isinstance(other, SecretValue):
            return self._value == other._value

        return NotImplemented

    def __hash__(self):
        return hash(self._value)

    def reveal(self) -> T:
        return self._value
