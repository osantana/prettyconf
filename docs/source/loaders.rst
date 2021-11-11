Configuration Loaders
---------------------

Loaders are in charge of loading configuration from various sources, like
``.ini`` files or *environment* variables. Loaders are ment to chained, so that
prettyconf checks one by one for a given configuration variable.

Prettyconf comes with some loaders already included in ``prettyconf.loaders``.

.. seealso::
    Some loaders include a ``var_format`` callable argument, see
    :ref:`variable-naming` to read more about it's purpose.



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

The ``EnvFile`` loader gets configuration from ``.env`` file. If the file
doesn't exist, this loader will be skipped without raising any errors.

.. code-block:: text

    # .env file
    DEBUG=1


.. code-block:: python

    from prettyconf import config
    from prettyconf.loaders import EnvFile


    config.loaders = [EnvFile(filename='.env', var_format=str.upper)]
    config('debug')  # will look for a `DEBUG` variable


.. note::
    You might want to use dump-env_, a utility to create ``.env`` files.


.. _`dump-env`: https://github.com/sobolevn/dump-env


IniFile
+++++++

.. autoclass:: prettyconf.loaders.IniFile

The ``IniFile`` loader gets configuration from ``.ini`` or ``.cfg`` files. If
the file doesn't exist, this loader will be skipped without raising any errors.


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

This loader tries to find ``.env`` or ``*.ini|*.cfg`` files and load them with
the :py:class:`EnvFile<prettyconf.loaders.EnvFile>` and
:py:class:`IniFile<prettyconf.loaders.IniFile>` loaders respectively. It will
start at the ``starting_path`` directory to look for configuration files.

.. warning::
    It is important to note that this loader uses the glob module internally to
    discover ``.env`` and ``*.ini|*.cfg`` files.  This could be problematic if
    the project includes many files that are unrelated, like a ``pytest.ini``
    file along side with a ``settings.ini``. An unexpected file could be found
    and be considered as the configuration to use.

Consider the following file structure:

.. code-block:: text

    project/
      settings.ini
      app/
        settings.py

When instantiating your
:py:class:`RecursiveSearch<prettyconf.loaders.RecursiveSearch>`, if you pass
``/absolute/path/to/project/app/`` as ``starting_path`` the loader will start
looking for configuration files at ``project/app``.

.. code-block:: python

    # Code example in project/app/settings.py
    import os

    from prettyconf import config
    from prettyconf.loaders import RecursiveSearch

    app_path = os.path.dirname(__file__)
    config.loaders = [RecursiveSearch(starting_path=app_path)]

By default, the loader will try to look for configuration files until it finds
valid configuration files **or** it reaches ``root_path``. The ``root_path`` is
set to the root directory ``/`` initialy.

Consider the following file structure:

.. code-block:: text

    /projects/
      any_settings.ini
      project/
        app/
          settings.py

You can change this behaviour by setting any parent directory of the
``starting_path`` as the ``root_path`` when instantiating
:py:class:`RecursiveSearch<prettyconf.loaders.RecursiveSearch>`:

.. code-block:: python

    # Code example in project/app/settings.py
    import os

    from prettyconf import Configuration
    from prettyconf.loaders import RecursiveSearch

    app_path = os.path.dirname(__file__)
    project_path = os.path.realpath(os.path.join(app_path, '..'))
    rs = RecursiveSearch(starting_path=app_path, root_path=project_path)
    config = Configuration(loaders=[rs])

The example above will start looking for files at ``project/app/`` and will stop looking
for configuration files at ``project/``, actually never looking at ``any_settings.ini``
and no configuration being loaded at all.

The ``root_path`` must be a parent directory of ``starting_path``:

.. code-block:: python

    # Code example in project/app/settings.py
    from prettyconf.loaders import RecursiveSearch

    # /baz is not parent of /foo/bar, so this raises an InvalidPath exception here
    rs = RecursiveSearch(starting_path="/foo/bar", root_path="/baz")


AwsParameterStore
+++++++++++++++++

.. autoclass:: prettyconf.loaders.AwsParameterStore

The ``AwsParameterStore`` loader gets configuration from the AWS Parameter Store,
part of AWS Systems Manager. The loader will be skipped if the parameter store is 
unreachable (connectivity, unavailability, access permissions).
The loader respects parameter hierarchies, performing non-recursive discoveries.
The loader accepts AWS access secrets and region when instantiated, otherwise, it 
will use system-wide defaults (if available).
The AWS parameter store supports three parameter types: ``String``, ``StringList`` 
and ``SecureString``. All types are read as strings, however, decryption of 
``SecureStrings`` is not handled by the loader.

.. code-block:: python

    from prettyconf import config
    from prettyconf.loaders import AwsParameterStore


    config.loaders = [AwsParameterStore(path='/api')]
    config('debug')  # will look for a parameter named "/api/debug" in the store
