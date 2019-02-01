from prettyconf.loaders import IniFile, InvalidConfigurationFile

from .base import BaseTestCase


class IniFileTestCase(BaseTestCase):
    def setUp(self):
        super(IniFileTestCase, self).setUp()
        self.inifile = self.test_files_path + "/config.ini"

    def test_basic_config_object(self):
        config = IniFile(self.inifile)

        self.assertEqual(repr(config), 'IniFile("{}")'.format(self.inifile))

    def test_fail_no_settings_section_in_ini_file(self):
        with self.assertRaises(KeyError):
            return IniFile(self.test_files_path + "/invalid_section.ini")['some_value']

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
        with self.assertRaises(KeyError):
            return IniFile(self.inifile)['some_value']

    def test_skip_invalid_ini_file(self):
        config = IniFile(self.test_files_path + "/invalid_chars.cfg")

        with self.assertRaises(KeyError):
            return config['some_value']

    def test_default_var_format(self):
        config = IniFile(self.inifile)

        self.assertIn("_var", config)
        self.assertEqual("test", config["_var"])

    def test_custom_var_format(self):
        def formatter(x):
            return '_{}'.format(str.lower(x))

        config = IniFile(self.inifile, var_format=formatter)

        self.assertIn("VAR", config)
        self.assertEqual("test", config["VAR"])

    def test_fail_missing_envfile_contains(self):
        config = IniFile("does-not-exist.ini")
        self.assertNotIn('error', config)

    def test_fail_missing_envfile_get_item(self):
        config = IniFile("does-not-exist.ini")
        with self.assertRaises(KeyError):
            return config['error']
