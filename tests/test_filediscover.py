import os

import pytest

from prettyconf.configuration import ConfigurationDiscovery
from prettyconf.exceptions import InvalidPath
from prettyconf.loaders import IniFileConfigurationLoader


def test_config_file_parsing(files_path, creator):
    creator.create(os.path.join(files_path, "..", ".env"))
    creator.create(os.path.join(files_path, "..", "setup.cfg"))  # invalid settings
    creator.create(os.path.join(files_path, "..", "settings.ini"), "[settings]")

    discovery = ConfigurationDiscovery(os.path.dirname(files_path))
    assert len(discovery.config_files) == 2  # 2 *valid* files created


def test_should_not_look_for_parent_directory_when_it_finds_valid_configurations(files_path, creator):
    creator.create(os.path.join(files_path, '../../settings.ini'), '[settings]')
    creator.create(os.path.join(files_path, '../../.env'))
    creator.create(os.path.join(files_path, '../.env'))
    creator.create(os.path.join(files_path, '../settings.ini'), '[settings]')

    discovery = ConfigurationDiscovery(os.path.dirname(files_path))
    assert len(discovery.config_files) == 2

    filenames = [cfg.filename for cfg in discovery.config_files]
    assert os.path.abspath(os.path.join(files_path, '..', '.env')) in filenames
    assert os.path.abspath(os.path.join(files_path, '..', 'settings.ini')) in filenames


def test_should_look_for_parent_directory_when_it_finds_invalid_configurations(files_path, creator):
    creator.create(os.path.join(files_path, '..', '..', 'settings.ini'), '[settings]')
    creator.create(os.path.join(files_path, '..', '..', '.env'))
    creator.create(os.path.join(files_path, '..', 'invalid.cfg'), '')
    creator.create(os.path.join(files_path, '..', 'settings.ini'), '')

    discovery = ConfigurationDiscovery(os.path.dirname(files_path))
    assert len(discovery.config_files) == 2

    filenames = [cfg.filename for cfg in discovery.config_files]
    assert os.path.abspath(os.path.join(files_path, '..', '..', '.env')) in filenames
    assert os.path.abspath(os.path.join(files_path, '..', '..', 'settings.ini')) in filenames


def test_default_root_path_should_default_to_root_directory(files_path):
    discovery = ConfigurationDiscovery(os.path.dirname(files_path))
    assert discovery.root_path == "/"


def test_root_path_should_be_parent_of_starting_path():
    with pytest.raises(InvalidPath):
        ConfigurationDiscovery('/foo', root_path='/foo/bar/baz/')


def test_use_configuration_from_root_path_when_no_other_was_found(creator):
    root_dir = creator.createtmpdir()

    start_path = os.path.join(root_dir, 'some/directories/to/start/looking/for/settings')
    os.makedirs(start_path)

    test_file = os.path.realpath(os.path.join(root_dir, 'settings.ini'))
    creator.create(test_file, '[settings]')

    discovery = ConfigurationDiscovery(start_path, root_path=root_dir)
    filenames = [cfg.filename for cfg in discovery.config_files]

    assert [test_file] == filenames


def test_lookup_should_stop_at_root_path(creator):
    test_dir = creator.createtmpdir()
    start_path = os.path.join(test_dir, 'some/dirs/without/config')
    os.makedirs(start_path)

    # create a file in the test_dir
    test_file = os.path.realpath(os.path.join(test_dir, 'settings.ini'))
    creator.create(test_file, '[settings]')

    root_dir = os.path.join(test_dir, 'some', 'dirs')  # No settings here

    discovery = ConfigurationDiscovery(start_path, root_path=root_dir)
    assert discovery.config_files == []


def test_inifile_discovery_should_ignore_invalid_files_without_raising_exception(creator):
    root_dir = creator.createtmpdir()
    cfg_dir = os.path.join(root_dir, "some/strange")
    os.makedirs(cfg_dir)

    creator.create(os.path.join(cfg_dir, "config.cfg"), '&ˆ%$#$%ˆ&*()(*&ˆ')
    creator.create(os.path.join(root_dir, "some/config.ini"), '$#%ˆ&*((*&ˆ%')

    discovery = ConfigurationDiscovery(cfg_dir, filetypes=(IniFileConfigurationLoader,))
    assert discovery.config_files == []
