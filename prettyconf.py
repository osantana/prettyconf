# coding: utf-8

import os

from glob import glob
from shlex import shlex
from ConfigParser import SafeConfigParser as ConfigParser
import sys


class ConfigurationException(Exception):
    pass


class InvalidConfigurationFile(ConfigurationException):
    pass


class InvalidPath(ConfigurationException):
    pass


class UnknownConfiguration(ConfigurationException):
    pass


class AbstractConfig(object):
    def __contains__(self, item):
        raise NotImplementedError()

    def __getitem__(self, item):
        raise NotImplementedError()


class EnvVarConfig(AbstractConfig):
    def __contains__(self, item):
        return item in os.environ

    def __getitem__(self, item):
        return os.environ[item]


class AbstractFileConfig(AbstractConfig):
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


class EnvFileConfig(AbstractFileConfig):
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


class IniFileConfig(AbstractFileConfig):
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
        return self.parser.get(self.section, item)


class ConfigFilesDiscovery(object):
    default_filetypes = (EnvFileConfig, IniFileConfig)

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


class Config(object):
    def __init__(self, configs=None, starting_path=None):
        if configs is None:
            configs = [EnvVarConfig()]
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
        discovery = ConfigFilesDiscovery(self.starting_path)
        self.configurations.extend(discovery.config_files)

    def __call__(self, item, cast=lambda v: v, **kwargs):
        for configuration in self.configurations:
            try:
                return cast(configuration[item])
            except KeyError:
                continue

        if "default" not in kwargs:
            raise UnknownConfiguration("Configuration '{}' not found".format(item))

        return cast(kwargs["default"])

# Use from prettyconf import config
config = Config()
