# coding: utf-8


import os

from .base import BaseTestCase
from prettyconf import EnvVarConfigurationLoader


class EnvVarTestCase(BaseTestCase):
    def test_basic_config(self):
        os.environ["TEST"] = "test"
        config = EnvVarConfigurationLoader()

        self.assertIn("TEST", config)
        self.assertEqual("test", config["TEST"])

        del os.environ["TEST"]

    def test_fail_missing_config(self):
        config = EnvVarConfigurationLoader()

        self.assertNotIn("UNKNOWN", config)
        with self.assertRaises(KeyError):
            _ = config["UNKNOWN"]
