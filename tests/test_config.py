import os

import pytest

from prettyconf.configuration import Configuration
from prettyconf.exceptions import InvalidConfigurationCast, UnknownConfiguration


def test_basic_config(config_files):
    os.environ["ENVVAR"] = "Environment Variable Value"
    config = Configuration()
    assert config("ENVVAR") == "Environment Variable Value"
    assert config("ENVFILE") == "Environment File Value"
    assert config("INIFILE") == "INI File Value"
    assert len(config.configurations) == 3  # envvar + .env + settings.ini


def test_basic_config_with_starting_path(config_files):
    os.environ["ENVVAR"] = "Environment Variable Value"
    starting_path = os.path.dirname(__file__)
    config = Configuration(starting_path=starting_path)
    assert config("ENVVAR") == "Environment Variable Value"
    assert config("ENVFILE") == "Environment File Value"
    assert config("INIFILE") == "INI File Value"
    assert len(config.configurations) == 3  # envvar + .env + settings.ini


def test_from_import_basic_config(config_files):
    from prettyconf import config
    os.environ["ENVVAR"] = "Environment Variable Value"
    assert config("ENVVAR") == "Environment Variable Value"
    assert config("ENVFILE") == "Environment File Value"
    assert config("INIFILE") == "INI File Value"
    assert len(config.configurations) == 3  # envvar + .env + settings.ini


def test_config_default_values():
    config = Configuration()
    assert config("DEFAULT", default="Default Value") == "Default Value"


def test_config_cast_value():
    os.environ["INTEGER"] = "42"
    config = Configuration()
    assert config("INTEGER", cast=int) == 42


def test_fail_invalid_cast_type():
    os.environ["INTEGER"] = "42"
    config = Configuration()
    with pytest.raises(InvalidConfigurationCast):
        config("INTEGER", cast="not callable")


def test_fail_unknown_config_without_default_value():
    os.environ["ENVVAR"] = "Environment Variable Value"
    config = Configuration()
    with pytest.raises(UnknownConfiguration):
        config("UNKNOWN")


def test_none_as_default_value():
    config = Configuration()
    assert config("UNKNOWN", default=None) is None
