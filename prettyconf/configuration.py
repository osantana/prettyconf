# coding: utf-8


import os
import sys

from .loaders import EnvFileConfigurationLoader, IniFileConfigurationLoader, EnvVarConfigurationLoader
from .exceptions import InvalidConfigurationFile, InvalidPath, InvalidConfigurationCast, UnknownConfiguration
from .casts import Boolean, List, Option


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
    # Shortcut for standard casts
    boolean = Boolean
    list = List
    option = Option

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
