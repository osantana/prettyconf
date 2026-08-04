import pytest

from prettyconf import exceptions

DEPRECATED_NAMES = [
    ('ConfigurationException', exceptions.ConfigurationError),
    ('InvalidConfigurationFile', exceptions.InvalidConfigurationFileError),
    ('MissingSettingsSection', exceptions.MissingSettingsSectionError),
    ('InvalidPath', exceptions.InvalidPathError),
    ('UnknownConfiguration', exceptions.UnknownConfigurationError),
    ('InvalidConfiguration', exceptions.InvalidConfigurationError),
]


@pytest.mark.parametrize(('old_name', 'replacement'), DEPRECATED_NAMES)
def test_deprecated_name_is_an_alias_of_its_replacement(old_name, replacement):
    with pytest.warns(DeprecationWarning, match=replacement.__name__):
        assert getattr(exceptions, old_name) is replacement


def test_deprecated_name_still_catches_what_the_library_raises():
    with pytest.warns(DeprecationWarning, match='UnknownConfigurationError'):
        old_name = exceptions.UnknownConfiguration

    with pytest.raises(old_name):
        raise exceptions.UnknownConfigurationError('not found')


def test_unknown_attribute_raises_attribute_error():
    with pytest.raises(AttributeError):
        getattr(exceptions, 'ThereIsNoSuchException')  # noqa: B009 - the attribute access is what is under test
