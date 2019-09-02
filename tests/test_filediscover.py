import os

import pytest

from prettyconf.exceptions import InvalidPath
from prettyconf.loaders import RecursiveSearch


def test_config_file_parsing(create_file, files_path):
    create_file(files_path + "/../.env")
    create_file(files_path + "/../setup.txt")  # invalid settings
    create_file(files_path + "/../settings.ini", "[settings]\nFOO=bar")
    discovery = RecursiveSearch(os.path.dirname(files_path))

    assert repr(discovery).startswith("RecursiveSearch(starting_path=")
    assert len(discovery.config_files) == 2  # 2 *valid* files created

    assert 'FOO' in discovery
    assert discovery['FOO'] == 'bar'
    assert 'not_found' not in discovery


def test_should_not_look_for_parent_directory_when_it_finds_valid_configurations(files_path):
    starting_path = files_path + '/recursive/valid/'
    discovery = RecursiveSearch(starting_path, root_path=files_path)
    assert len(discovery.config_files) == 3

    filenames = [cfg.filename for cfg in discovery.config_files]
    assert starting_path + '.env' in filenames
    assert starting_path + 'settings.ini' in filenames


def test_should_look_for_parent_directory_when_it_finds_invalid_configurations(files_path):
    starting_path = files_path + '/recursive/valid/invalid/'
    valid_path = files_path + '/recursive/valid/'
    discovery = RecursiveSearch(starting_path, root_path=files_path)
    assert len(discovery.config_files) == 3

    filenames = [cfg.filename for cfg in discovery.config_files]
    assert valid_path + '.env' in filenames
    assert valid_path + 'settings.ini' in filenames


def test_default_root_path_should_default_to_root_directory(files_path):
    discovery = RecursiveSearch(os.path.dirname(files_path))
    assert discovery.root_path == "/"


def test_root_path_should_be_parent_of_starting_path():
    with pytest.raises(InvalidPath):
        RecursiveSearch('/foo', root_path='/foo/bar/baz/')


def test_use_configuration_from_root_path_when_no_other_was_found(create_dir):
    root_dir, start_path = create_dir("start/here")

    test_file = os.path.realpath(os.path.join(root_dir, 'settings.ini'))
    with open(test_file, 'a') as file_:
        file_.write('[settings]')

    discovery = RecursiveSearch(start_path, root_path=root_dir)
    filenames = [cfg.filename for cfg in discovery.config_files]
    assert [test_file] == filenames


def test_lookup_should_stop_at_root_path(create_dir):
    test_dir, start_path = create_dir("some/dirs/without/config")

    # create a file in the test_dir
    test_file = os.path.realpath(os.path.join(test_dir, 'settings.ini'))
    with open(test_file, 'a') as file_:
        file_.write('[settings]')

    root_dir = os.path.join(test_dir, 'some', 'dirs')  # No settings here

    discovery = RecursiveSearch(start_path, root_path=root_dir)
    assert discovery.config_files == []


def test_config_file_fallback_loading(create_file, files_path):
    create_file(files_path + "/../.env", "SPAM=eggs")
    create_file(files_path + "/../settings.ini", "[settings]\nFOO=bar")
    discovery = RecursiveSearch(os.path.dirname(files_path))

    assert discovery['FOO'] == 'bar'
    assert discovery['SPAM'] == 'eggs'


def test_config_file_fallback_loading_skipping_empty_settings(create_file, files_path):
    create_file(files_path + "/../.env", "SPAM=eggs\nFOO=bar")
    create_file(files_path + "/../settings.ini", "[no_settings_session]\nFOO=not_bar")

    discovery = RecursiveSearch(os.path.dirname(files_path))

    assert discovery['FOO'] == 'bar'
    assert discovery['SPAM'] == 'eggs'


def test_env_dir_wont_break_loader(files_path):
    env_directory = os.path.join(files_path, "..", ".env")
    os.makedirs(env_directory, exist_ok=True)
    try:
        discovery = RecursiveSearch(os.path.dirname(files_path))
    finally:
        os.removedirs(env_directory)

    assert 'FOO' not in discovery
