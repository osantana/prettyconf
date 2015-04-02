# coding: utf-8


import os

from .base import BaseTestCase
from prettyconf import Configuration, UnknownConfiguration, InvalidConfigurationCast

ENVFILE_CONTENT = """
ENVFILE=Environment File Value
ENVVAR=Must be overrided
"""

INIFILE_CONTENT = """
[settings]
INIFILE=INI File Value
ENVFILE=Must be overrided
"""


class ConfigTestCase(BaseTestCase):
    def setUp(self):
        super(ConfigTestCase, self).setUp()
        self._create_file(self.test_files_path + "/../.env", ENVFILE_CONTENT)
        self._create_file(self.test_files_path + "/../settings.ini", INIFILE_CONTENT)

    def test_basic_config(self):
        os.environ["ENVVAR"] = "Environment Variable Value"
        config = Configuration()
        self.assertEqual(len(config.configurations), 3)  # envvar + .env + settings.ini
        self.assertEqual(config("ENVVAR"), "Environment Variable Value")
        self.assertEqual(config("ENVFILE"), "Environment File Value")
        self.assertEqual(config("INIFILE"), "INI File Value")

    def test_config_default_values(self):
        config = Configuration()
        self.assertEqual(config("DEFAULT", default="Default Value"), "Default Value")

    def test_config_cast_value(self):
        os.environ["INTEGER"] = "42"
        config = Configuration()
        self.assertEqual(config("INTEGER", cast=int), 42)

    def test_fail_invalid_cast_type(self):
        os.environ["INTEGER"] = "42"
        config = Configuration()
        with self.assertRaises(InvalidConfigurationCast):
            config("INTEGER", cast="not callable")

    def test_fail_unknown_config_without_default_value(self):
        os.environ["ENVVAR"] = "Environment Variable Value"
        config = Configuration()
        self.assertEqual(len(config.configurations), 3)  # envvar + .env + settings.ini

        with self.assertRaises(UnknownConfiguration):
            config("UNKNOWN")
