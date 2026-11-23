Exceptions
----------

Every exception raised by ``prettyconf`` lives in ``prettyconf.exceptions`` and
inherits from ``ConfigurationError``, so a single ``except`` clause is enough to
catch anything the library throws:

.. code-block:: python

    from prettyconf import config
    from prettyconf.exceptions import ConfigurationError

    try:
        DEBUG = config("DEBUG", cast=config.boolean)
    except ConfigurationError:
        DEBUG = False

The error message of a cast does not include the value that was rejected. The
value may be a password or a private key, and exceptions get logged. The
message has the name of the configuration and the reason it is invalid:

.. code-block:: text

    prettyconf.exceptions.InvalidConfigurationError: Configuration 'API_KEY' is
    invalid: Value is not a valid base64 encoded file

Do the same in your own casts: raise ``InvalidConfigurationError`` with the
reason and leave the value out. ``prettyconf`` adds the variable name.

The hierarchy is:

* ``ConfigurationError``

  * ``InvalidConfigurationError`` - a value could not be converted by a cast.
  * ``InvalidPathError`` - a :py:class:`RecursiveSearch<prettyconf.loaders.RecursiveSearch>`
    was given a ``starting_path`` that is not inside its ``root_path``.
  * ``UnknownConfigurationError`` - no loader had the requested variable and no
    ``default`` was given.
  * ``InvalidConfigurationFileError`` - a configuration file was found but could
    not be read.

    * ``MissingSettingsSectionError`` - an ``.ini``/``.cfg`` file has no
      ``[settings]`` section.

.. versionchanged:: 3.0.0
    These exceptions were renamed to carry the ``Error`` suffix. The old names
    (``ConfigurationException``, ``InvalidConfiguration``, ``InvalidPath``,
    ``UnknownConfiguration``, ``InvalidConfigurationFile`` and
    ``MissingSettingsSection``) are aliases of the new ones, so existing
    ``except`` clauses keep working. Importing them emits a
    ``DeprecationWarning`` and they will be removed in a future release.
