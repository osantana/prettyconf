# coding: utf-8


import os

from .base import BaseTestCase
from prettyconf.configuration import ConfigurationDiscovery
from prettyconf.exceptions import InvalidPath


class ConfigFilesDiscoveryTestCase(BaseTestCase):
    def setUp(self):
        super(ConfigFilesDiscoveryTestCase, self).setUp()

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
