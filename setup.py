# coding: utf-8

from setuptools import setup
import os


README = os.path.join(os.path.dirname(__file__), 'README.md')

setup(name='prettyconf',
      version='0.1',
      description='Separation of settings from code.',
      long_description=open(README).read(),
      author="Osvaldo Santana Neto", author_email="prettyconf@osantana.me",
      license="MIT",
      py_modules=['prettyconf'],
      platforms='any',
      include_package_data=True,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Framework :: Django',
          'Framework :: Flask',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Libraries',
      ],
      url='http://github.com/osantana/prettyconf',
)
