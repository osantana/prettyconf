# coding: utf-8


from __future__ import unicode_literals

import tempfile

from prettyconf.loaders import IniFile, InvalidConfigurationFile

from .base import BaseTestCase


class IniFileTestCase(BaseTestCase):
    def setUp(self):
        super(IniFileTestCase, self).setUp()
        self.inifile = self.test_files_path + "/config.ini"

    def test_fail_invalid_settings_file(self):
        with self.assertRaises(InvalidConfigurationFile):
            IniFile(self.test_files_path + "/invalid_section.ini")['some_value']

    def test_config_file_parsing(self):
        config = IniFile(self.inifile)

        self.assertEqual(config["KEY"], "Value")
        self.assertEqual(config["KEY_EMPTY"], "")
        # self.assertEqual(config["INLINE_COMMENTS"], "Foo")  # There is no inline comment in py3
        self.assertEqual(config["HASH_CONTENT"], "Foo 'Bar # Baz' Value")
        self.assertEqual(config["PERCENT_ESCAPED"], "%")
        self.assertEqual(config["IGNORE_SPACE"], "text")
        self.assertEqual(config["SINGLE_QUOTE_SPACE"], "' text'")
        self.assertEqual(config["DOUBLE_QUOTE_SPACE"], '" text"')
        self.assertEqual(config["UPDATED"], "text")
        self.assertNotIn("COMMENTED_KEY", config)
        self.assertNotIn("INVALID_KEY", config)
        self.assertNotIn("OTHER_INVALID_KEY", config)

        # Error when we refers to an unknown key for interpolation
        # self.assertEqual(config["NO_INTERPOLATION"], "%(unknown)s")

        # ConfigParser did not allow empty configs with inline comment
        # self.assertEqual(config["KEY_EMPTY_WITH_COMMENTS"], "")

    def test_skip_missing_key(self):
        config = IniFile(self.inifile)

        with self.assertRaises(KeyError):
            IniFile(self.inifile)['some_value']

    def test_skip_invalid_ini_file(self):
        config = IniFile(self.test_files_path + "/invalid_chars.cfg")

        with self.assertRaises(InvalidConfigurationFile):
            config['some_value']

    def test_default_var_format(self):
        config = IniFile(self.inifile)

        self.assertIn("_var", config)
        self.assertEqual("test", config["_var"])

    def test_custom_var_format(self):
        formatter = lambda x: '_{}'.format(str.lower(x))
        config = IniFile(self.inifile, var_format=formatter)

        self.assertIn("VAR", config)
        self.assertEqual("test", config["VAR"])
