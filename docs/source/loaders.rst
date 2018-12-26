Configuration Loaders
---------------------

Loaders are in charge of loading configuration from various sources, like
``.ini`` files or *environment* variables.

Prettyconf comes with some loaders already included in ``prettyconf.loaders``.


Environment
+++++++++++

The ``Environment`` loader gets configuration from ``os.environ``. Since it
is a common patter to write env variables in caps, the loader accepts a
``var_format`` function to pre-format the variable name before the lookup
occurs. By default it is ``str.upper()``.

.. code-block:: python

    from prettyconf import config
    from prettyconf.loaders import Environment


    config.loaders = [Environment(var_format=str.upper)]
    config('debug')  # will look for a `DEBUG` variable


EnvFile
+++++++

The ``EnvFile`` loader gets configuration from ``env`` file.

.. code-block:: text

    # .env file
    DEBUG=1


.. code-block:: python

    from prettyconf import config
    from prettyconf.loaders import EnvFile


    config.loaders = [EnvFile(file='.env', required=True, var_format=str.upper)]
    config('debug')  # will look for a `DEBUG` variable
