import os
import shutil
import tempfile

import pytest


@pytest.fixture
def files_path():
    return os.path.join(os.path.dirname(__file__), "files")


@pytest.fixture
def inifile(files_path):
    return os.path.join(files_path, "config.ini")


@pytest.fixture
def envfile(files_path):
    return os.path.join(files_path, "envfile")


@pytest.fixture
def envfile_content():
    return ("ENVFILE=Environment File Value\n"
            "ENVVAR=Must be overrided")


@pytest.fixture
def inifile_content():
    return ("[settings]\n"
            "INIFILE=INI File Value\n"
            "ENVFILE=Must be overrided")


@pytest.fixture
def config_files(files_path, envfile_content, inifile_content):
    with open(os.path.join(files_path, "..", ".env"), "w") as envfile:
        envfile.write(envfile_content)

    with open(os.path.join(files_path, "..", "settings.ini"), "w") as inifile:
        inifile.write(inifile_content)

    yield envfile, inifile

    os.remove(envfile.name)
    os.remove(inifile.name)


class Creator:
    def __init__(self):
        self.filenames = []
        self.dirs = []

    def create(self, filename, content=""):
        with open(filename, "a") as settings_file:
            settings_file.write(content)
        self.filenames.append(filename)

    def createtmpdir(self):
        directory = tempfile.mkdtemp()
        self.dirs.append(directory)
        return directory

    def remove(self):
        for filename in self.filenames:
            os.remove(filename)

        for directory in self.dirs:
            shutil.rmtree(directory)


@pytest.fixture
def creator():
    creator = Creator()
    yield creator
    creator.remove()
