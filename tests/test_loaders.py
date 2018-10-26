import tempfile

import pytest

from prettyconf.exceptions import InvalidConfigurationFile
from prettyconf.loaders import IniFileConfigurationLoader


def test_skip_invalid_ini_file():
    with tempfile.NamedTemporaryFile() as temp:
        temp.write('*&ˆ%$#$%ˆ&*('.encode("utf-8"))

        with pytest.raises(InvalidConfigurationFile):
            IniFileConfigurationLoader(temp.name)
