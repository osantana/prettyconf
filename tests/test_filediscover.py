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
        self.assertEqual(len(discovery.config_files), 2)  # 3 *valid* files created at .setUp()

    def test_abort_discovery_from_invalid_path(self):
        with self.assertRaises(InvalidPath):
            # filename is not a valid starting path...
            ConfigurationDiscovery(self.test_files_path + "/.env").config_files

        with self.assertRaises(InvalidPath):
            # ... and missing path either
            ConfigurationDiscovery(self.test_files_path + "/missing").config_files

    def test_should_look_for_parent_directory_until_find_valid_configurations(self):
        self._create_file(self.test_files_path + '/../../.env')
        self._create_file(self.test_files_path + '/../.env')

        discovery = ConfigurationDiscovery(os.path.dirname(self.test_files_path))
        self.assertEqual(len(discovery.config_files), 1)
