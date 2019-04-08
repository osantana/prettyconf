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

.. seealso::
    Find out more about other casts or how to write
    your own at :doc:`Casts<casts>`.


Configuration files discovery
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default library will use the directory of the file where ``config()`` was
called as the start directory to look for configuration files. Consider the
following file structure:

.. code-block:: text

    project/
      settings.ini
      app/
        settings.py

If you call ``config()`` from ``project/app/settings.py`` the library will
start looking for configuration files at ``project/app`` until it finds
``.env|*.ini|*.cfg`` files.

.. seealso::
    This behavior is described more deeply on the
    :py:class:`RecursiveSearch<prettyconf.loaders.RecursiveSearch>` loader.
    :doc:`Loaders<loaders>` will help you customize how configuration
    discovery works. Find out more at :ref:`discovery-customization`.
