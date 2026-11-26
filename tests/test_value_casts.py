import datetime
import decimal
import enum
import pathlib

import pytest

from prettyconf import config
from prettyconf.casts import URL, AbstractCast, Decimal, Enum, Float, Integer, Path, Timedelta
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


@pytest.mark.parametrize(
    ('value', 'result'),
    [
        ('30', datetime.timedelta(seconds=30)),
        ('1.5', datetime.timedelta(seconds=1.5)),
        (30, datetime.timedelta(seconds=30)),
        ('500ms', datetime.timedelta(milliseconds=500)),
        ('30s', datetime.timedelta(seconds=30)),
        ('5m', datetime.timedelta(minutes=5)),
        ('2h', datetime.timedelta(hours=2)),
        ('7d', datetime.timedelta(days=7)),
        ('1.5h', datetime.timedelta(minutes=90)),
        ('1h30m', datetime.timedelta(minutes=90)),
        ('1d2h3m4s5ms', datetime.timedelta(days=1, hours=2, minutes=3, seconds=4, milliseconds=5)),
        (' 30s ', datetime.timedelta(seconds=30)),
        (datetime.timedelta(minutes=5), datetime.timedelta(minutes=5)),
    ],
)
def test_timedelta_cast(value, result):
    assert Timedelta()(value) == result


@pytest.mark.parametrize(
    'value',
    ['super-secret', '', '5 m', '5x', 'm5', '-5s', '1e3', 'nan', 'inf', '5M', '1h 30m', None, '9' * 400 + 'd'],
)
def test_fail_invalid_timedelta_without_leaking_the_value(value):
    with pytest.raises(InvalidConfigurationError) as error:
        Timedelta()(value)

    assert 'super-secret' not in str(error.value)


def test_url_cast():
    url = URL()('postgres://user:password@db.example.com:5432/app?sslmode=require')

    assert url.scheme == 'postgres'
    assert url.hostname == 'db.example.com'
    assert url.port == 5432
    assert url.username == 'user'
    assert url.password == 'password'  # noqa: S105
    assert url.path == '/app'
    assert url.query == 'sslmode=require'


@pytest.mark.parametrize(
    ('value', 'scheme', 'hostname', 'path'),
    [
        ('https://example.com', 'https', 'example.com', ''),
        ('HTTP://example.com/', 'http', 'example.com', '/'),
        ('sqlite:///db.sqlite3', 'sqlite', None, '/db.sqlite3'),
        ('redis://localhost:6379/0', 'redis', 'localhost', '/0'),
    ],
)
def test_url_cast_accepts(value, scheme, hostname, path):
    url = URL()(value)

    assert (url.scheme, url.hostname, url.path) == (scheme, hostname, path)


@pytest.mark.parametrize(
    'value',
    [
        'super-secret',
        'localhost:8000',
        'example.com/path',
        '/just/a/path',
        'http://',
        'mailto:someone@example.com',
        'http://example.com:port',
        'http://[broken',
        '',
        None,
        b'http://example.com',
    ],
)
def test_fail_invalid_url_without_leaking_the_value(value):
    with pytest.raises(InvalidConfigurationError) as error:
        URL()(value)

    assert 'super-secret' not in str(error.value)


@pytest.mark.parametrize(
    ('cast', 'value', 'result'),
    [
        (Integer(minimum=1, maximum=65535), '1', 1),
        (Integer(minimum=1, maximum=65535), '65535', 65535),
        (Integer(minimum=0), 0, 0),
        (Integer(maximum=0), '-7', -7),
        (Float(minimum=0, maximum=1), '0.5', 0.5),
        (Decimal(minimum=decimal.Decimal('0.01')), '0.01', decimal.Decimal('0.01')),
        (Timedelta(minimum=datetime.timedelta(seconds=1)), '1s', datetime.timedelta(seconds=1)),
        (Timedelta(maximum=datetime.timedelta(hours=1)), 30, datetime.timedelta(seconds=30)),
    ],
)
def test_casts_accept_values_inside_their_limits(cast, value, result):
    assert cast(value) == result


@pytest.mark.parametrize(
    ('cast', 'value', 'reason'),
    [
        (Integer(minimum=1, maximum=65535), '0', 'at least 1'),
        (Integer(minimum=1, maximum=65535), '65536', 'at most 65535'),
        (Integer(minimum=0), '-1', 'at least 0'),
        (Integer(maximum=0), 1, 'at most 0'),
        (Float(minimum=0, maximum=1), '1.5', 'at most 1'),
        (Float(minimum=0), 'nan', 'at least 0'),
        (Decimal(minimum=decimal.Decimal('0.01')), '0.001', 'at least 0.01'),
        (Decimal(minimum=0), 'NaN', 'not a valid decimal'),
        (Timedelta(minimum=datetime.timedelta(seconds=1)), '500ms', 'at least 0:00:01'),
        (Timedelta(maximum=datetime.timedelta(hours=1)), '2h', 'at most 1:00:00'),
        (Timedelta(maximum=datetime.timedelta(hours=1)), datetime.timedelta(hours=2), 'at most 1:00:00'),
    ],
)
def test_casts_reject_values_outside_their_limits_without_leaking_them(cast, value, reason):
    with pytest.raises(InvalidConfigurationError, match=reason) as error:
        cast(value)

    assert str(value) not in str(error.value).replace(reason, '')


def test_limits_of_a_cast_apply_to_the_default_and_name_the_configuration(monkeypatch):
    monkeypatch.setenv('PORT', '70000')
    port = Integer(minimum=1, maximum=65535)

    with pytest.raises(InvalidConfigurationError, match="'PORT' is invalid: Value must be at most 65535"):
        config('PORT', cast=port)

    with pytest.raises(InvalidConfigurationError, match="'MISSING_PORT' is invalid: Value must be at least 1"):
        config('MISSING_PORT', default=0, cast=port)


def test_limits_of_a_cast_apply_to_the_elements_of_a_list():
    ports = config.list[Integer(minimum=1, maximum=65535)]

    assert ports('80, 443') == [80, 443]
    with pytest.raises(InvalidConfigurationError, match='at most 65535'):
        ports('80, 70000')


def test_timedelta_and_url_shortcuts(monkeypatch):
    monkeypatch.setenv('TIMEOUT', '1m30s')
    monkeypatch.setenv('API_URL', 'https://api.example.com/v1')

    assert config('TIMEOUT', cast=config.timedelta) == datetime.timedelta(seconds=90)
    assert config('TIMEOUT', default=30, cast=config.timedelta) == datetime.timedelta(seconds=90)
    assert config('MISSING', default=30, cast=config.timedelta) == datetime.timedelta(seconds=30)
    assert config('API_URL', cast=config.url).hostname == 'api.example.com'
    assert isinstance(config.timedelta, AbstractCast)
    assert isinstance(config.url, AbstractCast)
