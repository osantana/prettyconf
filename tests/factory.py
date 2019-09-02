import argparse

from prettyconf import NOT_SET


def parser_factory():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--var', '-v', dest='var', default=NOT_SET, help='set var')
    parser.add_argument('--var2', '-b', dest='var2', default='foo', help='set var2')
    return parser
