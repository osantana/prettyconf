# coding: utf-8
from __future__ import unicode_literals

from testfixtures import TempDirectory

from prettyconf.exceptions import InvalidConfigurationFile

from .base import BaseTestCase


class IniFileConfigurationLoaderTestCase(BaseTestCase):

    def setUp(self):
        super(IniFileConfigurationLoaderTestCase, self).setUp()
        self.tmp_dir = TempDirectory()

    def tearDown(self):
        super(IniFileConfigurationLoaderTestCase, self).tearDown()
        self.tmp_dir.cleanup_all()

    def test_skip_invalid_ini_file(self):
        from prettyconf.loaders import IniFileConfigurationLoader

        test_file = self.tmp_dir.write('some/strange/config.cfg', '*&ˆ%$#$%ˆ&*('.encode('utf8'))
        with self.assertRaises(InvalidConfigurationFile):
            IniFileConfigurationLoader(test_file)
