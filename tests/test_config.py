import os

from prettyconf.configuration import Configuration
from prettyconf.exceptions import UnknownConfiguration
from prettyconf.loaders import EnvFile, Environment, IniFile
from .base import BaseTestCase

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
        self.envfile = self.test_files_path + "/../.env"
        self.inifile = self.test_files_path + "/../settings.ini"
        self._create_file(self.envfile, ENVFILE_CONTENT)
        self._create_file(self.inifile, INIFILE_CONTENT)

    def test_basic_config(self):
        os.environ["ENVVAR"] = "Environment Variable Value"
        config = Configuration()
        self.assertEqual(config("ENVVAR"), "Environment Variable Value")
        self.assertEqual(config("ENVFILE"), "Environment File Value")
        self.assertEqual(config("INIFILE"), "INI File Value")
        self.assertEqual(len(config.loaders), 2)  # Environment + RecursiveSearch
        del os.environ["ENVVAR"]

    def test_customized_loaders(self):
        os.environ["ENVVAR"] = "Environment Variable Value"
        os.environ["ENVVAR2"] = "Foo"
        loaders = [EnvFile(self.envfile), Environment(), IniFile(self.inifile)]
        config = Configuration(loaders=loaders)
        self.assertEqual(config("ENVVAR"), "Must be overrided")
        self.assertEqual(config("ENVVAR2"), "Foo")
        self.assertEqual(config("ENVFILE"), "Environment File Value")
        self.assertEqual(config("INIFILE"), "INI File Value")
        self.assertEqual(len(config.loaders), 3)
        del os.environ["ENVVAR"]
        del os.environ["ENVVAR2"]

    def test_from_import_basic_config(self):
        from prettyconf import config

        self.assertIsInstance(config, Configuration)

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
        with self.assertRaises(TypeError):
            config("INTEGER", cast="not callable")

    def test_fail_unknown_config_without_default_value(self):
        os.environ["ENVVAR"] = "Environment Variable Value"
        config = Configuration()
        with self.assertRaises(UnknownConfiguration):
            config("UNKNOWN")

    def test_none_as_default_value(self):
        config = Configuration()
        self.assertIsNone(config("UNKNOWN", default=None))
