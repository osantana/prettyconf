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
    PORTS = config("PORTS", cast=config.list[config.int])  # list[int]
    PORT = config("PORT", cast=config.int)                 # int
    WORKERS = config("WORKERS", config.int)                # int, cast given by position

The return type of the cast is what you get back, so custom casts are inferred
too. Without a ``cast``, the value comes back as ``str``, or as ``str | T`` when
you pass a ``default`` of type ``T``.

.. versionadded:: 3.0.0


Namespaces
~~~~~~~~~~

Settings for the same service often share a prefix, like ``AUTH0_DOMAIN`` and
``AUTH0_TOKEN``. Index ``config`` with that prefix to get a configuration that
adds it to every name:

.. code-block:: python

    from prettyconf import config

    auth0 = config["AUTH0_"]

    AUTH0_DOMAIN = auth0("DOMAIN")                          # reads AUTH0_DOMAIN
    AUTH0_TOKEN = auth0("TOKEN", wrapper=config.secret)     # reads AUTH0_TOKEN
    AUTH0_RETRIES = auth0("RETRIES", default="3", cast=config.int)

The prefix is used exactly as written, separator included, so ``config["AUTH0"]``
would read ``AUTH0DOMAIN``. A namespace takes ``cast``, ``default`` and
``wrapper`` like ``config`` itself, reads from the same loaders, and can be
indexed again: ``config["AUTH0_"]["API_"]("TOKEN")`` reads ``AUTH0_API_TOKEN``.
Error messages show the full name.

A namespace keeps the loaders that ``config`` had when you created it. If you
replace ``config.loaders``, create the namespace afterwards.

.. versionadded:: 3.1.0


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
