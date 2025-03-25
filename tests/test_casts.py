import pytest

from prettyconf import config
from prettyconf.casts import JSON, Boolean, List, Option, Tuple
from prettyconf.exceptions import InvalidConfiguration


@pytest.mark.parametrize(
    'value,result',
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
    boolean = Boolean({'sim': True, 'não': False})

    assert boolean('sim')
    assert boolean('yes')
    assert not boolean('não')
    assert not boolean('no')


def test_fail_invalid_boolean_cast():
    boolean = Boolean()

    with pytest.raises(InvalidConfiguration):
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

    with pytest.raises(InvalidConfiguration):
        option('unknown')


def test_if_cast_is_unbounded():
    assert config.eval('None') is None


@pytest.mark.parametrize(
    'value,result',
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
    with pytest.raises(InvalidConfiguration):
        json('invalid')
