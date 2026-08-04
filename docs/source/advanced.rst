Advanced Usage
--------------


Most of the time you can use the ``prettyconf.config`` function to get your
settings and use the ``prettyconf``'s standard behaviour. But some times
you need to change this behaviour.

To make this changes possible you can always create your own
``Configuration()`` instance and change its default behaviour:

.. code-block:: python

    from prettyconf import Configuration

    config = Configuration()

.. warning:: ``prettyconf`` looks for configuration files on the filesystem, so
   it will not find files packed inside an archive, such as a zipapp or a
   wheel that is never unpacked.


.. _discovery-customization:

Customizing the configuration discovery
+++++++++++++++++++++++++++++++++++++++

By default the library will use the environment and the directory of the file
where ``config()`` was called as the start directory to look for a ``.env``
configuration file.  Consider the following file structure:

.. code-block:: text

    project/
      app/
        .env
        config.ini
        settings.py

If you call ``config()`` from ``project/app/settings.py`` the library will
inspect the environment and then look for configuration files at
``project/app``.

You can change that behaviour, by customizing configuration loaders to look at
a different ``path`` when instantiating your ``Configuration()``:

.. code-block:: python

    # Code example in project/app/settings.py
    import os

    from prettyconf import Configuration
    from prettyconf.loaders import Environment, EnvFile

    project_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
    env_file = f"{project_path}/.env"
    config = Configuration(loaders=[Environment(), EnvFile(filename=env_file)])

The example above will start looking for configuration in the environment and
then in a ``.env`` file at ``project/`` instead of ``project/app``.

Because ``config`` is nothing but an already instantiated ``Configuration`` object,
you can also alter this ``loaders`` attribute in ``prettyconf.config`` before using it:

.. code-block:: python

    # Code example in project/app/settings.py
    import os

    from prettyconf import config
    from prettyconf.loaders import Environment, EnvFile

    project_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
    env_file = f"{project_path}/.env"
    config.loaders = [Environment(), EnvFile(filename=env_file)]

Read more about how loaders can be configured in the :doc:`loaders section<loaders>`.

.. _variable-naming:

Naming conventions for variables
++++++++++++++++++++++++++++++++

There happen to be some formatting conventions for configuration parameters
based on where they are set. For example, it is common to name environment
variables in uppercase:

.. code-block:: sh

    $ DEBUG=yes OTHER_CONFIG=10 ./app.py

but if you were to set this config in an ``.ini`` file, it should probably be
in lower case:

.. code-block:: ini

    [settings]
    debug=yes
    other_config=10

command line arguments have yet another convention:

.. code-block:: sh

    $ ./app.py --debug=yes --another-config=10

Prettyconf lets you follow these aesthetic patterns by setting a
``var_format`` function when instantiating the :doc:`loaders<loaders>`.

By default, the :py:class:`Environment<prettyconf.loaders.Environment>` is
instantiated with ``var_format=str.upper`` so that lookups play nice with the
env variables.

.. code-block:: python

    from prettyconf import Configuration
    from prettyconf.loaders import Environment

    config = Configuration(loaders=[Environment(var_format=str.upper)])
    debug = config('debug', default=False, cast=config.boolean)  # lookups for DEBUG=[yes|no]


Writing your own loader
+++++++++++++++++++++++

If you need a custom loader, you should just extend the :py:class:`AbstractConfigurationLoader<prettyconf.loaders.AbstractConfigurationLoader>`.

.. autoclass:: prettyconf.loaders.AbstractConfigurationLoader

For example, say you want to write a Yaml loader. It is important to note
that by raising a ``KeyError`` exception from the loader, prettyconf knows
that it has to keep looking down the loaders chain for a specific config.

.. code-block:: python

    import yaml
    from prettyconf.loaders import AbstractConfigurationLoader

    class YamlFile(AbstractConfigurationLoader):
        def __init__(self, filename):
            self.filename = filename
            self.config = {}
            self._initialized = False

        def _parse(self):
            if self._initialized:
                return

            with open(self.filename) as yamlfile:
                self.config = yaml.safe_load(yamlfile)

            self._initialized = True

        def __contains__(self, item):
            try:
                self._parse()
            except (OSError, yaml.YAMLError):
                return False

            return item in self.config

        def __getitem__(self, item):
            try:
                self._parse()
            except (OSError, yaml.YAMLError) as ex:
                # KeyError tells prettyconf to keep looking elsewhere!
                raise KeyError(f"{item!r}") from ex

            return self.config[item]


Then configure prettyconf to use it.

.. code-block:: python

    from prettyconf import config
    config.loaders = [YamlFile('config.yml')]


