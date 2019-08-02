from unittest import mock

import botocore

from prettyconf.loaders import AwsParameterStore
from .base import BaseTestCase


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


class AwsParameterStoreTestCase(BaseTestCase):
    @mock.patch("prettyconf.loaders.boto3")
    def test_basic_config(self, mock_boto):
        mock_boto.client.return_value.get_parameters_by_path.return_value = PARAMETER_RESPONSE
        config = AwsParameterStore()

        self.assertIn("HOST", config)
        self.assertEqual(config["HOST"], "host_url")
        self.assertTrue(repr(config).startswith("AwsParameterStore(path="))

    @mock.patch("prettyconf.loaders.boto3")
    def test_basic_config_response_paginated(self, mock_boto):
        mock_boto.client.return_value.get_parameters_by_path.side_effect = [
            PARAMETER_RESPONSE_FIRST_PAGE, PARAMETER_RESPONSE_LAST_PAGE,
        ]
        config = AwsParameterStore()

        self.assertIn("HOST", config)
        self.assertIn("DEBUG", config)
        self.assertEqual(config["HOST"], "host_url")
        self.assertEqual(config["DEBUG"], "false")

    @mock.patch("prettyconf.loaders.boto3")
    def test_fail_missing_config(self, mock_boto):
        mock_boto.client.return_value.get_parameters_by_path.return_value = PARAMETER_RESPONSE
        config = AwsParameterStore()

        self.assertNotIn("DATABASE_URL", config)
        with self.assertRaises(KeyError):
            config["DATABASE_URL"]

    @mock.patch("prettyconf.loaders.boto3")
    def test_parameter_store_access_fail(self, mock_boto):
        mock_boto.client.return_value.get_parameters_by_path.side_effect = botocore.exceptions.BotoCoreError
        config = AwsParameterStore()

        self.assertNotIn("DATABASE_URL", config)
        with self.assertRaises(KeyError):
            config["DATABASE_URL"]
