# coding: utf-8


import os
from glob import glob
from shlex import shlex

try:
    from ConfigParser import SafeConfigParser as ConfigParser, NoOptionError
except ImportError:
    from configparser import ConfigParser, NoOptionError

from .exceptions import InvalidConfigurationFile


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
        key = []
        pos = 0
        comment = ""

        # parse key
        for pos, char in enumerate(line):
            if char == "=":
                break

            if char == "#":
                comment = char
                continue

            if comment:
                continue

            if char.isspace():
                continue

            key.append(char)

        else:
            raise ValueError("Invalid line format (key=value)")

        key = "".join(key)

        if not key:
            return

        # parse value
        value = []
        quote = ""
        started = False
        for char in line[pos + 1:]:
            if not char.isspace():
                started = True

            if not started:
                continue

            if char == "#" and not quote:
                break

            if char in "\"'":
                if not quote:
                    quote = char
                    continue

                if quote and quote == char:
                    quote = ""
                    continue

                value.append(char)
                continue

            value.append(char)

        value = "".join(value).rstrip()

        return key, value

    def _parse(self):
        self.configs = {}
        with open(self.filename) as envfile:
            for line in envfile:
                try:
                    key, value = self._parse_line(line.strip())
                except (ValueError, TypeError):
                    continue

                self.configs[key] = value

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
