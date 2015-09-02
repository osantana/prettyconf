# coding: utf-8


from unittest import TestCase

from prettyconf.casts import Boolean, Option, InvalidConfiguration, List, Tuple


class BooleanCastTestCase(TestCase):
    def test_basic_boolean_cast(self):
        boolean = Boolean()

        self.assertTrue(boolean(1))
        self.assertTrue(boolean("1"))
        self.assertTrue(boolean("true"))
        self.assertTrue(boolean("True"))
        self.assertTrue(boolean("yes"))
        self.assertTrue(boolean("on"))

        self.assertFalse(boolean(0))
        self.assertFalse(boolean("0"))
        self.assertFalse(boolean("false"))
        self.assertFalse(boolean("False"))
        self.assertFalse(boolean("no"))
        self.assertFalse(boolean("off"))

    def test_more_valid_boolean_values(self):
        boolean = Boolean({"sim": True, "não": False})

        self.assertTrue(boolean("sim"))
        self.assertTrue(boolean("yes"))
        self.assertFalse(boolean("não"))
        self.assertFalse(boolean("no"))

    def test_fail_invalid_boolean_cast(self):
        boolean = Boolean()

        with self.assertRaises(InvalidConfiguration):
            boolean(42)


class SequenceCastTestCase(TestCase):
    def test_basic_list_cast(self):
        l = List()

        self.assertEqual(l("foo,bar"), ["foo", "bar"])
        self.assertEqual(l("foo, bar"), ["foo", "bar"])
        self.assertEqual(l(" foo , bar "), ["foo", "bar"])
        self.assertEqual(l(" foo ,, bar "), ["foo", "", "bar"])
        self.assertEqual(l("foo, 'bar, baz', qux # doo "), ["foo", "'bar, baz'", "qux # doo"])
        self.assertEqual(l("foo, '\"bar\", baz  ', qux # doo "), ["foo", "'\"bar\", baz  '", "qux # doo"])

    def test_basic_tuple_cast(self):
        t = Tuple()

        self.assertEqual(t("foo,bar"), ("foo", "bar"))
        self.assertEqual(t("foo, bar"), ("foo", "bar"))
        self.assertEqual(t(" foo , bar "), ("foo", "bar"))
        self.assertEqual(t(" foo ,, bar "), ("foo", "", "bar"))
        self.assertEqual(t("foo, 'bar, baz', qux # doo "), ("foo", "'bar, baz'", "qux # doo"))
        self.assertEqual(t("foo, '\"bar\", baz  ', qux # doo "), ("foo", "'\"bar\", baz  '", "qux # doo"))


class OptionCastTestCase(TestCase):
    def test_options(self):
        choices = {
            'option1': "asd",
            'option2': "def",
        }
        option = Option(choices)

        self.assertEqual(option("option1"), "asd")
        self.assertEqual(option("option2"), "def")

    def test_fail_invalid_option_config(self):
        choices = {
            'option1': "asd",
            'option2': "def",
        }
        option = Option(choices)

        with self.assertRaises(InvalidConfiguration):
            option("unknown")
