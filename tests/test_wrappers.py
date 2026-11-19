import base64
import json
from pathlib import Path

import pytest

from prettyconf.configuration import Configuration
from prettyconf.exceptions import InvalidConfigurationError
from prettyconf.wrappers import SecretValue


def test_secret_value_hides_the_value_until_revealed():
    secret = SecretValue('sk-live-123')

    assert secret.reveal() == 'sk-live-123'
    assert 'sk-live-123' not in repr(secret)
    assert 'sk-live-123' not in str(secret)
    assert 'sk-live-123' not in f'{secret}'


def test_secret_value_fails_loudly_instead_of_leaking():
    secret = SecretValue('sk-live-123')

    with pytest.raises(TypeError):
        json.dumps({'key': secret})

    with pytest.raises(TypeError):
        secret + '!'


def test_secret_value_never_equals_the_plain_value():
    wrapped = SecretValue('sk-live-123')

    assert wrapped != 'sk-live-123'
    assert wrapped == SecretValue('sk-live-123')
    assert wrapped != SecretValue('other')
    assert hash(wrapped) == hash(SecretValue('sk-live-123'))


def test_secret_value_truthiness_follows_the_value():
    assert SecretValue('sk-live-123')
    assert not SecretValue('')


def test_wrapper_receives_the_value(monkeypatch):
    monkeypatch.setenv('API_KEY', 'sk-live-123')
    config = Configuration()

    secret = config('API_KEY', wrapper=config.secret)

    assert isinstance(secret, SecretValue)
    assert secret.reveal() == 'sk-live-123'


def test_wrapper_runs_after_the_cast(monkeypatch):
    monkeypatch.setenv('CREDENTIALS', base64.b64encode(b'private key').decode())
    monkeypatch.setenv('PIN', '1234')
    monkeypatch.setenv('DEBUG', 'yes')
    config = Configuration()

    assert config('CREDENTIALS', cast=config.base64, wrapper=config.secret).reveal() == b'private key'
    assert config('PIN', cast=config.int, wrapper=config.secret).reveal() == 1234
    assert config('DEBUG', config.boolean, wrapper=config.secret).reveal() is True


def test_wrapper_also_wraps_the_default_value():
    config = Configuration()

    secret = config('MISSING', default='fallback', wrapper=config.secret)

    assert secret.reveal() == 'fallback'


def test_wrapper_can_be_any_callable(monkeypatch):
    monkeypatch.setenv('DATA_DIR', '/var/data')
    config = Configuration()

    assert config('DATA_DIR', wrapper=Path) == Path('/var/data')


def test_wrapper_does_not_hide_the_error_of_the_cast(monkeypatch):
    monkeypatch.setenv('CREDENTIALS', 'super-secret!')
    config = Configuration()

    with pytest.raises(InvalidConfigurationError) as error:
        config('CREDENTIALS', cast=config.base64, wrapper=config.secret)

    assert 'CREDENTIALS' in str(error.value)
    assert 'super-secret' not in str(error.value)


def test_fail_invalid_wrapper_type(monkeypatch):
    monkeypatch.setenv('API_KEY', 'sk-live-123')
    config = Configuration()

    with pytest.raises(TypeError):
        config('API_KEY', wrapper='not callable')
