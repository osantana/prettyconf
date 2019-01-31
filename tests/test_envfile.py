# coding: utf-8


import os

from prettyconf.loaders import EnvFile
from .base import BaseTestCase


class EnvFileTestCase(BaseTestCase):
    def setUp(self):
        super(EnvFileTestCase, self).setUp()
        self.envfile = os.path.join(self.test_files_path, "envfile")

    def test_config_file_parsing(self):
        config = EnvFile(self.envfile)

        self.assertEqual(config["KEY"], "Value")
        self.assertEqual(config["KEY_EMPTY"], "")
        self.assertEqual(config["KEY_EMPTY_WITH_COMMENTS"], "")
        self.assertEqual(config["INLINE_COMMENTS"], "Foo")
        self.assertEqual(config["HASH_CONTENT"], "Foo Bar # Baz %(key)s")
        self.assertEqual(config["PERCENT_NOT_ESCAPED"], "%%")
        self.assertEqual(config["NO_INTERPOLATION"], "%(KeyOff)s")
        self.assertEqual(config["IGNORE_SPACE"], "text")
        self.assertEqual(config["SINGLE_QUOTE_SPACE"], " text")
        self.assertEqual(config["DOUBLE_QUOTE_SPACE"], " text")
        self.assertEqual(config["UPDATED"], "text")
        self.assertEqual(config["CACHE_URL_QUOTES"], "cache+memcached://foo:bar@localhost:11211/?n=1&x=2,5")
        self.assertEqual(config["CACHE_URL"], "cache+memcached://foo:bar@localhost:11211/?n=1&x=2,5")
        self.assertEqual(config["DOUBLE_QUOTE_INSIDE_QUOTE"], 'foo "bar" baz')
        self.assertEqual(config["SINGLE_QUOTE_INSIDE_QUOTE"], "foo 'bar' baz")

    def test_missing_invalid_keys_in_config_file_parsing(self):
        config = EnvFile(self.envfile)

        self.assertNotIn("COMMENTED_KEY", config)
        self.assertNotIn("INVALID_KEY", config)
        self.assertNotIn("OTHER_INVALID_KEY", config)

    def test_default_var_format(self):
        config = EnvFile(self.envfile)

        self.assertIn("key", config)
        self.assertEqual("Value", config["key"])

    def test_custom_var_format(self):
        formatter = lambda x: '_{}'.format(str.lower(x))
        config = EnvFile(self.envfile, var_format=formatter)

        self.assertIn("VAR", config)
        self.assertEqual("test", config["VAR"])
