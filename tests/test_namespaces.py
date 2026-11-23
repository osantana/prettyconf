import pytest

from prettyconf.configuration import Configuration
from prettyconf.exceptions import InvalidConfigurationError, UnknownConfigurationError
from prettyconf.loaders import Environment
from prettyconf.wrappers import SecretValue


def test_namespace_prefixes_the_name(monkeypatch):
    monkeypatch.setenv('AUTH0_TOKEN', 'token')
    config = Configuration()

    auth0 = config['AUTH0_']

    assert auth0('TOKEN') == 'token'


def test_namespace_takes_the_prefix_as_it_is(monkeypatch):
    monkeypatch.setenv('AUTH0TOKEN', 'glued')
    monkeypatch.setenv('AUTH0_TOKEN', 'separated')
    config = Configuration()

    assert config['AUTH0']('TOKEN') == 'glued'
    assert config['AUTH0_']('TOKEN') == 'separated'


def test_namespaces_can_be_nested(monkeypatch):
    monkeypatch.setenv('AUTH0_API_TOKEN', 'token')
    config = Configuration()

    assert config['AUTH0_']['API_']('TOKEN') == 'token'


def test_namespace_does_not_change_the_configuration_it_came_from(monkeypatch):
    monkeypatch.setenv('TOKEN', 'root')
    monkeypatch.setenv('AUTH0_TOKEN', 'namespaced')
    config = Configuration()

    auth0 = config['AUTH0_']

    assert auth0('TOKEN') == 'namespaced'
    assert config('TOKEN') == 'root'


def test_namespace_accepts_cast_default_and_wrapper(monkeypatch):
    monkeypatch.setenv('AUTH0_RETRIES', '3')
    config = Configuration()
    auth0 = config['AUTH0_']

    assert auth0('RETRIES', cast=config.int) == 3
    assert auth0('TIMEOUT', cast=config.int, default='30') == 30
    assert auth0('RETRIES', cast=config.int, wrapper=config.secret) == SecretValue(3)


def test_namespace_uses_the_loaders_of_the_configuration_it_came_from(monkeypatch):
    monkeypatch.setenv('auth0_token', 'lowercase')
    config = Configuration(loaders=[Environment(var_format=str.lower)])

    assert config['AUTH0_']('TOKEN') == 'lowercase'


def test_namespace_finds_configuration_files_next_to_the_caller(env_config):
    config = Configuration()

    assert config['ENV']('FILE') == 'Environment File Value'


def test_errors_name_the_whole_variable(monkeypatch):
    monkeypatch.setenv('AUTH0_RETRIES', 'super-secret')
    config = Configuration()
    auth0 = config['AUTH0_']

    with pytest.raises(UnknownConfigurationError, match='AUTH0_TOKEN'):
        auth0('TOKEN')

    with pytest.raises(InvalidConfigurationError, match='AUTH0_RETRIES') as error:
        auth0('RETRIES', cast=config.int)

    assert 'super-secret' not in str(error.value)
