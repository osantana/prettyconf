# coding: utf-8


import os

from .base import BaseTestCase
from prettyconf.exceptions import UnknownConfiguration, InvalidConfigurationCast
from prettyconf.configuration import Configuration


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
        self.assertEqual(config("ENVVAR"), "Environment Variable Value")
        self.assertEqual(config("ENVFILE"), "Environment File Value")
        self.assertEqual(config("INIFILE"), "INI File Value")
        self.assertEqual(len(config.configurations), 3)  # envvar + .env + settings.ini

    def test_basic_config_with_starting_path(self):
        os.environ["ENVVAR"] = "Environment Variable Value"
        starting_path = os.path.dirname(__file__)
        config = Configuration(starting_path=starting_path)
        self.assertEqual(config("ENVVAR"), "Environment Variable Value")
        self.assertEqual(config("ENVFILE"), "Environment File Value")
        self.assertEqual(config("INIFILE"), "INI File Value")
        self.assertEqual(len(config.configurations), 3)  # envvar + .env + settings.ini

    def test_from_import_basic_config(self):
        from prettyconf import config
        os.environ["ENVVAR"] = "Environment Variable Value"
        self.assertEqual(config("ENVVAR"), "Environment Variable Value")
        self.assertEqual(config("ENVFILE"), "Environment File Value")
        self.assertEqual(config("INIFILE"), "INI File Value")
        self.assertEqual(len(config.configurations), 3)  # envvar + .env + settings.ini

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
        with self.assertRaises(UnknownConfiguration):
            config("UNKNOWN")
