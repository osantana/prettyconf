import pytest

from prettyconf.loaders import EnvFile

CACHE_URL = 'cache+memcached://foo:bar@localhost:11211/?n=1&x=2,5'

PARSED_VALUES = (
    pytest.param('KEY=Value', 'KEY', 'Value', id='plain-value'),
    pytest.param('KEY_EMPTY=', 'KEY_EMPTY', '', id='empty-value'),
    pytest.param('KEY_EMPTY=  # no comments', 'KEY_EMPTY', '', id='empty-value-with-comment'),
    pytest.param('INLINE=Foo  # a comment', 'INLINE', 'Foo', id='inline-comment'),
    pytest.param(
        "HASH_CONTENT=Foo 'Bar # Baz' %(key)s  # a comment",
        'HASH_CONTENT',
        'Foo Bar # Baz %(key)s',
        id='hash-inside-quotes',
    ),
    pytest.param('PERCENT_NOT_ESCAPED=%%', 'PERCENT_NOT_ESCAPED', '%%', id='percent-not-escaped'),
    pytest.param('NO_INTERPOLATION=%(KeyOff)s', 'NO_INTERPOLATION', '%(KeyOff)s', id='no-interpolation'),
    pytest.param('IGNORE_SPACE = text', 'IGNORE_SPACE', 'text', id='spaces-around-equals'),
    pytest.param("SINGLE_QUOTE_SPACE = ' text'", 'SINGLE_QUOTE_SPACE', ' text', id='single-quoted-space'),
    pytest.param('DOUBLE_QUOTE_SPACE = " text"', 'DOUBLE_QUOTE_SPACE', ' text', id='double-quoted-space'),
    pytest.param('UPDATED=\nUPDATED=text', 'UPDATED', 'text', id='last-assignment-wins'),
    pytest.param(f'CACHE_URL="{CACHE_URL}"', 'CACHE_URL', CACHE_URL, id='quoted-url'),
    pytest.param(f'CACHE_URL={CACHE_URL}', 'CACHE_URL', CACHE_URL, id='bare-url'),
    pytest.param('MIXED=\'foo "bar" baz\'', 'MIXED', 'foo "bar" baz', id='double-quote-inside-single'),
    pytest.param('MIXED="foo \'bar\' baz"', 'MIXED', "foo 'bar' baz", id='single-quote-inside-double'),
    pytest.param(
        'MULTIPLE_LINES=multiple \\\nlines \\\nconfig',
        'MULTIPLE_LINES',
        'multiple lines config',
        id='continuation',
    ),
    pytest.param('HASH_GLUED=Xy#7kQ', 'HASH_GLUED', 'Xy#7kQ', id='hash-glued-to-text'),
    pytest.param('HASH_AFTER_EQUALS=#novalue', 'HASH_AFTER_EQUALS', '#novalue', id='hash-opening-the-value'),
    pytest.param('ESCAPED_HASH=a\\#b', 'ESCAPED_HASH', 'a#b', id='escaped-hash'),
    pytest.param('ESCAPED_QUOTE=a\\"b', 'ESCAPED_QUOTE', 'a"b', id='escaped-quote'),
    pytest.param('ESCAPED_ORDINARY=C:\\Users', 'ESCAPED_ORDINARY', 'C:Users', id='escaped-ordinary-character'),
    pytest.param('DOUBLE_BACKSLASH=C:\\\\Users', 'DOUBLE_BACKSLASH', 'C:\\Users', id='doubled-backslash'),
    pytest.param('UNBALANCED="never closed', 'UNBALANCED', 'never closed', id='unbalanced-quote'),
    pytest.param(
        'UNBALANCED="never closed\nAFTER=value  # comment',
        'AFTER',
        'value',
        id='line-after-unbalanced-quote',
    ),
)

SKIPPED_ENTRIES = (
    pytest.param('#COMMENTED_KEY=None', 'COMMENTED_KEY', id='commented-out-line'),
    pytest.param('INVALID_KEY#SKIPPED', 'INVALID_KEY', id='key-without-value'),
    pytest.param('OTHER_INVALID_KEY', 'OTHER_INVALID_KEY', id='bare-key'),
)


@pytest.fixture
def parse(tmp_path):
    def _parse(content):
        path = tmp_path / 'envfile'
        path.write_text(f'{content}\n')
        return EnvFile(str(path))

    return _parse


def test_basic_config_object(envfile):
    config = EnvFile(envfile)

    assert repr(config) == f'EnvFile("{envfile}")'


@pytest.mark.parametrize(('content', 'key', 'expected'), PARSED_VALUES)
def test_config_file_parsing(parse, content, key, expected):
    config = parse(content)

    assert config[key] == expected


@pytest.mark.parametrize(('content', 'key'), SKIPPED_ENTRIES)
def test_missing_invalid_keys_in_config_file_parsing(parse, content, key):
    config = parse(content)

    assert key not in config


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
