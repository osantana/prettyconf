# coding: utf-8


from unittest import TestCase

from prettyconf import Boolean, List


# bool, list, dict


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

        with self.assertRaises(TypeError):
            boolean(42)


class ListCastTestCase(TestCase):
    def test_basic_list_cast(self):
        l = List()

        self.assertEqual(l("foo,bar"), ["foo", "bar"])
        self.assertEqual(l("foo, bar"), ["foo", "bar"])
        self.assertEqual(l(" foo , bar "), ["foo", "bar"])
        self.assertEqual(l(" foo ,, bar "), ["foo", "", "bar"])
        self.assertEqual(l("foo, 'bar, baz', qux # doo "), ["foo", "'bar, baz'", "qux # doo"])
        self.assertEqual(l("foo, '\"bar\", baz  ', qux # doo "), ["foo", "'\"bar\", baz  '", "qux # doo"])
