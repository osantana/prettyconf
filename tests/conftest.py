import importlib.util
import shutil
import tempfile
from pathlib import Path

import pytest

from prettyconf.loaders import CommandLine

from .factory import parser_factory

collect_ignore = []
if importlib.util.find_spec('botocore') is None:
    collect_ignore.append('test_parameterstore.py')

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
    return Path(__file__).parent / 'files'


@pytest.fixture
def inifile(files_path):
    return files_path / 'config.ini'


@pytest.fixture
def envfile(files_path):
    return files_path / 'envfile'


def parse_args():
    parser = parser_factory()
    return parser.parse_args([])


@pytest.fixture
def command_line_config():
    parser = parser_factory()
    parser.parse_args = parse_args
    return CommandLine(parser=parser)


def _create_file(filename, content=''):
    with Path(filename).open('a') as file_:
        file_.write(content)


@pytest.fixture
def create_file():
    remove_list = []

    def _create_fixture_file(filename, content=''):
        _create_file(filename, content)
        remove_list.append(Path(filename))

    yield _create_fixture_file

    for file in remove_list:
        file.unlink()


@pytest.fixture
def create_dir():
    tempdir = Path(tempfile.mkdtemp())

    def _create_tempdir(path=''):
        full_path = tempdir / path
        full_path.mkdir(parents=True, exist_ok=True)
        return tempdir, full_path

    yield _create_tempdir

    shutil.rmtree(tempdir)


@pytest.fixture
def env_config(files_path):
    envfile = files_path.parent / '.env'
    _create_file(envfile, ENVFILE_CONTENT)

    yield envfile

    envfile.unlink()


@pytest.fixture
def ini_config(files_path):
    inifile = files_path.parent / 'settings.ini'
    _create_file(inifile, INIFILE_CONTENT)

    yield inifile

    inifile.unlink()
