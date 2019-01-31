# coding: utf-8


from __future__ import unicode_literals

import argparse

from prettyconf.loaders import CommandLine, NOT_SET
from .base import BaseTestCase


def parser_factory():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--var', '-v', dest='var', default=NOT_SET, help='set var')
    parser.add_argument('--var2', '-b', dest='var2', default='foo', help='set var2')
    return parser


def test_parse_args():
    # mock function used to always parse known args
    parser = parser_factory()
    return parser.parse_args([])


class CommandLineTestCase(BaseTestCase):

    def setUp(self):
        super(CommandLineTestCase, self).setUp()
        parser = parser_factory()
        parser.parse_args = test_parse_args
        self.config = CommandLine(parser=parser)

    def test_basic_config(self):
        self.assertEquals(self.config['var2'], 'foo')

    def test_ignores_NOT_SET_values(self):
        with self.assertRaises(KeyError):
            self.config['var']

    def test_ignores_missing_keys(self):
        with self.assertRaises(KeyError):
            self.config['var3']

    def test_does_not_ignore_set_values(self):
        parser = parser_factory()
        def test_args():
            parser = parser_factory()
            return parser.parse_args(['--var=bar', '-b', 'bar2'])
        parser.parse_args = test_args
        config = CommandLine(parser=parser)
        self.assertEquals(config['var'], 'bar')
        self.assertEquals(config['var2'], 'bar2')
