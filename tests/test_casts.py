import base64
import textwrap

import pytest

from prettyconf import config
from prettyconf.casts import JSON, Base64, Boolean, List, Option, Tuple
from prettyconf.exceptions import InvalidConfigurationError

PRIVATE_KEY = textwrap.dedent("""\
    -----BEGIN PRIVATE KEY-----
    MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQg
    -----END PRIVATE KEY-----
    """)


@pytest.mark.parametrize(
    ('value', 'result'),
    [
        (1, True),
        ('1', True),
        ('true', True),
        ('True', True),
        ('TrUE', True),
        ('TRUE', True),
        ('yes', True),
        ('YES', True),
        ('Yes', True),
        ('on', True),
        ('ON', True),
        ('On', True),
        ('t', True),
        (True, True),
        (0, False),
        ('0', False),
        ('false', False),
        ('False', False),
        ('FalSE', False),
        ('FALSE', False),
        ('no', False),
        ('No', False),
        ('NO', False),
        ('nO', False),
        ('off', False),
        ('Off', False),
        ('OFF', False),
        ('OfF', False),
        ('f', False),
        (False, False),
    ],
)
def test_basic_boolean_cast_values(value, result):
    boolean = Boolean()
    assert boolean(value) is result


def test_more_valid_boolean_values():
    boolean = Boolean({'enabled': True, 'disabled': False})

    assert boolean('enabled')
    assert boolean('yes')
    assert not boolean('disabled')
    assert not boolean('no')


def test_custom_boolean_values_do_not_leak_into_other_instances():
    Boolean({'enabled': True})

    assert 'enabled' not in Boolean.default_values
    assert 'enabled' not in Boolean().values


def test_fail_invalid_boolean_cast():
    boolean = Boolean()

    with pytest.raises(InvalidConfigurationError):
        boolean(42)


def test_basic_list_cast():
    list_cast = List()

    assert list_cast('foo,bar') == ['foo', 'bar']
    assert list_cast('foo, bar') == ['foo', 'bar']
    assert list_cast(' foo , bar ') == ['foo', 'bar']
    assert list_cast(' foo ,, bar ') == ['foo', '', 'bar']
    assert list_cast("foo, 'bar, baz', qux # doo ") == ['foo', "'bar, baz'", 'qux # doo']
    assert list_cast('foo, \'"bar", baz  \', qux # doo ') == ['foo', '\'"bar", baz  \'', 'qux # doo']


def test_basic_tuple_cast():
    tuple_cast = Tuple()

    assert tuple_cast('foo,bar') == ('foo', 'bar')
    assert tuple_cast('foo, bar') == ('foo', 'bar')
    assert tuple_cast(' foo , bar ') == ('foo', 'bar')
    assert tuple_cast(' foo ,, bar ') == ('foo', '', 'bar')
    assert tuple_cast("foo, 'bar, baz', qux # doo ") == ('foo', "'bar, baz'", 'qux # doo')
    assert tuple_cast('foo, \'"bar", baz  \', qux # doo ') == ('foo', '\'"bar", baz  \'', 'qux # doo')


def test_options():
    choices = {
        'option1': 'asd',
        'option2': 'def',
    }
    option = Option(choices)

    assert option('option1') == 'asd'
    assert option('option2') == 'def'


def test_fail_invalid_option_config():
    choices = {
        'option1': 'asd',
        'option2': 'def',
    }
    option = Option(choices)

    with pytest.raises(InvalidConfigurationError):
        option('unknown')


def test_if_cast_is_unbounded():
    assert config.eval('None') is None


@pytest.mark.parametrize(
    ('value', 'result'),
    [
        ('"string"', 'string'),
        ('["obj1", "obj2"]', ['obj1', 'obj2']),
        ('{"key": "value"}', {'key': 'value'}),
        ('null', None),
        (['already decoded object in default argument'], ['already decoded object in default argument']),
    ],
)
def test_basic_json_cast_values(value, result):
    json = JSON()
    assert json(value) == result


def test_fail_invalid_json_config():
    json = JSON()
    with pytest.raises(InvalidConfigurationError):
        json('invalid')


def test_base64_cast_returns_bytes():
    encoded = base64.b64encode(PRIVATE_KEY.encode()).decode()

    assert Base64()(encoded) == PRIVATE_KEY.encode()


def test_base64_cast_decodes_with_an_encoding():
    encoded = base64.b64encode(PRIVATE_KEY.encode()).decode()

    assert Base64('utf-8')(encoded) == PRIVATE_KEY


def test_base64_cast_accepts_binary_content():
    content = bytes(range(256))
    encoded = base64.b64encode(content).decode()

    assert Base64()(encoded) == content


def test_base64_cast_joins_wrapped_lines():
    content = PRIVATE_KEY.encode()
    wrapped = '\n'.join(textwrap.wrap(base64.b64encode(content).decode(), 76))

    assert '\n' in wrapped
    assert Base64()(wrapped) == content


def test_base64_cast_accepts_bytes_input():
    encoded = base64.b64encode(PRIVATE_KEY.encode())

    assert Base64()(encoded) == PRIVATE_KEY.encode()


def test_base64_cast_repr():
    assert repr(Base64('utf-8')) == "Base64(encoding='utf-8')"


@pytest.mark.parametrize('value', ['not base64!', 42, None])
def test_fail_invalid_base64(value):
    with pytest.raises(InvalidConfigurationError):
        Base64()(value)


@pytest.mark.parametrize('value', ['YWJj=', 'YWJj==', 'YWJj===', 'YWJ', 'YW=j', '====', 'YWJjZB==', 'YWJj\u00ff'])
def test_fail_base64_that_is_not_canonically_encoded(value):
    with pytest.raises(InvalidConfigurationError):
        Base64()(value)


def test_base64_accepts_what_it_produces():
    for content in [b'', b'a', b'ab', b'abc', b'abcd', bytes(range(256))]:
        encoded = base64.b64encode(content).decode()
        assert Base64()(encoded) == content


def test_fail_base64_that_is_not_text():
    encoded = base64.b64encode(b'\xff\xfe binary').decode()

    with pytest.raises(InvalidConfigurationError):
        Base64('utf-8')(encoded)


def test_base64_error_never_leaks_the_secret():
    secret = base64.b64encode(PRIVATE_KEY.encode()).decode() + '!!!'

    with pytest.raises(InvalidConfigurationError) as error:
        Base64()(secret)

    assert 'PRIVATE KEY' not in str(error.value)
    assert secret not in str(error.value)


@pytest.mark.parametrize(
    ('cast', 'value'),
    [
        (Boolean(), 'super-secret'),
        (Option({'production': 1}), 'super-secret'),
        (JSON(), 'super-secret'),
        (Base64(), 'super-secret'),
        (Base64('utf-8'), base64.b64encode(b'\xff\xfe').decode()),
    ],
)
def test_no_cast_puts_the_rejected_value_in_its_error_message(cast, value):
    with pytest.raises(InvalidConfigurationError) as error:
        cast(value)

    assert 'super-secret' not in str(error.value)
    assert value not in str(error.value)


def test_option_cast_error_lists_the_valid_choices():
    option = Option({'production': 1, 'local': 2})

    with pytest.raises(InvalidConfigurationError) as error:
        option('unknown')

    assert "'production'" in str(error.value)
    assert "'local'" in str(error.value)


def test_base64_cast_shortcut(monkeypatch):
    monkeypatch.setenv('CREDENTIALS', base64.b64encode(b'{"type": "service_account"}').decode())

    assert config('CREDENTIALS', cast=config.base64) == b'{"type": "service_account"}'
