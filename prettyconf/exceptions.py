class ConfigurationException(Exception):
    pass


class InvalidConfigurationFile(ConfigurationException):
    pass


class MissingSettingsSection(InvalidConfigurationFile):
    pass


class InvalidPath(ConfigurationException):
    pass


class UnknownConfiguration(ConfigurationException):
    pass


class InvalidConfiguration(ConfigurationException):
    pass
