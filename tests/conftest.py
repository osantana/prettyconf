import os

import pytest

from prettyconf.loaders import CommandLine
from .factory import parser_factory

ENVFILE_CONTENT = """
ENVFILE=Environment File Value
ENVVAR=Must be overrided
"""

INIFILE_CONTENT = """
[settings]
INIFILE=INI File Value
ENVFILE=Must be overrided
"""


@pytest.fixture
def files_path():
    return os.path.join(os.path.dirname(__file__), "files")


@pytest.fixture
def inifile(files_path):
    return os.path.join(files_path, "config.ini")


@pytest.fixture
def envfile(files_path):
    return os.path.join(files_path, "envfile")


def parse_args():
    parser = parser_factory()
    return parser.parse_args([])


@pytest.fixture
def command_line_config():
    parser = parser_factory()
    parser.parse_args = parse_args
    return CommandLine(parser=parser)


def _create_file(filename, content):
    with open(filename, "a") as file_:
        file_.write(content)


@pytest.fixture
def env_config(files_path):
    envfile = files_path + "/../.env"
    _create_file(envfile, ENVFILE_CONTENT)

    yield envfile

    os.remove(envfile)


@pytest.fixture
def ini_config(files_path):
    inifile = files_path + "/../settings.ini"
    _create_file(inifile, INIFILE_CONTENT)

    yield inifile

    os.remove(inifile)
