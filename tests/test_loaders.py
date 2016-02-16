# coding: utf-8

from __future__ import unicode_literals

import tempfile

from prettyconf.exceptions import InvalidConfigurationFile
from .base import BaseTestCase


class IniFileConfigurationLoaderTestCase(BaseTestCase):
    def test_skip_invalid_ini_file(self):
        from prettyconf.loaders import IniFileConfigurationLoader

        with tempfile.NamedTemporaryFile() as temp:
            temp.write(u'*&ˆ%$#$%ˆ&*('.encode("utf-8"))

            with self.assertRaises(InvalidConfigurationFile):
                IniFileConfigurationLoader(temp.name)
