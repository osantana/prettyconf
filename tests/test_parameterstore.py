import importlib
import sys
from unittest import mock

import pytest
from botocore.exceptions import BotoCoreError

from prettyconf.loaders import AwsParameterStore


PARAMETER_RESPONSE = {
    "Parameters": [
        {
            "Name": "DEBUG",
            "Type": "String",
            "Value": "false",
        },
        {
            "Name": "HOST",
            "Type": "String",
            "Value": "host_url",
        },
    ],
}

PARAMETER_RESPONSE_FIRST_PAGE = {
    "Parameters": [
        {
            "Name": "/api/DEBUG",
            "Type": "String",
            "Value": "false",
        },
    ],
    "NextToken": "token",
}

PARAMETER_RESPONSE_LAST_PAGE = {
    "Parameters": [
        {
            "Name": "/api/HOST",
            "Type": "String",
            "Value": "host_url",
        },
    ],
}


@pytest.fixture
def boto_not_installed():
    sys.modules['boto3'] = None
    importlib.reload(sys.modules['prettyconf.loaders'])
    yield
    sys.modules.pop('boto3')
    importlib.reload(sys.modules['prettyconf.loaders'])


def test_create_loader_boto_not_installed(boto_not_installed):
    with pytest.raises(RuntimeError):
        AwsParameterStore()


@mock.patch("prettyconf.loaders.boto3")
def test_basic_config(mock_boto):
    mock_boto.client.return_value.get_parameters_by_path.return_value = PARAMETER_RESPONSE
    config = AwsParameterStore()

    assert "HOST" in config
    assert config["HOST"] == "host_url"
    assert repr(config).startswith("AwsParameterStore(path=")
    mock_boto.client.return_value.get_parameters_by_path.assert_called_with(Path="/")


@mock.patch("prettyconf.loaders.boto3")
def test_basic_config_response_paginated(mock_boto):
    mock_boto.client.return_value.get_parameters_by_path.side_effect = [
        PARAMETER_RESPONSE_FIRST_PAGE, PARAMETER_RESPONSE_LAST_PAGE,
    ]
    config = AwsParameterStore(path="/api")

    assert "HOST" in config
    assert "DEBUG" in config
    assert config["HOST"] == "host_url"
    assert config["DEBUG"] == "false"
    assert mock_boto.client.return_value.get_parameters_by_path.call_count == 2
    mock_boto.client.return_value.get_parameters_by_path.assert_called_with(NextToken="token", Path="/api")


@mock.patch("prettyconf.loaders.boto3")
def test_fail_missing_config(mock_boto):
    mock_boto.client.return_value.get_parameters_by_path.return_value = PARAMETER_RESPONSE
    config = AwsParameterStore()

    assert "DATABASE_URL" not in config
    with pytest.raises(KeyError):
        config["DATABASE_URL"]


@mock.patch("prettyconf.loaders.boto3")
def test_parameter_store_access_fail(mock_boto):
    mock_boto.client.return_value.get_parameters_by_path.side_effect = BotoCoreError
    config = AwsParameterStore()

    assert "DATABASE_URL" not in config
    with pytest.raises(KeyError):
        config["DATABASE_URL"]
