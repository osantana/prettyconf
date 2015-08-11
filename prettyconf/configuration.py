# coding: utf-8


import os
import sys

from .loaders import EnvFileConfigurationLoader, IniFileConfigurationLoader, EnvVarConfigurationLoader
from .exceptions import InvalidConfigurationFile, InvalidPath, InvalidConfigurationCast, UnknownConfiguration
from .casts import Boolean, List, Option


MAGIC_FRAME_DEPTH = 3


class ConfigurationDiscovery(object):
    default_filetypes = (EnvFileConfigurationLoader, IniFileConfigurationLoader)

    def __init__(self, starting_path, filetypes=None, root_path="/"):
        """
        Setup the configuration file discovery.

        :param starting_path: The path to begin looking for configuration files
        :param filetypes: tuple with configuration loaders. Defaults to
                          ``(EnvFileConfigurationLoader, IniFileConfigurationLoader)``
        :param root_path: Configuration lookup will stop at the given path. Defaults to
                          the current user directory
        """
        self.starting_path = os.path.realpath(os.path.abspath(starting_path))
        self.root_path = os.path.realpath(root_path)

        if not self.starting_path.startswith(self.root_path):
            raise InvalidPath('Invalid root path given')

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

            if self._config_files or path == self.root_path or path == os.path.sep:
                break

            path = os.path.dirname(path)

    @property
    def config_files(self):
        if self._config_files is None:
            self._discover()

        return self._config_files


class Configuration(object):
    # Shortcut for standard casts
    boolean = Boolean()
    list = List()
    option = Option

    def __init__(self, configs=None, starting_path=None, root_path="/"):
        if configs is None:
            configs = [EnvVarConfigurationLoader()]
        self.configurations = configs
        self.starting_path = starting_path
        self.root_path = root_path
        self._initialized = False

    @staticmethod
    def _caller_path():
        # MAGIC! Get the caller's module path.
        # noinspection PyProtectedMember
        frame = sys._getframe(MAGIC_FRAME_DEPTH)
        path = os.path.dirname(frame.f_code.co_filename)
        return path

    def _init_configs(self):
        if self._initialized:
            return

        if self.starting_path is None:
            self.starting_path = self._caller_path()

        discovery = ConfigurationDiscovery(self.starting_path, root_path=self.root_path)
        self.configurations.extend(discovery.config_files)

        self._initialized = True

    def __call__(self, item, cast=lambda v: v, **kwargs):
        if not callable(cast):
            raise InvalidConfigurationCast("Cast must be callable")

        self._init_configs()

        for configuration in self.configurations:
            try:
                return cast(configuration[item])
            except KeyError:
                continue

        if 'default' not in kwargs:
            raise UnknownConfiguration("Configuration '{}' not found".format(item))

        return cast(kwargs["default"])
