Configuration Loaders
---------------------

Loaders are in charge of loading configuration from various sources, like
``.ini`` files or *environment* variables.

Prettyconf comes with some loaders already included in ``prettyconf.loaders``.


Environment
+++++++++++

.. autoclass:: prettyconf.loaders.Environment

The ``Environment`` loader gets configuration from ``os.environ``. Since it
is a common pattern to write env variables in caps, the loader accepts a
``var_format`` function to pre-format the variable name before the lookup
occurs. By default it is ``str.upper()``.

.. code-block:: python

    from prettyconf import config
    from prettyconf.loaders import Environment


    config.loaders = [Environment(var_format=str.upper)]
    config('debug')  # will look for a `DEBUG` variable


EnvFile
+++++++

.. autoclass:: prettyconf.loaders.EnvFile

The ``EnvFile`` loader gets configuration from ``.env`` file.

.. code-block:: text

    # .env file
    DEBUG=1


.. code-block:: python

    from prettyconf import config
    from prettyconf.loaders import EnvFile


    config.loaders = [EnvFile(file='.env', required=True, var_format=str.upper)]
    config('debug')  # will look for a `DEBUG` variable


.. note::
    You might want to use dump-env_, a utility to create ``.env`` files.


.. _`dump-env`: https://github.com/sobolevn/dump-env


IniFile
+++++++

.. autoclass:: prettyconf.loaders.IniFile



CommandLine
+++++++++++

.. autoclass:: prettyconf.loaders.CommandLine

This loader lets you extract configuration variables from parsed CLI arguments.
By default it works with `argparse`_ parsers.


.. code-block:: python

    from prettyconf import Configuration, NOT_SET
    from prettyconf.loaders import CommandLine

    import argparse


    parser = argparse.ArgumentParser(description='Does something useful.')
    parser.add_argument('--debug', '-d', dest='debug', default=NOT_SET, help='set debug mode')

    config = Configuration(loaders=[CommandLine(parser=parser)])
    print(config('debug', default=False, cast=config.boolean))


Something to notice here is the :py:const:`NOT_SET<prettyconf.loaders.NOT_SET>` value. CLI parsers often force you
to put a default value so that they don't fail. In that case, to play nice with
prettyconf, you must set one. But that would break the discoverability chain
that prettyconf encourages. So by setting this special default value, you will
allow prettyconf to keep the lookup going.

The :py:func:`get_args<prettyconf.loaders.get_args>` function converts the
argparse parser's values to a dict that ignores
:py:const:`NOT_SET<prettyconf.loaders.NOT_SET>` values.


.. _argparse: https://docs.python.org/3/library/argparse.html



RecursiveSearch
+++++++++++++++

.. autoclass:: prettyconf.loaders.RecursiveSearch


