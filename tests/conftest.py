import os

import pytest

from prettyconf.loaders import CommandLine
from .factory import parser_factory


@pytest.fixture
def files_path():
    return os.path.join(os.path.dirname(__file__), "files")


@pytest.fixture
def inifile(files_path):
    return os.path.join(files_path, "config.ini")


def parse_args():
    parser = parser_factory()
    return parser.parse_args([])


@pytest.fixture
def command_line_config():
    parser = parser_factory()
    parser.parse_args = parse_args
    return CommandLine(parser=parser)
