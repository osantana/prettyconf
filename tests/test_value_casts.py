import decimal
import enum
import pathlib

import pytest

from prettyconf import config
from prettyconf.casts import AbstractCast, Decimal, Enum, Path
from prettyconf.exceptions import InvalidConfigurationError


class LogLevel(enum.Enum):
    DEBUG = 'debug'
    INFO = 'info'


class Priority(enum.IntEnum):
    LOW = 1
    HIGH = 2


def test_path_cast():
    assert Path()('/var/data') == pathlib.Path('/var/data')
    assert Path()(pathlib.Path('/var/data')) == pathlib.Path('/var/data')


def test_fail_invalid_path():
    with pytest.raises(InvalidConfigurationError):
        Path()(None)


@pytest.mark.parametrize(
    ('value', 'result'),
    [
        ('19.90', decimal.Decimal('19.90')),
        ('1e3', decimal.Decimal(1000)),
        (7, decimal.Decimal(7)),
    ],
)
def test_decimal_cast(value, result):
    assert Decimal()(value) == result


def test_decimal_cast_keeps_the_precision_of_the_text():
    assert str(Decimal()('0.10')) == '0.10'


@pytest.mark.parametrize('value', ['super-secret', '', None, [1]])
def test_fail_invalid_decimal_without_leaking_the_value(value):
    with pytest.raises(InvalidConfigurationError) as error:
        Decimal()(value)

    assert 'super-secret' not in str(error.value)


def test_enum_cast_accepts_the_name_of_a_member():
    assert Enum(LogLevel)('DEBUG') is LogLevel.DEBUG


def test_enum_cast_accepts_the_value_of_a_member():
    assert Enum(LogLevel)('info') is LogLevel.INFO


def test_enum_cast_accepts_a_member():
    assert Enum(LogLevel)(LogLevel.INFO) is LogLevel.INFO


def test_enum_cast_with_values_that_are_not_text():
    assert Enum(Priority)('HIGH') is Priority.HIGH
    assert Enum(Priority)(2) is Priority.HIGH


@pytest.mark.parametrize('value', ['super-secret', 'Debug', None, ['DEBUG']])
def test_fail_invalid_enum_listing_the_valid_names(value):
    with pytest.raises(InvalidConfigurationError) as error:
        Enum(LogLevel)(value)

    assert 'DEBUG, INFO' in str(error.value)
    assert 'super-secret' not in str(error.value)


def test_value_cast_shortcuts(monkeypatch):
    monkeypatch.setenv('DATA_DIR', '/var/data')
    monkeypatch.setenv('PRICE', '19.90')
    monkeypatch.setenv('LOG_LEVEL', 'debug')

    assert config('DATA_DIR', cast=config.path) == pathlib.Path('/var/data')
    assert config('PRICE', cast=config.decimal) == decimal.Decimal('19.90')
    assert config('LOG_LEVEL', cast=config.enum(LogLevel)) is LogLevel.DEBUG


def test_value_cast_shortcuts_are_casts():
    assert isinstance(config.path, AbstractCast)
    assert isinstance(config.decimal, AbstractCast)
    assert isinstance(config.enum(LogLevel), AbstractCast)


def test_enum_cast_error_names_the_configuration(monkeypatch):
    monkeypatch.setenv('LOG_LEVEL', 'verbose')

    with pytest.raises(InvalidConfigurationError, match='LOG_LEVEL') as error:
        config('LOG_LEVEL', cast=config.enum(LogLevel))

    assert 'verbose' not in str(error.value)
