import os

from prettyconf.loaders import EnvFileConfigurationLoader


# def setUp(self):
#     super(EnvFileTestCase, self).setUp()
#     self.envfile = os.path.join(self.test_files_path, "envfile")

def test_config_file_parsing(envfile):
    config = EnvFileConfigurationLoader(envfile)

    assert config["KEY"] == "Value"
    assert config["KEY_EMPTY"] == ""
    assert config["KEY_EMPTY_WITH_COMMENTS"] == ""
    assert config["INLINE_COMMENTS"] == "Foo"
    assert config["HASH_CONTENT"] == "Foo Bar # Baz %(key)s"
    assert config["PERCENT_NOT_ESCAPED"] == "%%"
    assert config["NO_INTERPOLATION"] == "%(KeyOff)s"
    assert config["IGNORE_SPACE"] == "text"
    assert config["SINGLE_QUOTE_SPACE"] == " text"
    assert config["DOUBLE_QUOTE_SPACE"] == " text"
    assert config["UPDATED"] == "text"
    assert config["CACHE_URL_QUOTES"] == "cache+memcached://foo:bar@localhost:11211/?n=1&x=2,5"
    assert config["CACHE_URL"] == "cache+memcached://foo:bar@localhost:11211/?n=1&x=2,5"
    assert config["DOUBLE_QUOTE_INSIDE_QUOTE"] == 'foo "bar" baz'
    assert config["SINGLE_QUOTE_INSIDE_QUOTE"] == "foo 'bar' baz"


def test_missing_invalid_keys_in_config_file_parsing(envfile):
    config = EnvFileConfigurationLoader(envfile)

    assert "COMMENTED_KEY" not in config
    assert "INVALID_KEY" not in config
    assert "OTHER_INVALID_KEY" not in config


def test_list_config_filenames(files_path):
    with open(os.path.join(files_path, ".env"), "w") as envfile:
        # self._create_file(self.test_files_path + "/.env")
        filenames = EnvFileConfigurationLoader.get_filenames(files_path)

    assert len(filenames) == 1
    assert envfile.name == filenames[0]
