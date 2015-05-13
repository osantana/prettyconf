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
        line = line.split('#', 1)[0].strip()

        if not line or line.startswith('#') or '=' not in line:
            raise ValueError("Invalid line format (key=value)")

        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('\'"')
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
