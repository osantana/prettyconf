# coding: utf-8
import os
import sys
from argparse import Action, ArgumentParser

from .exceptions import InvalidConfigurationFile

try:
    from ConfigParser import SafeConfigParser as ConfigParser, NoOptionError, MissingSectionHeaderError
except ImportError:
    from configparser import ConfigParser, NoOptionError, MissingSectionHeaderError


CLI_DEFAULT = '==PRETTYCONF=='


class AbstractConfigurationLoader(object):
    def __contains__(self, item):
        raise NotImplementedError()  # pragma: no cover

    def __getitem__(self, item):
        raise NotImplementedError()  # pragma: no cover


class CommandLine(AbstractConfigurationLoader):
    """
    Works with `argparse` parsers.
    """
    default = '==PRETTYCONF=='
    def __init__(self, parser):
        # We have to put a special default value so that we know if the
        # variable has been set by the user explicitly.
        _parser = ArgumentParser()
        for action in parser._actions:
            copy = Action(**dict(action._get_kwargs()))
            copy.default = self.default
            _parser._actions.append(copy)
        self.configs = _parser.parse_args()

    def __contains__(self, item):
        return item in self.configs and getattr(self.configs, item) != self.default

    def __getitem__(self, item):
        try:
            res = getattr(self.configs, item)
        except AttributeError:
            raise KeyError("{!r}".format(item))

        if res == self.default:
            raise KeyError("{!r}".format(item))
        return res


class IniFile(AbstractConfigurationLoader):

    def __init__(self, filename, section="settings", required=True, var_format=lambda x: x):
        self.filename = filename
        self.required = required
        self.section = section
        self.var_format = var_format
        self.parser = ConfigParser(allow_no_value=True)
        self.file_is_missing = not os.path.isfile(self.filename)

        if self.required and self.file_is_missing:
            raise InvalidConfigurationFile("Could not find {}".format(self.filename))

        if self.file_is_missing:
            # do not open it
            return

        with open(self.filename) as inifile:
            try:
                if sys.version_info[0] < 3:
                    # ConfigParser.readfp is deprecated for Python3, read_file replaces it
                    # noinspection PyDeprecation
                    self.parser.readfp(inifile)
                else:
                    self.parser.read_file(inifile)
            except (UnicodeDecodeError, MissingSectionHeaderError):
                raise InvalidConfigurationFile()

        if not self.parser.has_section(self.section):
            raise InvalidConfigurationFile("Missing [{}] section in {}".format(self.section, self.filename))

    def __contains__(self, item):
        if self.file_is_missing:
            return False
        return self.parser.has_option(self.section, self.var_format(item))

    def __getitem__(self, item):
        if self.file_is_missing:
            raise KeyError("{!r}".format(item))
        try:
            return self.parser.get(self.section, self.var_format(item))
        except NoOptionError:
            raise KeyError("{!r}".format(item))


class Environment(AbstractConfigurationLoader):
    """
    Get's configuration from the environment.
    """

    def __init__(self, var_format=str.upper):
        self.var_format = var_format

    def __contains__(self, item):
        return self.var_format(item) in os.environ

    def __getitem__(self, item):
        # Uses `os.environ` because it raises an exception if the environmental
        # variable does not exist, whilst `os.getenv` doesn't.
        return os.environ[self.var_format(item)]


class EnvFile(AbstractConfigurationLoader):
    def __init__(self, filename='.env', required=True, var_format=str.upper):
        self.filename = filename
        self.var_format = var_format
        self.required = required
        self.configs = None
        self.file_is_missing = not os.path.isfile(self.filename)

        if self.required and self.file_is_missing:
            raise InvalidConfigurationFile("Could not find {}".format(self.filename))

    @staticmethod
    def _parse_line(line):
        key = []
        pos = 0
        comment = ""

        # parse key
        for pos, char in enumerate(line):
            if char == "=":
                break

            if char == "#":
                comment = char
                continue

            if comment:
                continue

            if char.isspace():
                continue

            key.append(char)

        else:
            raise ValueError("Invalid line format (key=value)")

        key = "".join(key)

        if not key:
            return

        # parse value
        value = []
        quote = ""
        started = False
        for char in line[pos + 1:]:
            if not char.isspace():
                started = True

            if not started:
                continue

            if char == "#" and not quote:
                break

            if char in "\"'":
                if not quote:
                    quote = char
                    continue

                if quote and quote == char:
                    quote = ""
                    continue

                value.append(char)
                continue

            value.append(char)

        value = "".join(value).rstrip()

        return key, value

    def _parse(self):
        self.configs = {}
        with open(self.filename) as envfile:
            for line in envfile:
                try:
                    key, value = self._parse_line(line.strip())
                except (ValueError, TypeError):
                    continue

                self.configs[key] = value

    def __contains__(self, item):
        if self.configs is None:
            self._parse()

        return self.var_format(item) in self.configs

    def __getitem__(self, item):
        if self.configs is None:
            self._parse()

        return self.configs[self.var_format(item)]
