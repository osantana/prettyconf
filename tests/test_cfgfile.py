# coding: utf-8


from .base import BaseTestCase
from prettyconf import IniFileConfigurationLoader, InvalidConfigurationFile


class IniFileTestCase(BaseTestCase):
    def setUp(self):
        super(IniFileTestCase, self).setUp()
        self.inifile = self.test_files_path + "/config.ini"

    def test_fail_invalid_settings_file(self):
        with self.assertRaises(InvalidConfigurationFile):
            IniFileConfigurationLoader(self.test_files_path + "/invalid.ini")

    def test_config_file_parsing(self):
        config = IniFileConfigurationLoader(self.inifile)

        self.assertEqual(config["KEY"], "Value")
        self.assertEqual(config["KEY_EMPTY"], "")
        self.assertEqual(config["INLINE_COMMENTS"], "Foo")
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

    def test_list_config_filenames(self):
        filenames = IniFileConfigurationLoader.get_filenames(self.test_files_path)
        self.assertEqual(len(filenames), 2)
        self.assertEqual(self.test_files_path + "/config.ini", filenames[0])
        self.assertEqual(self.test_files_path + "/invalid.ini", filenames[1])
