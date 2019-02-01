import os
import shutil
import tempfile

from prettyconf.exceptions import InvalidPath
from prettyconf.loaders import RecursiveSearch
from .base import BaseTestCase


class RecursiveSearchTestCase(BaseTestCase):
    def setUp(self):
        super(RecursiveSearchTestCase, self).setUp()
        self.tmpdirs = []

    def tearDown(self):
        super(RecursiveSearchTestCase, self).tearDown()
        for tmpdir in self.tmpdirs:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_config_file_parsing(self):
        self._create_file(self.test_files_path + "/../.env")
        self._create_file(self.test_files_path + "/../setup.txt")  # invalid settings
        self._create_file(self.test_files_path + "/../settings.ini", "[settings]\nFOO=bar")
        discovery = RecursiveSearch(os.path.dirname(self.test_files_path))
        self.assertTrue(repr(discovery).startswith("RecursiveSearch(starting_path="))
        self.assertEqual(len(discovery.config_files), 2)  # 2 *valid* files created

        self.assertIn('FOO', discovery)
        self.assertEqual(discovery['FOO'], 'bar')
        self.assertNotIn('not_found', discovery)

    def test_should_not_look_for_parent_directory_when_it_finds_valid_configurations(self):
        starting_path = self.test_files_path + '/recursive/valid/'
        discovery = RecursiveSearch(starting_path, root_path=self.test_files_path)
        self.assertEqual(len(discovery.config_files), 3)
        filenames = [cfg.filename for cfg in discovery.config_files]
        self.assertIn(starting_path + '.env', filenames)
        self.assertIn(starting_path + 'settings.ini', filenames)

    def test_should_look_for_parent_directory_when_it_finds_invalid_configurations(self):
        starting_path = self.test_files_path + '/recursive/valid/invalid/'
        valid_path = self.test_files_path + '/recursive/valid/'
        discovery = RecursiveSearch(starting_path, root_path=self.test_files_path)
        self.assertEqual(len(discovery.config_files), 3)
        filenames = [cfg.filename for cfg in discovery.config_files]
        self.assertIn(valid_path + '.env', filenames)
        self.assertIn(valid_path + 'settings.ini', filenames)

    def test_default_root_path_should_default_to_root_directory(self):
        discovery = RecursiveSearch(os.path.dirname(self.test_files_path))
        assert discovery.root_path == "/"

    def test_root_path_should_be_parent_of_starting_path(self):
        with self.assertRaises(InvalidPath):
            RecursiveSearch('/foo', root_path='/foo/bar/baz/')

    def test_use_configuration_from_root_path_when_no_other_was_found(self):
        root_dir = tempfile.mkdtemp()
        self.tmpdirs.append(root_dir)

        start_path = os.path.join(root_dir, 'start/here')
        os.makedirs(start_path)

        test_file = os.path.realpath(os.path.join(root_dir, 'settings.ini'))
        with open(test_file, 'a') as file_:
            file_.write('[settings]')
        self.files.append(test_file)  # Required to removed it at tearDown

        discovery = RecursiveSearch(start_path, root_path=root_dir)
        filenames = [cfg.filename for cfg in discovery.config_files]
        self.assertEqual([test_file], filenames)

    def test_lookup_should_stop_at_root_path(self):
        test_dir = tempfile.mkdtemp()
        self.tmpdirs.append(test_dir)  # Cleanup dir at tearDown

        start_path = os.path.join(test_dir, 'some', 'dirs', 'without', 'config')
        os.makedirs(start_path)

        # create a file in the test_dir
        test_file = os.path.realpath(os.path.join(test_dir, 'settings.ini'))
        with open(test_file, 'a') as file_:
            file_.write('[settings]')
        self.files.append(test_file)  # Required to removed it at tearDown

        root_dir = os.path.join(test_dir, 'some', 'dirs')  # No settings here

        discovery = RecursiveSearch(start_path, root_path=root_dir)
        self.assertEqual(discovery.config_files, [])

    def test_config_file_fallback_loading(self):
        self._create_file(self.test_files_path + "/../.env", "SPAM=eggs")
        self._create_file(self.test_files_path + "/../settings.ini", "[settings]\nFOO=bar")
        discovery = RecursiveSearch(os.path.dirname(self.test_files_path))

        self.assertEqual(discovery['FOO'], 'bar')
        self.assertEqual(discovery['SPAM'], 'eggs')

    def test_config_file_fallback_loading_skipping_empty_settings(self):
        self._create_file(self.test_files_path + "/../.env", "SPAM=eggs\nFOO=bar")
        self._create_file(self.test_files_path + "/../settings.ini", "[no_settings_session]\nFOO=not_bar")

        discovery = RecursiveSearch(os.path.dirname(self.test_files_path))

        self.assertEqual(discovery['FOO'], 'bar')
        self.assertEqual(discovery['SPAM'], 'eggs')
