# coding: utf-8

import os
import sys

from glob import glob
from shlex import shlex

try:
    from ConfigParser import SafeConfigParser as ConfigParser, NoOptionError
except ImportError:
    from configparser import ConfigParser, NoOptionError


class ConfigurationException(Exception):
    pass


class InvalidConfigurationFile(ConfigurationException):
    pass


class InvalidPath(ConfigurationException):
    pass


class UnknownConfiguration(ConfigurationException):
    pass


class InvalidConfiguration(ConfigurationException):
    pass


class InvalidConfigurationCast(ConfigurationException):
    pass


class AbstractConfigurationLoader(object):
    def __contains__(self, item):
        raise NotImplementedError()

    def __getitem__(self, item):
        raise NotImplementedError()


class EnvVarConfigurationLoader(AbstractConfigurationLoader):
    def __contains__(self, item):
        return item in os.environ

    def __getitem__(self, item):
        return os.environ[item]


class AbstractFileConfigurationLoader(AbstractConfigurationLoader):
    patterns = ()

    @classmethod
    def get_filenames(cls, path):
        filenames = []
        for pattern in cls.patterns:
            filenames += glob(os.path.join(path, pattern))
        return filenames

    def __getitem__(self, item):
        raise NotImplementedError()

    def __contains__(self, item):
        raise NotImplementedError()


class EnvFileConfigurationLoader(AbstractFileConfigurationLoader):
    patterns = (".env", )

    def __init__(self, filename):
        self.filename = filename
        self.configs = None

    @staticmethod
    def _parse_line(line):
        parser = shlex(line)
        parser.wordchars += "%()"

        parsed_line = list(parser)

        if len(parsed_line) < 2 or parsed_line[1] != "=":
            raise ValueError("Invalid line format (key=value)")

        key = parsed_line[0]
        value = " ".join(part.strip("\"'") for part in parsed_line[2:])
        return key, value

    def _parse(self):
        self.configs = {}
        with open(self.filename) as envfile:
            for line in envfile:
                try:
                    line = self._parse_line(line)
                except ValueError:
                    continue

                self.configs[line[0]] = line[1]

    def __contains__(self, item):
        if self.configs is None:
            self._parse()

        return item in self.configs

    def __getitem__(self, item):
        if self.configs is None:
            self._parse()

        return self.configs[item]


class IniFileConfigurationLoader(AbstractFileConfigurationLoader):
    default_section = "settings"
    patterns = ("*.ini", "*.cfg")

    def __init__(self, filename, section=None):
        self.filename = filename

        if not section:
            section = self.default_section

        self.section = section

        self.parser = ConfigParser(allow_no_value=True)

        with open(self.filename) as inifile:
            self.parser.readfp(inifile)

        if not self.parser.has_section(self.section):
            raise InvalidConfigurationFile("Missing [{}] section in {}".format(self.section, self.filename))

    def __contains__(self, item):
        return self.parser.has_option(self.section, item)

    def __getitem__(self, item):
        try:
            return self.parser.get(self.section, item)
        except NoOptionError:
            raise KeyError("{!r}".format(item))


class ConfigurationDiscovery(object):
    default_filetypes = (EnvFileConfigurationLoader, IniFileConfigurationLoader)

    def __init__(self, starting_path, filetypes=None):
        self.starting_path = os.path.realpath(os.path.abspath(starting_path))
        if filetypes is None:
            filetypes = self.default_filetypes
        self.filetypes = filetypes
        self._config_files = None

    def _scan_path(self, path):
        config_files = []

        for file_type in self.filetypes:
            for filename in file_type.get_filenames(path):
                try:
                    config_files.append(file_type(filename))
                except InvalidConfigurationFile:
                    continue

        return config_files

    def _discover(self):
        self._config_files = []

        path = self.starting_path
        while True:
            if not os.path.isdir(path):
                raise InvalidPath("Invalid path ({})".format(path))

            self._config_files += self._scan_path(path)

            if path == os.path.sep:
                break

            path = os.path.dirname(path)

    @property
    def config_files(self):
        if self._config_files is None:
            self._discover()

        return self._config_files


class Configuration(object):
    def __init__(self, configs=None, starting_path=None):
        if configs is None:
            configs = [EnvVarConfigurationLoader()]
        self.configurations = configs

        if starting_path is None:
            starting_path = self._caller_path()
        self.starting_path = starting_path

        self._init_configs()

    @staticmethod
    def _caller_path():
        # MAGIC! Get the caller's module path.
        frame = sys._getframe()
        path = os.path.dirname(frame.f_back.f_back.f_code.co_filename)
        return path

    def _init_configs(self):
        discovery = ConfigurationDiscovery(self.starting_path)
        self.configurations.extend(discovery.config_files)

    def __call__(self, item, cast=lambda v: v, default=None):
        if not callable(cast):
            raise InvalidConfigurationCast("Cast must be callable")

        for configuration in self.configurations:
            try:
                return cast(configuration[item])
            except KeyError:
                continue

        if default is None:
            raise UnknownConfiguration("Configuration '{}' not found".format(item))

        return cast(default)


# Use from prettyconf import config
config = Configuration()


class AbstractCast(object):
    def __call__(self, value):
        raise NotImplementedError()


class Boolean(AbstractCast):
    default_values = {
        "1": True, "true": True, "yes": True, "y": True, "on": True,
        "0": False, "false": False, "no": False, "n": False, "off": False,
    }

    def __init__(self, values=None):
        self.values = self.default_values
        if isinstance(values, dict):
            self.values.update(values)

    def __call__(self, value):
        try:
            return self.values[str(value).lower()]
        except KeyError:
            raise InvalidConfiguration("Error casting value {!r} to boolean".format(value))


class List(AbstractCast):
    def __init__(self, delimiter=",", quotes="\"'"):
        self.delimiter = delimiter
        self.quotes = quotes

    def _parse(self, string):
        elements = []
        element = []
        quote = ""
        for char in string:
            # open quote
            if char in self.quotes and not quote:
                quote = char
                element.append(char)
                continue

            # close quote
            if char in self.quotes and char == quote:
                quote = ""
                element.append(char)
                continue

            if quote:
                element.append(char)
                continue

            if char == self.delimiter:
                elements.append("".join(element))
                element = []
                continue

            element.append(char)

        # remaining element
        if element:
            elements.append("".join(element))

        return [e.strip() for e in elements]

    def __call__(self, value):
        return self._parse(value)


class Options(AbstractCast):
    """
    Example::
        _INSTALLED_APPS = ("foo", "bar")
        INSTALLED_APPS = config("ENVIRONMENT", default="production", cast=Options({
            "production": _INSTALLED_APPS,
            "local": _INSTALLED_APPS + ("baz",)
        }))
    """
    def __init__(self, options):
        self.options = options

    def __call__(self, value):
        try:
            return self.options[value]
        except KeyError:
            raise InvalidConfiguration("Invalid option {!r}".format(value))
