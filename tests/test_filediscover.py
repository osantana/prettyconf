# coding: utf-8


import os

from .base import BaseTestCase
from prettyconf.configuration import ConfigurationDiscovery
from prettyconf.exceptions import InvalidPath


class ConfigFilesDiscoveryTestCase(BaseTestCase):
    def setUp(self):
        super(ConfigFilesDiscoveryTestCase, self).setUp()
        self._create_file(self.test_files_path + "/../.env")
        self._create_file(self.test_files_path + "/../setup.cfg")  # invalid settings
        self._create_file(self.test_files_path + "/../settings.ini", "[settings]")
        self._create_file(self.test_files_path + "/../../.env")

    def test_config_file_parsing(self):
        discovery = ConfigurationDiscovery(os.path.dirname(self.test_files_path))
        self.assertEqual(len(discovery.config_files), 3)  # 3 *valid* files created at .setUp()

    def test_abort_discovery_from_invalid_path(self):
        with self.assertRaises(InvalidPath):
            # filename is not a valid starting path...
            _ = ConfigurationDiscovery(self.test_files_path + "/.env").config_files

        with self.assertRaises(InvalidPath):
            # ... and missing path either
            _ = ConfigurationDiscovery(self.test_files_path + "/missing").config_files
