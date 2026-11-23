from pathlib import Path

from typing_extensions import assert_type

from prettyconf import config
from prettyconf.casts import AbstractCast, Base64, List
from prettyconf.wrappers import SecretValue


def _without_cast(fallback: int) -> None:
    assert_type(config('NAME'), str)
    assert_type(config('NAME', default=None), str | None)
    assert_type(config('PORT', default=fallback), str | int)


def _with_builtin_casts() -> None:
    assert_type(config('DEBUG', cast=config.boolean), bool)
    assert_type(config('DEBUG', default=False, cast=config.boolean), bool)
    assert_type(config('HOSTS', cast=config.list), list[str])
    assert_type(config('HOSTS', cast=config.tuple), tuple[str, ...])
    assert_type(config('CREDENTIALS', cast=config.base64), bytes)
    assert_type(config('CREDENTIALS', cast=Base64('utf-8')), str)
    assert_type(config('PORT', cast=config.int), int)
    assert_type(config('PORT', config.int), int)
    assert_type(config('PORTS', cast=config.list[config.int]), list[int])
    assert_type(config('FLAGS', cast=config.tuple[config.boolean]), tuple[bool, ...])
    assert_type(config('HOSTS', cast=List(delimiter=';')), list[str])


class _Upper(AbstractCast[str]):
    def __call__(self, value) -> str:
        return value.upper()


def _with_custom_casts() -> None:
    assert_type(config('NAME', cast=_Upper()), str)
    assert_type(config('NAMES', cast=config.list[_Upper()]), list[str])
    assert_type(config('NAME', cast=_Upper(), wrapper=config.secret), SecretValue[str])


def _with_callable_casts() -> None:
    assert_type(config('PORT', cast=int), int)
    assert_type(config('NUMBERS', cast=lambda value: [int(v) for v in value.split(';')]), list[int])


def _with_wrappers() -> None:
    assert_type(config('API_KEY', wrapper=config.secret), SecretValue[str])
    assert_type(config('API_KEY', default=None, wrapper=config.secret), SecretValue[str | None])
    assert_type(config('CREDENTIALS', cast=config.base64, wrapper=config.secret), SecretValue[bytes])
    assert_type(config('DEBUG', config.boolean, wrapper=config.secret), SecretValue[bool])
    assert_type(config('DEBUG', cast=config.boolean, default=False, wrapper=config.secret), SecretValue[bool])
    assert_type(config('DEBUG', cast=config.boolean, wrapper=SecretValue), SecretValue[bool])
    assert_type(config('DEBUG', cast=config.boolean, wrapper=config.secret).reveal(), bool)
    assert_type(config('PORTS', cast=config.list[config.int], wrapper=config.secret), SecretValue[list[int]])
    assert_type(config('DATA_DIR', wrapper=Path), Path)


def _with_namespaces() -> None:
    auth0 = config['AUTH0_']

    assert_type(auth0('DOMAIN'), str)
    assert_type(auth0('RETRIES', cast=config.int), int)
    assert_type(auth0('TOKEN', wrapper=config.secret), SecretValue[str])
    assert_type(config['AUTH0_']['API_']('RETRIES', cast=config.int), int)


def _with_option_cast() -> None:
    environments = {
        'production': ('spam', 'eggs'),
        'local': ('spam', 'eggs', 'test'),
    }
    assert_type(config('ENVIRONMENT', default='production', cast=config.option(environments)), tuple[str, ...])
