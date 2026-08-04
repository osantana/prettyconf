import warnings


class ConfigurationError(Exception):
    pass


class InvalidConfigurationFileError(ConfigurationError):
    pass


class MissingSettingsSectionError(InvalidConfigurationFileError):
    pass


class InvalidPathError(ConfigurationError):
    pass


class UnknownConfigurationError(ConfigurationError):
    pass


class InvalidConfigurationError(ConfigurationError):
    pass


_DEPRECATED_NAMES = {
    'ConfigurationException': ConfigurationError,
    'InvalidConfigurationFile': InvalidConfigurationFileError,
    'MissingSettingsSection': MissingSettingsSectionError,
    'InvalidPath': InvalidPathError,
    'UnknownConfiguration': UnknownConfigurationError,
    'InvalidConfiguration': InvalidConfigurationError,
}


def __getattr__(name):
    if name not in _DEPRECATED_NAMES:
        raise AttributeError(f'module {__name__!r} has no attribute {name!r}')

    replacement = _DEPRECATED_NAMES[name]
    warnings.warn(
        f'{name} is deprecated and will be removed in a future release. Use {replacement.__name__} instead.',
        DeprecationWarning,
        stacklevel=2,
    )
    return replacement
