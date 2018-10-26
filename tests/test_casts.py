import pytest

from prettyconf import config
from prettyconf.casts import Boolean, InvalidConfiguration, List, Option, Tuple


def test_basic_boolean_cast():
    boolean = Boolean()

    assert boolean(1) is True
    assert boolean("1") is True
    assert boolean("true") is True
    assert boolean("True") is True
    assert boolean("yes") is True
    assert boolean("on") is True

    assert boolean(0) is False
    assert boolean("0") is False
    assert boolean("false") is False
    assert boolean("False") is False
    assert boolean("no") is False
    assert boolean("off") is False


def test_more_valid_boolean_values():
    boolean = Boolean({"sim": True, "não": False})

    assert boolean("sim") == True
    assert boolean("yes") == True
    assert boolean("não") == False
    assert boolean("no") == False


def test_fail_invalid_boolean_cast():
    boolean = Boolean()

    with pytest.raises(InvalidConfiguration):
        boolean(42)


def test_basic_list_cast():
    l = List()

    assert l("foo,bar") == ["foo", "bar"]
    assert l("foo, bar") == ["foo", "bar"]
    assert l(" foo , bar ") == ["foo", "bar"]
    assert l(" foo ,, bar ") == ["foo", "", "bar"]
    assert l("foo, 'bar, baz', qux # doo ") == ["foo", "'bar, baz'", "qux # doo"]
    assert l("foo, '\"bar\", baz  ', qux # doo ") == ["foo", "'\"bar\", baz  '", "qux # doo"]


def test_basic_tuple_cast():
    t = Tuple()

    assert t("foo,bar") == ("foo", "bar")
    assert t("foo, bar") == ("foo", "bar")
    assert t(" foo , bar ") == ("foo", "bar")
    assert t(" foo ,, bar ") == ("foo", "", "bar")
    assert t("foo, 'bar, baz', qux # doo ") == ("foo", "'bar, baz'", "qux # doo")
    assert t("foo, '\"bar\", baz  ', qux # doo ") == ("foo", "'\"bar\", baz  '", "qux # doo")


def test_options():
    choices = {
        'option1': "asd",
        'option2': "def",
    }
    option = Option(choices)

    assert option("option1") == "asd"
    assert option("option2") == "def"


def test_fail_invalid_option_config():
    choices = {
        'option1': "asd",
        'option2': "def",
    }
    option = Option(choices)

    with pytest.raises(InvalidConfiguration):
        option("unknown")


def test_if_cast_is_unbounded():
    assert config.eval("None") is None
