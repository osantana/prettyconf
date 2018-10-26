import os
import pytest

from prettyconf.loaders import IniFileConfigurationLoader, InvalidConfigurationFile


def test_fail_invalid_settings_file(files_path):
    with pytest.raises(InvalidConfigurationFile):
        IniFileConfigurationLoader(os.path.join(files_path, "invalid_section.ini"))


def test_config_file_parsing(inifile):
    config = IniFileConfigurationLoader(inifile)

    assert config["KEY"] == "Value"
    assert config["KEY_EMPTY"] == ""
    assert config["HASH_CONTENT"] == "Foo 'Bar # Baz' Value"
    assert config["PERCENT_ESCAPED"] == "%"
    assert config["IGNORE_SPACE"] == "text"
    assert config["SINGLE_QUOTE_SPACE"] == "' text'"
    assert config["DOUBLE_QUOTE_SPACE"] == '" text"'
    assert config["UPDATED"] == "text"
    assert "COMMENTED_KEY" not in config
    assert "INVALID_KEY" not in config
    assert "OTHER_INVALID_KEY" not in config

    # Error when we refers to an unknown key for interpolation
    # self.assertEqual(config["NO_INTERPOLATION"], "%(unknown)s")

    # ConfigParser did not allow empty configs with inline comment
    # self.assertEqual(config["KEY_EMPTY_WITH_COMMENTS"], "")


def test_list_config_filenames(files_path):
    filenames = IniFileConfigurationLoader.get_filenames(files_path)
    assert len(filenames) == 3
    assert os.path.join(files_path, "config.ini") in filenames
    assert os.path.join(files_path, "invalid_section.ini") in filenames
