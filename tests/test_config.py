import inspect
import os

import pytest

from prettyconf import config as package_config
from prettyconf.configuration import Configuration
from prettyconf.exceptions import InvalidConfigurationError, UnknownConfigurationError
from prettyconf.loaders import EnvFile, Environment, IniFile


def test_basic_config(env_config, ini_config):
    os.environ['ENVVAR'] = 'Environment Variable Value'
    config = Configuration()
    assert repr(config).startswith('Configuration(loaders=[')
    assert config('ENVVAR') == 'Environment Variable Value'
    assert config('ENVFILE') == 'Environment File Value'
    assert config('INIFILE') == 'INI File Value'
    assert len(config.loaders) == 2  # Environment + RecursiveSearch
    del os.environ['ENVVAR']


def test_customized_loaders(env_config, ini_config):
    os.environ['ENVVAR'] = 'Environment Variable Value'
    os.environ['ENVVAR2'] = 'Foo'
    loaders = [EnvFile(env_config), Environment(), IniFile(ini_config)]
    config = Configuration(loaders=loaders)
    assert config('ENVVAR') == 'Must be overrided'
    assert config('ENVVAR2') == 'Foo'
    assert config('ENVFILE') == 'Environment File Value'
    assert config('INIFILE') == 'INI File Value'
    assert len(config.loaders) == 3
    del os.environ['ENVVAR']
    del os.environ['ENVVAR2']


def test_from_import_basic_config():
    assert isinstance(package_config, Configuration)


def test_config_default_values():
    config = Configuration()
    assert config('DEFAULT', default='Default Value') == 'Default Value'


def test_config_cast_value():
    os.environ['INTEGER'] = '42'
    config = Configuration()
    assert config('INTEGER', cast=int) == 42


def test_fail_invalid_cast_type():
    os.environ['INTEGER'] = '42'
    config = Configuration()
    with pytest.raises(TypeError):
        config('INTEGER', cast='not callable')


def test_fail_unknown_config_without_default_value():
    os.environ['ENVVAR'] = 'Environment Variable Value'
    config = Configuration()
    with pytest.raises(UnknownConfigurationError):
        config('UNKNOWN')


def test_none_as_default_value():
    config = Configuration()
    assert config('UNKNOWN', default=None) is None


def test_default_value_goes_through_the_cast():
    config = Configuration()
    assert config('UNKNOWN', default='yes', cast=config.boolean) is True


def test_fail_unexpected_keyword_argument():
    config = Configuration()
    with pytest.raises(TypeError):
        config('UNKNOWN', defualt='typo')


def test_missing_default_reads_well_in_the_signature():
    assert str(inspect.signature(Configuration.__call__).parameters['default'].default) == '<not given>'


def test_cast_error_names_the_configuration_without_leaking_its_value(monkeypatch):
    monkeypatch.setenv('API_KEY', 'super-secret')
    config = Configuration()

    with pytest.raises(InvalidConfigurationError) as error:
        config('API_KEY', cast=config.base64)

    assert 'API_KEY' in str(error.value)
    assert 'super-secret' not in str(error.value)


def test_cast_error_keeps_the_reason_reported_by_the_cast(monkeypatch):
    monkeypatch.setenv('DEBUG', 'perhaps')
    config = Configuration()

    with pytest.raises(InvalidConfigurationError) as error:
        config('DEBUG', cast=config.boolean)

    assert 'DEBUG' in str(error.value)
    assert 'boolean' in str(error.value)


def test_cast_error_on_the_default_value_names_the_configuration():
    config = Configuration()

    with pytest.raises(InvalidConfigurationError) as error:
        config('MISSING', default='not a boolean', cast=config.boolean)

    assert 'MISSING' in str(error.value)


def test_option_cast_shortcut():
    os.environ['ENVIRONMENT'] = 'local'
    config = Configuration()
    environments = {'production': ('spam',), 'local': ('spam', 'test')}

    assert config('ENVIRONMENT', cast=config.option(environments)) == ('spam', 'test')

    del os.environ['ENVIRONMENT']
