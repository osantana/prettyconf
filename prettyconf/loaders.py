import os
from configparser import ConfigParser, MissingSectionHeaderError, NoOptionError
from glob import glob

try:
    import boto3
    import botocore
except ImportError:
    boto3 = None

from .exceptions import InvalidConfigurationFile, InvalidPath, MissingSettingsSection
from .parsers import EnvFileParser


class NotSet(str):
    """
    A special type that behaves as a replacement for None.
    We have to put a new default value to know if a variable has been set by
    the user explicitly. This is useful for the ``CommandLine`` loader, when
    CLI parsers force you to set a default value, and thus, break the discovery
    chain.
    """

    pass


NOT_SET = NotSet()


def get_args(parser):
    """
    Converts arguments extracted from a parser to a dict,
    and will dismiss arguments which default to NOT_SET.

    :param parser: an ``argparse.ArgumentParser`` instance.
    :type parser: argparse.ArgumentParser
    :return: Dictionary with the configs found in the parsed CLI arguments.
    :rtype: dict
    """
    args = vars(parser.parse_args()).items()
    return {key: val for key, val in args if not isinstance(val, NotSet)}


class AbstractConfigurationLoader:
    def __repr__(self):
        raise NotImplementedError()  # pragma: no cover

    def __contains__(self, item):
        raise NotImplementedError()  # pragma: no cover

    def __getitem__(self, item):
        raise NotImplementedError()  # pragma: no cover

    def check(self):
        return True


# noinspection PyAbstractClass
class AbstractConfigurationFileLoader(AbstractConfigurationLoader):
    file_filters = ()


class CommandLine(AbstractConfigurationLoader):
    """
    Extract configuration from an ``argparse`` parser.
    """

    # noinspection PyShadowingNames
    def __init__(self, parser, get_args=get_args):
        """
        :param parser: An `argparse` parser instance to extract variables from.
        :param function get_args: A function to extract args from the parser.
        :type parser: argparse.ArgumentParser
        """
        self.parser = parser
        self.configs = get_args(self.parser)

    def __repr__(self):
        return "CommandLine(parser={})".format(self.parser)

    def __contains__(self, item):
        return item in self.configs

    def __getitem__(self, item):
        return self.configs[item]


class IniFile(AbstractConfigurationFileLoader):
    file_extensions = ("*.ini", "*.cfg")

    def __init__(self, filename, section="settings", var_format=lambda x: x):
        """
        :param str filename: Path to the ``.ini/.cfg`` file.
        :param str section: Section name inside the config file.
        :param function var_format: A function to pre-format variable names.
        """
        self.filename = filename
        self.section = section
        self.var_format = var_format
        self.parser = ConfigParser(allow_no_value=True)
        self._initialized = False

    def __repr__(self):
        return 'IniFile("{}")'.format(self.filename)

    def _parse(self):
        if self._initialized:
            return

        with open(self.filename) as inifile:
            try:
                self.parser.read_file(inifile)
            except (UnicodeDecodeError, MissingSectionHeaderError):
                raise InvalidConfigurationFile()

        if not self.parser.has_section(self.section):
            raise MissingSettingsSection("Missing [{}] section in {}".format(self.section, self.filename))

        self._initialized = True

    def check(self):
        try:
            self._parse()
        except (FileNotFoundError, InvalidConfigurationFile, MissingSettingsSection):
            return False

        return super().check()

    def __contains__(self, item):
        if not self.check():
            return False

        return self.parser.has_option(self.section, self.var_format(item))

    def __getitem__(self, item):
        if not self.check():
            raise KeyError("{!r}".format(item))

        try:
            return self.parser.get(self.section, self.var_format(item))
        except NoOptionError:
            raise KeyError("{!r}".format(item))


class Environment(AbstractConfigurationLoader):
    """
    Get's configuration from the environment, by inspecting ``os.environ``.
    """

    def __init__(self, var_format=str.upper):
        """
        :param function var_format: A function to pre-format variable names.
        """
        self.var_format = var_format

    def __repr__(self):
        return "Environment(var_format={})".format(self.var_format)

    def __contains__(self, item):
        return self.var_format(item) in os.environ

    def __getitem__(self, item):
        # Uses `os.environ` because it raises an exception if the environmental
        # variable does not exist, whilst `os.getenv` doesn't.
        return os.environ[self.var_format(item)]


class EnvFile(AbstractConfigurationFileLoader):
    file_extensions = (".env",)

    def __init__(self, filename=".env", var_format=str.upper):
        """
        :param str filename: Path to the ``.env`` file.
        :param function var_format: A function to pre-format variable names.
        """
        self.filename = filename
        self.var_format = var_format
        self.configs = None

    def __repr__(self):
        return 'EnvFile("{}")'.format(self.filename)

    def _parse(self):
        if self.configs is not None:
            return

        self.configs = {}
        with open(self.filename) as envfile:
            self.configs.update(EnvFileParser(envfile).parse_config())

    def check(self):
        if not os.path.isfile(self.filename):
            return False

        try:
            self._parse()
        except FileNotFoundError:
            return False

        return super().check()

    def __contains__(self, item):
        if not self.check():
            return False

        return self.var_format(item) in self.configs

    def __getitem__(self, item):
        if not self.check():
            raise KeyError("{!r}".format(item))

        return self.configs[self.var_format(item)]


class RecursiveSearch(AbstractConfigurationLoader):
    def __init__(self, starting_path=None, filetypes=((".env", EnvFile), (("*.ini", "*.cfg"), IniFile)), root_path="/"):
        """
        :param str starting_path: The path to begin looking for configuration files.
        :param tuple filetypes: tuple of tuples with configuration loaders, order matters.
                                Defaults to
                                ``(('*.env', EnvFile), (('*.ini', *.cfg',), IniFile)``
        :param str root_path: Configuration lookup will stop at the given path. Defaults to
                              the current user directory
        """
        self.root_path = os.path.realpath(root_path)
        self._starting_path = self.root_path

        if starting_path:
            self.starting_path = starting_path

        self.filetypes = filetypes
        self._config_files = None

    @property
    def starting_path(self):
        return self._starting_path

    @starting_path.setter
    def starting_path(self, path):
        if not path:
            raise InvalidPath("Invalid starting path")

        path = os.path.realpath(os.path.abspath(path))
        if not path.startswith(self.root_path):
            raise InvalidPath("Invalid root path given")
        self._starting_path = path

    @staticmethod
    def get_filenames(path, patterns):
        filenames = []
        if type(patterns) is str:
            patterns = (patterns,)

        for pattern in patterns:
            filenames += glob(os.path.join(path, pattern))
        return filenames

    def _scan_path(self, path):
        config_files = []

        for patterns, Loader in self.filetypes:
            for filename in self.get_filenames(path, patterns):
                try:
                    loader = Loader(filename=filename)
                    if not loader.check():
                        continue
                    config_files.append(loader)
                except InvalidConfigurationFile:
                    continue

        return config_files

    def _discover(self):
        self._config_files = []

        path = self.starting_path
        while True:
            if os.path.isdir(path):
                self._config_files += self._scan_path(path)

            if path == self.root_path:
                break

            path = os.path.dirname(path)

    @property
    def config_files(self):
        if self._config_files is None:
            self._discover()

        return self._config_files

    def __repr__(self):
        return "RecursiveSearch(starting_path={})".format(self.starting_path)

    def __contains__(self, item):
        for config_file in self.config_files:
            if item in config_file:
                return True
        return False

    def __getitem__(self, item):
        for config_file in self.config_files:
            try:
                return config_file[item]
            except KeyError:
                continue
        else:
            raise KeyError("{!r}".format(item))


class AwsParameterStore(AbstractConfigurationLoader):
    def __init__(self, path="/", aws_access_key_id=None, aws_secret_access_key=None, region_name="us-east-1", endpoint_url=None):
        if not boto3:
            raise RuntimeError(
                'AwsParameterStore requires [aws] feature. Please install it: "pip install prettyconf[aws]"'
            )

        self.path = path
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.endpoint_url = endpoint_url
        self._fetched = False
        self._parameters = {}

    def _store_parameters(self, parameters):
        for parameter in parameters:
            self._parameters[parameter["Name"].split("/")[-1]] = parameter["Value"]

    def _fetch_parameters(self):
        if self._fetched:
            return

        client = boto3.client(
            service_name="ssm",
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name,
            endpoint_url=self.endpoint_url,
        )

        response = client.get_parameters_by_path(Path=self.path)
        next_token = response.get("NextToken")
        self._store_parameters(response["Parameters"])

        while next_token:
            response = client.get_parameters_by_path(Path=self.path, NextToken=next_token)
            next_token = response.get("NextToken")
            self._store_parameters(response["Parameters"])

        self._fetched = True

    def check(self):
        try:
            self._fetch_parameters()
        except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError):
            return False

        return super().check()

    def __repr__(self):
        return "AwsParameterStore(path={} region={})".format(self.path, self.region_name)

    def __contains__(self, item):
        if not self.check():
            return False

        return item in self._parameters

    def __getitem__(self, item):
        if not self.check():
            raise KeyError("{!r}".format(item))

        return self._parameters[item]
