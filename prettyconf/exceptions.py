# coding: utf-8


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
