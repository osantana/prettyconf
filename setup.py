import os
import re

from setuptools import setup, Command

here = os.path.abspath(os.path.dirname(__file__))

version = "0.0.0"
with open(os.path.join(here, "CHANGES.txt")) as changes:
    for line in changes:
        version = line.strip()
        if re.search(r'^[0-9]+\.[0-9]+(\.[0-9]+)?$', version):
            break


class VersionCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print(version)


setup(
    name='prettyconf',
    version=version,
    description='Separation of settings from code.',
    author="Osvaldo Santana Neto", author_email="prettyconf@osantana.me",
    license="MIT",
    packages=['prettyconf'],
    platforms='any',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries',
    ],
    url='http://github.com/osantana/prettyconf',
    download_url='https://github.com/osantana/prettyconf/tarball/{}'.format(version),
    cmdclass={'version': VersionCommand},
    test_suite="tests",
)
