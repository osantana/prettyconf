Usage
-----

You can import and use ``prettyconf`` in your Python code:

.. code-block:: python

    from prettyconf import config

    MY_CONFIG = config("PROJECT_MY_CONFIG")

If ``PROJECT_MY_CONFIG`` is not defined in an environment variable neither in a
``.env`` (or ``*.cfg``) file, ``prettyconf`` will raise a
``UnknownConfiguration`` exception.

.. warning:: ``prettyconf`` will skip configuration files inside ``.zip``,
   ``.egg`` or wheel packages.

In these cases you could define a default configuration value:

.. code-block:: python

    MY_CONFIG = config("PROJECT_MY_CONFIG", default="default value")

You can also use the ``cast`` argument to convert a string value into
a specific value type:

.. code-block:: python

    DEBUG = config("DEBUG", default=False, cast=config.boolean)

The ``boolean`` cast converts strings values like ``On|Off``, ``1|0``,
``yes|no``, ``true|False`` into Python boolean ``True`` or ``False``.


Casts
~~~~~

Buitin Casts
++++++++++++

#. ``config.boolean`` - converts values like ``On|Off``, ``1|0``, ``yes|no``,
   ``true|false`` into booleans.
#. ``config.eval`` - safely evaluate strings with Python literals to Python
   objects (alias to Python's ``ast.literal_eval``).
#. ``config.list`` - converts comma separated strings into lists.
#. ``config.tuple`` - converts comma separated strings into tuples.
#. ``config.option`` - get a return value based on specific options:

.. code-block:: python

    environments = {
        "production": ("spam", "eggs"),
        "local": ("spam", "eggs", "test"),
    }

    # Will return a tuple with ("spam", "eggs") when
    # ENVIRONMENT is undefined or defined with `production`
    # and a tuple with ("spam", "eggs", "test") when
    # ENVIRONMENT is set with `local`.
    MODULES = config("ENVIRONMENT",
                     default="production",
                     cast=Option(environment))


Custom casts
++++++++++++

You can implement your own custom casting function:

.. code-block:: python

   def number_list(value):
       return [int(v) for v in value.split(";")]

   NUMBERS = config("NUMBERS", default="1;2;3", cast=number_list)


Useful third-parties casts
++++++++++++++++++++++++++

* `dj-database-url`_ - Parses URLs like ``mysql://user:pass@server/db`` into
  Django ``DATABASES`` configuration format.
* `django-cache-url`_ - Parses URLs like ``memcached://server:port/prefix``
  into Django ``CACHES`` configuration format.
* `dj-email-url`_ - Parses URLs like
  ``smtp://user@domain.com:pass@smtp.example.com:465/?ssl=True`` with
  parameters used in Django ``EMAIL_*`` configurations.


Advanced usage
~~~~~~~~~~~~~~

Most of the time you can use the ``prettyconf.config`` function to get your
settings and use the ``prettyconf``'s standard behaviour. But some times
you need to change this behaviour.

To make this changes possible you can always create your own
``Configuration()`` instance and change it's default behaviour:

.. code-block:: python

    from prettyconf import Configuration

    config = Configuration()

.. warning:: ``prettyconf`` will skip configuration files inside ``.zip``,
   ``.egg`` or wheel packages.


Customizing the configuration file location
+++++++++++++++++++++++++++++++++++++++++++

By default library will use the directory of the file where ``config()`` was
called as the start directory to look for a ``.env`` configuration file.
Consider the following file structure:

.. code-block:: text

    project/
      app/
        .env
        settings.py

If you call ``config()`` from ``project/app/settings.py`` the library will look
for configuration files at ``project/app``.

You can change that behaviour, by customizing configuration loaders to look at
a different ``path`` when instantiating your ``Configuration()``:

.. code-block:: python

    # Code example in project/app/settings.py
    import os

    from prettyconf import Configuration
    from prettyconf.loaders import Environment, EnvFile

    project_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
    env_file = f"{project_path}/.env"
    config = Configuration(loaders=[Environment(), 
                                    EnvFile(filename=env_file, required=False)])

The example above will start looking for configuration in the environment and
then in a ``.env`` file at ``project/`` instead of ``project/app``.

You can also alter this ``loaders`` attribute in ``prettyconf.config`` before use it:

.. code-block:: python

    # Code example in project/app/settings.py
    import os

    from prettyconf import config
    from prettyconf.loaders import Environment, EnvFile

    project_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
    env_file = f"{project_path}/.env"
    config.loaders = [Environment(), EnvFile(filename=env_file, required=False)]

because ``config`` is nothing but an already instantiated ``Configuration`` object.


Read more about how loaders can be configured in the :doc:`loaders section<loaders>`.


.. _dj-database-url: https://github.com/kennethreitz/dj-database-url
.. _django-cache-url: https://github.com/ghickman/django-cache-url
.. _dj-email-url: https://github.com/migonzalvar/dj-email-url
