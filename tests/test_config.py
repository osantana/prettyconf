# coding: utf-8


import os

from .base import BaseTestCase
from prettyconf import Config

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
        config = Config()
        self.assertEqual(len(config.configurations), 3)  # envvar + .env + settings.ini
        self.assertEqual(config("ENVVAR"), "Environment Variable Value")
        self.assertEqual(config("ENVFILE"), "Environment File Value")
        self.assertEqual(config("INIFILE"), "INI File Value")

    def test_config_default_values(self):
        # TODO: test cast & default values
        # TODO: casts: Boolean, Csv, Dictionary
        self.fail("TODO")
