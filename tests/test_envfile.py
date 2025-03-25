import pytest

from prettyconf.loaders import EnvFile


def test_basic_config_object(envfile):
    config = EnvFile(envfile)

    assert repr(config) == f'EnvFile("{envfile}")'


def test_config_file_parsing(envfile):
    config = EnvFile(envfile)

    assert config['KEY'] == 'Value'
    assert config['KEY_EMPTY'] == ''
    assert config['KEY_EMPTY_WITH_COMMENTS'] == ''
    assert config['INLINE_COMMENTS'] == 'Foo'
    assert config['HASH_CONTENT'] == 'Foo Bar # Baz %(key)s'
    assert config['PERCENT_NOT_ESCAPED'] == '%%'
    assert config['NO_INTERPOLATION'] == '%(KeyOff)s'
    assert config['IGNORE_SPACE'] == 'text'
    assert config['SINGLE_QUOTE_SPACE'] == ' text'
    assert config['DOUBLE_QUOTE_SPACE'] == ' text'
    assert config['UPDATED'] == 'text'
    assert config['CACHE_URL_QUOTES'] == 'cache+memcached://foo:bar@localhost:11211/?n=1&x=2,5'
    assert config['CACHE_URL'] == 'cache+memcached://foo:bar@localhost:11211/?n=1&x=2,5'
    assert config['DOUBLE_QUOTE_INSIDE_QUOTE'] == 'foo "bar" baz'
    assert config['SINGLE_QUOTE_INSIDE_QUOTE'] == "foo 'bar' baz"
    assert config['MULTIPLE_LINES'] == 'multiple lines config'


def test_missing_invalid_keys_in_config_file_parsing(envfile):
    config = EnvFile(envfile)

    assert 'COMMENTED_KEY' not in config
    assert 'INVALID_KEY' not in config
    assert 'OTHER_INVALID_KEY' not in config


def test_default_var_format(envfile):
    config = EnvFile(envfile)

    assert 'key' in config
    assert 'Value' == config['key']


def test_custom_var_format(envfile):
    def formatter(x):
        return f'_{str.lower(x)}'

    config = EnvFile(envfile, var_format=formatter)

    assert 'VAR' in config
    assert 'test' == config['VAR']


def test_fail_missing_envfile_contains():
    config = EnvFile('does-not-exist.env')
    assert 'error' not in config


def test_fail_missing_envfile_get_item():
    config = EnvFile('does-not-exist.env')
    with pytest.raises(KeyError):
        return config['error']
