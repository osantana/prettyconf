Usage
-----

You can import and use ``prettyconf`` in your Python code:

.. code-block:: python

    from prettyconf import config

    MY_CONFIG = config("PROJECT_MY_CONFIG")

If ``PROJECT_MY_CONFIG`` is not defined in an environment variable neither in a
``.env`` (or ``*.cfg``) file, ``prettyconf`` will raise an
``UnknownConfigurationError`` exception.

.. warning:: ``prettyconf`` looks for configuration files on the filesystem, so
   it will not find files packed inside an archive, such as a zipapp or a
   wheel that is never unpacked.

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


.. _type-checking:

Type checking
~~~~~~~~~~~~~

``prettyconf`` ships a ``py.typed`` marker, and ``config()`` infers its return
type from the ``cast`` you pass, so a type checker knows what each setting is:

.. code-block:: python

    NAME = config("NAME")                                  # str
    TIMEOUT = config("TIMEOUT", default=None)              # str | None
    DEBUG = config("DEBUG", default=False, cast=config.boolean)  # bool
    HOSTS = config("HOSTS", cast=config.list)              # list[str]
    PORT = config("PORT", cast=int)                        # int

Any callable works as a ``cast``, and its return type is what you get back, so
custom casts are inferred too. Without a ``cast``, the value comes back as
``str``, or as ``str | T`` when you pass a ``default`` of type ``T``.

.. versionadded:: 3.0.0


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
