Usage
-----

You can import and use ``prettyconf`` in your Python code:

.. code-block:: python

    from prettyconf import config

    MY_CONFIG = config("PROJECT_MY_CONFIG")

If ``PROJECT_MY_CONFIG`` is not defined in an environment variable neither in a
``.env`` (or ``*.cfg``) file, ``prettyconf`` will raise a
``UnknownConfiguration`` exception.

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
#. ``config.list`` - converts comma separated strings into lists.
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

#. ``config.dictionary`` - TODO


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


Advanced usage
~~~~~~~~~~~~~~
You can always create your own ``Configuration`` instance and change it's default behaviour.

.. code-block:: python

    from prettyconf.configuration import Configuration
    config = Configuration()

Set the starting path
+++++++++++++++++++++
By default the library will use the directory of the file where ``config()`` was called 
as the starting directory to look for configuration files. Consider the following file 
structure:

.. code-block:: shell

    project/
      settings.ini
      app/
        settings.py

When calling ``config()`` from ``project/app/settings.py`` the library will start looking
for configuration files at ``project/app``

You can change that behaviour, by setting a different ``starting_path`` when instantiating
your ``Configuration``:

.. code-block:: python

    # Code example in project/app/settings.py
    import os

    from prettyconf.configuration import Configuration

    project_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
    config = Configuration(project_path)

The example above will start looking for files at ``project/`` instead of ``project/app``.

Set a different root path
+++++++++++++++++++++++++
By default, the library will try to look for configuration files until it finds valid 
configuration files **or** it reaches ``Configuration.root_path``.

Consider the following file structure:

.. code-block:: shell
    
    /projects/
      any_settings.ini
      project/
        app/
          settings.py

The default root path is set to the user home directory (e.g. ``$HOME`` or 
``/home/yourusername``). You can change this behaviour by setting any parent directory 
of the ``starting_path`` as the ``root_path`` when instantiating ``Configuration``:

.. code-block:: python

    # Code example in project/app/settings.py
    import os

    from prettyconf.configuration import Configuration

    app_path = os.path.dirname(__file__)
    project_path = os.path.realpath(os.path.join(app_path), '..'))

    config = Configuration(root_path=project_path)

The example above will start looking for files at ``project/app/`` and will stop looking
for configuration files at ``project/``, actually never looking at ``any_settings.ini``
and no configuration being loaded at all.

.. _dj-database-url: https://github.com/kennethreitz/dj-database-url
.. _django-cache-url: https://github.com/ghickman/django-cache-url

