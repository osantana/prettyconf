Wrappers
--------

You can pass a ``wrapper`` to ``config()``. It is called with the value that
the cast returned, and ``config()`` returns whatever the wrapper returns:

.. code-block:: python

    from prettyconf import config

    value = config("NAME", cast=some_cast, wrapper=some_wrapper)
    # the same as some_wrapper(some_cast(raw_value))

If the variable is not set and you gave a ``default``, the default goes through
the cast and the wrapper too.


.. _secret:

Keeping secrets out of logs
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Settings get printed. Someone leaves a ``print(settings.API_KEY)`` behind while
debugging, a log line includes the database URL, an error tracker saves the
local variables of the function that failed. If the setting is a password or an
API key, it is now readable in all of those places.

Use the ``config.secret`` wrapper for these settings. It returns a
``SecretValue``, which prints as ``***``. To get the real value you call
``reveal()``:

.. code-block:: python

    from prettyconf import config

    API_KEY = config("API_KEY", wrapper=config.secret)
    PIN = config("PIN", cast=config.int, wrapper=config.secret)
    CREDENTIALS = config("GOOGLE_CREDENTIALS", cast=config.base64, wrapper=config.secret)

    print(API_KEY)            # ***
    repr(API_KEY)             # SecretValue(***)
    API_KEY.reveal()          # the key, a str
    PIN.reveal()              # an int
    CREDENTIALS.reveal()      # bytes

A ``SecretValue`` is not a string, and code that expects one fails:
``json.dumps`` and string concatenation raise ``TypeError``, and comparing it
with a plain value is always ``False``. Libraries will not accept it either, so
call ``reveal()`` where you pass the secret on:

.. code-block:: python

    server.login(EMAIL_USER, EMAIL_PASSWORD.reveal())    # smtplib

Type checkers know what is inside. ``PIN`` above is a ``SecretValue[int]`` and
``PIN.reveal()`` is an ``int``.


Writing a wrapper
~~~~~~~~~~~~~~~~~

A wrapper is any callable that takes the value and returns something:

.. code-block:: python

    from pathlib import Path

    DATA_DIR = config("DATA_DIR", wrapper=Path)   # a Path

.. versionadded:: 3.1.0
