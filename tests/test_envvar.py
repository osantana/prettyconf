# coding: utf-8


import os

from .base import BaseTestCase
from prettyconf import EnvVarConfig


class EnvVarTestCase(BaseTestCase):
    def test_basic_config(self):
        os.environ["TEST"] = "test"
        config = EnvVarConfig()

        self.assertIn("TEST", config)
        self.assertEqual("test", config["TEST"])

        del os.environ["TEST"]

    def test_fail_missing_config(self):
        config = EnvVarConfig()

        self.assertNotIn("UNKNOWN", config)
        with self.assertRaises(KeyError):
            _ = config["UNKNOWN"]
