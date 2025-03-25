import pytest

from prettyconf.loaders import CommandLine

from .factory import parser_factory


def test_basic_config(command_line_config):
    assert repr(command_line_config).startswith('CommandLine(parser=')
    assert command_line_config['var2'] == 'foo'


def test_ignores_not_set_values(command_line_config):
    with pytest.raises(KeyError):
        return command_line_config['var']


def test_ignores_missing_keys(command_line_config):
    with pytest.raises(KeyError):
        return command_line_config['var3']


def test_does_not_ignore_set_values():
    parser = parser_factory()

    def test_args():
        _parser = parser_factory()
        return _parser.parse_args(['--var=bar', '-b', 'bar2'])

    parser.parse_args = test_args
    config = CommandLine(parser=parser)
    assert config['var'] == 'bar'
    assert config['var2'] == 'bar2'


def test_contains_missing_keys(command_line_config):
    assert 'var3' not in command_line_config
