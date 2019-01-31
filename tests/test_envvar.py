# coding: utf-8


import os

from prettyconf.loaders import Environment
from .base import BaseTestCase


class EnvironmentTestCase(BaseTestCase):
    def test_basic_config(self):
        os.environ["TEST"] = "test"
        config = Environment()

        self.assertIn("TEST", config)
        self.assertEqual("test", config["TEST"])

        del os.environ["TEST"]

    def test_fail_missing_config(self):
        config = Environment()

        self.assertNotIn("UNKNOWN", config)
        with self.assertRaises(KeyError):
            _ = config["UNKNOWN"]

    def test_default_var_format(self):
        os.environ["TEST"] = "test"
        config = Environment()

        self.assertIn("test", config)
        self.assertEqual("test", config["test"])

        del os.environ["TEST"]

    def test_custom_var_format(self):
        def formatter(x):
            return '_{}'.format(x)

        os.environ["_TEST"] = "test"
        config = Environment(var_format=formatter)

        self.assertIn("TEST", config)
        self.assertEqual("test", config["TEST"])

        del os.environ["_TEST"]
