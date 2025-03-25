import os

import pytest

from prettyconf.loaders import Environment


def test_basic_config():
    os.environ['TEST'] = 'test'
    config = Environment()

    assert 'TEST' in config
    assert 'test' == config['TEST']
    assert repr(config).startswith('Environment(var_format=')

    del os.environ['TEST']


def test_fail_missing_config():
    config = Environment()

    assert 'UNKNOWN' not in config
    with pytest.raises(KeyError):
        _ = config['UNKNOWN']


def test_default_var_format():
    os.environ['TEST'] = 'test'
    config = Environment()

    assert 'test' in config
    assert 'test' == config['test']

    del os.environ['TEST']


def test_custom_var_format():
    def formatter(x):
        return f'_{x}'

    os.environ['_TEST'] = 'test'
    config = Environment(var_format=formatter)

    assert 'TEST' in config
    assert 'test' == config['TEST']

    del os.environ['_TEST']
