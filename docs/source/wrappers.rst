Wrappers
--------

A cast decides the *type* of a setting. A wrapper decides what happens to the
value once it has that type, and the two are independent: ``wrapper`` receives
whatever the cast returned.

.. code-block:: python

    from prettyconf import config

    value = config("NAME", cast=some_cast, wrapper=some_wrapper)
    # the same as some_wrapper(some_cast(raw_value))

The default value, when one is used, goes through the cast and the wrapper too.


.. _secret:

Keeping secrets out of logs
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A password or an API key read as a plain value ends up wherever the settings
object is printed: a debug page, a log line, an error tracker. Being a secret
has nothing to do with the type of the value, so it is a wrapper and not a cast:
``config.secret`` puts the value in a ``SecretValue``, which shows as ``***``
everywhere and only hands the real value over when you call ``reveal()``.

.. code-block:: python

    from prettyconf import config

    API_KEY = config("API_KEY", wrapper=config.secret)
    PIN = config("PIN", cast=config.int, wrapper=config.secret)
    CREDENTIALS = config("GOOGLE_CREDENTIALS", cast=config.base64, wrapper=config.secret)

    print(API_KEY)            # ***
    repr(API_KEY)             # SecretValue(***)
    API_KEY.reveal()          # the actual key, a str
    PIN.reveal()              # an int
    CREDENTIALS.reveal()      # bytes

A ``SecretValue`` is deliberately not a string. Serializing it with
``json.dumps`` or concatenating it raises ``TypeError`` instead of quietly
writing the secret out, and it never compares equal to a plain value. The price
is that it cannot be handed to a library as it is: pass ``reveal()`` at the
point where the secret is actually needed.

Type checkers follow the cast through the wrapper: ``PIN`` above is a
``SecretValue[int]``, and ``PIN.reveal()`` is an ``int``.


Writing a wrapper
~~~~~~~~~~~~~~~~~

Any callable that takes the value and returns something is a wrapper:

.. code-block:: python

    from pathlib import Path

    DATA_DIR = config("DATA_DIR", wrapper=Path)   # a Path

.. versionadded:: 3.1.0
