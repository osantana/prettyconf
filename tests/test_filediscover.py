# coding: utf-8
from __future__ import unicode_literals

import os

from testfixtures import TempDirectory

from .base import BaseTestCase
from prettyconf.configuration import ConfigurationDiscovery
from prettyconf.exceptions import InvalidPath
from prettyconf.loaders import IniFileConfigurationLoader


# noinspection PyStatementEffect
class ConfigFilesDiscoveryTestCase(BaseTestCase):
    def setUp(self):
        super(ConfigFilesDiscoveryTestCase, self).setUp()
        self.tmpdirs = []

    def tearDown(self):
        super(ConfigFilesDiscoveryTestCase, self).tearDown()
        for tmpdir in self.tmpdirs:
            tmpdir.cleanup_all()

    def test_config_file_parsing(self):
        self._create_file(self.test_files_path + "/../.env")
        self._create_file(self.test_files_path + "/../setup.cfg")  # invalid settings
        self._create_file(self.test_files_path + "/../settings.ini", "[settings]")
        discovery = ConfigurationDiscovery(os.path.dirname(self.test_files_path))
        self.assertEqual(len(discovery.config_files), 2)  # 2 *valid* files created

    def test_abort_discovery_from_invalid_path(self):
        self._create_file(self.test_files_path + '/.env')
        with self.assertRaises(InvalidPath):
            # filename is not a valid starting path...
            ConfigurationDiscovery(self.test_files_path + "/.env").config_files

    def test_abort_discovery_with_non_existing_path(self):
        with self.assertRaises(InvalidPath):
            # ... and missing path either
            ConfigurationDiscovery(self.test_files_path + "/missing").config_files

    def test_should_not_look_for_parent_directory_when_it_finds_valid_configurations(self):
        self._create_file(self.test_files_path + '/../../settings.ini', '[settings]')
        self._create_file(self.test_files_path + '/../../.env')
        self._create_file(self.test_files_path + '/../.env')
        self._create_file(self.test_files_path + '/../settings.ini', '[settings]')

        discovery = ConfigurationDiscovery(os.path.dirname(self.test_files_path))
        self.assertEqual(len(discovery.config_files), 2)
        filenames = [cfg.filename for cfg in discovery.config_files]
        self.assertIn(os.path.abspath(self.test_files_path + '/../.env'), filenames)
        self.assertIn(os.path.abspath(self.test_files_path + '/../settings.ini'), filenames)

    def test_should_look_for_parent_directory_when_it_finds_invalid_configurations(self):
        self._create_file(self.test_files_path + '/../../settings.ini', '[settings]')
        self._create_file(self.test_files_path + '/../../.env')
        self._create_file(self.test_files_path + '/../invalid.cfg', '')
        self._create_file(self.test_files_path + '/../settings.ini', '')

        discovery = ConfigurationDiscovery(os.path.dirname(self.test_files_path))
        self.assertEqual(len(discovery.config_files), 2)
        filenames = [cfg.filename for cfg in discovery.config_files]
        self.assertIn(os.path.abspath(self.test_files_path + '/../../.env'), filenames)
        self.assertIn(os.path.abspath(self.test_files_path + '/../../settings.ini'), filenames)

    def test_default_root_path_should_default_to_root_directory(self):
        discovery = ConfigurationDiscovery(os.path.dirname(self.test_files_path))
        assert discovery.root_path == "/"

    def test_root_path_should_be_parent_of_starting_path(self):
        with self.assertRaises(InvalidPath):
            ConfigurationDiscovery('/foo', root_path='/foo/bar/baz/')

    def test_use_configuration_from_root_path_when_no_other_was_found(self):
        root_dir = TempDirectory()
        self.tmpdirs.append(root_dir)

        start_path = root_dir.makedir('some/directories/to/start/looking/for/settings')
        test_file = os.path.realpath(os.path.join(root_dir.path, 'settings.ini'))
        with open(test_file, 'a') as file_:
            file_.write('[settings]')
        self.files.append(test_file)  # Required to removed it at tearDown

        discovery = ConfigurationDiscovery(start_path, root_path=root_dir.path)
        filenames = [cfg.filename for cfg in discovery.config_files]
        self.assertEqual([test_file], filenames)

    def test_lookup_should_stop_at_root_path(self):
        test_dir = TempDirectory()
        self.tmpdirs.append(test_dir)  # Cleanup dir at tearDown

        start_path = test_dir.makedir('some/dirs/without/config')

        # create a file in the test_dir
        test_file = os.path.realpath(os.path.join(test_dir.path, 'settings.ini'))
        with open(test_file, 'a') as file_:
            file_.write('[settings]')
        self.files.append(test_file)  # Required to removed it at tearDown

        root_dir = os.path.join(test_dir.path, 'some', 'dirs')  # No settings here

        discovery = ConfigurationDiscovery(start_path, root_path=root_dir)
        self.assertEqual(discovery.config_files, [])

    def test_inifile_discovery_should_ignore_invalid_files_without_raising_exception(self):
        root_dir = TempDirectory()
        self.tmpdirs.append(root_dir)

        cfg_file = root_dir.write(('some', 'strange', 'config.cfg'), '&ˆ%$#$%ˆ&*()(*&ˆ'.encode('utf8'))
        root_dir.write(('some', 'config.ini'), '$#%ˆ&*((*&ˆ%'.encode('utf8'))

        discovery = ConfigurationDiscovery(
            os.path.realpath(os.path.dirname(cfg_file)), filetypes=(IniFileConfigurationLoader, ))

        self.assertEqual(discovery.config_files,  [])
