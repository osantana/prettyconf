from typing_extensions import assert_type

from prettyconf import config
from prettyconf.casts import Base64


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


def _with_callable_casts() -> None:
    assert_type(config('PORT', cast=int), int)
    assert_type(config('NUMBERS', cast=lambda value: [int(v) for v in value.split(';')]), list[int])


def _with_option_cast() -> None:
    environments = {
        'production': ('spam', 'eggs'),
        'local': ('spam', 'eggs', 'test'),
    }
    assert_type(config('ENVIRONMENT', default='production', cast=config.option(environments)), tuple[str, ...])
