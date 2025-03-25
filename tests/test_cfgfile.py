import pytest

from prettyconf.loaders import IniFile


def test_basic_config_object(inifile):
    config = IniFile(inifile)

    assert repr(config) == f'IniFile("{inifile}")'


def test_fail_no_settings_section_in_ini_file(files_path):
    with pytest.raises(KeyError):
        return IniFile(files_path + '/invalid_section.ini')['some_value']


def test_config_file_parsing(inifile):
    config = IniFile(inifile)

    assert config['KEY'] == 'Value'
    assert config['KEY_EMPTY'] == ''
    assert config['HASH_CONTENT'] == "Foo 'Bar # Baz' Value"
    assert config['PERCENT_ESCAPED'] == '%'
    assert config['IGNORE_SPACE'] == 'text'
    assert config['SINGLE_QUOTE_SPACE'] == "' text'"
    assert config['DOUBLE_QUOTE_SPACE'] == '" text"'
    assert config['UPDATED'] == 'text'
    assert 'COMMENTED_KEY' not in config
    assert 'INVALID_KEY' not in config
    assert 'OTHER_INVALID_KEY' not in config


def test_skip_missing_key(inifile):
    with pytest.raises(KeyError):
        return IniFile(inifile)['some_value']


def test_skip_invalid_ini_file(files_path):
    config = IniFile(files_path + '/invalid_chars.cfg')

    with pytest.raises(KeyError):
        return config['some_value']


def test_default_var_format(inifile):
    config = IniFile(inifile)

    assert '_var' in config
    assert 'test' == config['_var']


def test_custom_var_format(inifile):
    def formatter(x):
        return f'_{str.lower(x)}'

    config = IniFile(inifile, var_format=formatter)

    assert 'VAR' in config
    assert 'test' == config['VAR']


def test_fail_missing_envfile_contains():
    config = IniFile('does-not-exist.ini')
    assert 'error' not in config


def test_fail_missing_envfile_get_item():
    config = IniFile('does-not-exist.ini')
    with pytest.raises(KeyError):
        return config['error']
