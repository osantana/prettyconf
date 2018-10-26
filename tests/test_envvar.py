import os

import pytest

from prettyconf.loaders import EnvVarConfigurationLoader


def test_basic_config():
    os.environ["TEST"] = "test"
    config = EnvVarConfigurationLoader()

    assert "TEST" in config
    assert "test" == config["TEST"]

    del os.environ["TEST"]


def test_fail_missing_config():
    config = EnvVarConfigurationLoader()

    assert "UNKNOWN" not in config
    with pytest.raises(KeyError):
        _ = config["UNKNOWN"]
