Casts
-----

Builtin Casts
~~~~~~~~~~~~~

A configuration value always arrives as text. A cast reads that text and
returns the value your code will use. The builtin casts do one of three jobs.

Some return a value of one type:

#. ``config.boolean`` - converts values like ``On|Off``, ``1|0``, ``yes|no``,
   ``true|false``, ``t|f`` into booleans.
#. ``config.int`` - converts the value into an integer.
#. ``config.float`` - converts the value into a float.
#. ``config.decimal`` - converts the value into a ``decimal.Decimal``, keeping
   the digits as written (``"0.10"`` stays ``Decimal("0.10")``).
#. ``config.path`` - converts the value into a ``pathlib.Path``.
#. ``config.timedelta`` - converts a duration like ``30``, ``500ms`` or
   ``1h30m`` into a ``datetime.timedelta``, see :ref:`timedelta`.
#. ``config.url`` - splits a URL into its parts and checks that it has a
   scheme, see :ref:`url`.
#. ``config.enum`` - converts the name or the value of a member into that
   member of an ``Enum``, see :ref:`enum`.

Some read a format, which is a way of writing a structure as text:

#. ``config.list`` - reads comma separated values into a list.
#. ``config.tuple`` - reads comma separated values into a tuple.
#. ``config.json`` - reads a JSON document. What you get is what the document
   holds, usually a ``dict`` or a ``list``.
#. ``config.eval`` - safely evaluate strings with Python literals to Python
   objects (alias to Python's ``ast.literal_eval``).

One undoes an encoding, which is what made a value fit in a single line:

#. ``config.base64`` - decodes a whole file encoded as a single base64
   string, see :ref:`base64`.

A list, a tuple and a base64 string contain something else, so these casts take
the cast of their content between brackets. ``config.list[config.int]`` is a
list of integers, and ``config.base64[config.json]`` is a JSON document encoded
as base64. Without the brackets, ``config.list`` and ``config.tuple`` return
strings and ``config.base64`` returns ``bytes``.

There is also ``config.option``, which returns a value picked from the options
you give:

.. code-block:: python

    from prettyconf import config

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
                     cast=config.option(environments))


.. _limits:

Limits
~~~~~~

The casts of values that have an order take a ``minimum`` and a ``maximum``.
``config.int`` has no limits, so build the cast yourself:

.. code-block:: python

    import datetime

    from prettyconf import config
    from prettyconf.casts import Float, Integer, Timedelta

    PORT = config("PORT", default=8000, cast=Integer(minimum=1, maximum=65535))
    SAMPLE_RATE = config("SAMPLE_RATE", default=1, cast=Float(minimum=0, maximum=1))
    TIMEOUT = config("TIMEOUT", default=30, cast=Timedelta(maximum=datetime.timedelta(minutes=5)))

Both limits are inclusive and either one can be left out. ``Integer``,
``Float``, ``Decimal`` and ``Timedelta`` take them. A value outside the limits
raises ``InvalidConfigurationError`` with the limit in the message:

.. code-block:: text

    Configuration 'PORT' is invalid: Value must be at most 65535

A cast with limits works wherever a cast does, so
``config.list[Integer(minimum=1, maximum=65535)]`` is a list of ports.

.. versionadded:: 3.1.0


.. _enum:

Settings with a fixed set of values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a setting only accepts a few values, declare them in an ``Enum`` and use
``config.enum``:

.. code-block:: python

    import enum

    from prettyconf import config


    class LogLevel(enum.Enum):
        DEBUG = "debug"
        INFO = "info"


    LOG_LEVEL = config("LOG_LEVEL", default="info", cast=config.enum(LogLevel))

The variable can hold the name of a member (``LOG_LEVEL=DEBUG``) or its value
(``LOG_LEVEL=debug``). Names are tried first and the match is exact, so
``Debug`` is rejected. Anything else raises ``InvalidConfigurationError`` with
the list of valid names:

.. code-block:: text

    Configuration 'LOG_LEVEL' is invalid: Value is not one of the valid options: DEBUG, INFO

Type checkers know that ``LOG_LEVEL`` is a ``LogLevel``.

.. versionadded:: 3.1.0


.. _timedelta:

Durations
~~~~~~~~~

``config.timedelta`` reads timeouts, intervals and expiration times into a
``datetime.timedelta``:

.. code-block:: python

    from prettyconf import config

    TIMEOUT = config("TIMEOUT", default=30, cast=config.timedelta)

A number alone is a number of seconds. A number followed by a unit uses that
unit, and several of them can be written together:

========== ======================
value      result
========== ======================
``30``     30 seconds
``1.5``    1.5 seconds
``500ms``  500 milliseconds
``30s``    30 seconds
``5m``     5 minutes
``2h``     2 hours
``7d``     7 days
``1h30m``  1 hour and 30 minutes
========== ======================

The units are ``ms``, ``s``, ``m``, ``h`` and ``d``, in lower case and with no
spaces. Negative durations are not accepted.

.. versionadded:: 3.1.0


.. _url:

URLs
~~~~

``config.url`` returns what ``urllib.parse.urlsplit`` returns, after checking
that the value has a scheme followed by ``://``, something after it, and a port
that is a number when there is one:

.. code-block:: python

    from prettyconf import config

    API = config("API_URL", cast=config.url)

    API.scheme        # "https"
    API.hostname      # "api.example.com"
    API.port          # None, or an int
    API.path          # "/v1"

A value like ``localhost:8000`` or ``example.com/path`` is rejected, because
without the scheme ``urlsplit`` reads them as something else.

When the URL carries a password, as database URLs usually do, printing the
result shows it. Add ``wrapper=config.secret``:

.. code-block:: python

    DATABASE = config("DATABASE_URL", cast=config.url, wrapper=config.secret)

    DATABASE.reveal().password

.. versionadded:: 3.1.0


.. _base64:

Encoding a whole file in one variable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some credentials come as files, like a Google service account ``.json`` or an
Apple ``.p8`` signing key, and a configuration variable has to be a single
line. ``config.base64`` decodes a file that was encoded as one base64 string:

.. code-block:: sh

    # generate the value, without line wrapping
    $ base64 -w0 service-account.json      # GNU coreutils
    $ base64 -i service-account.json | tr -d '\n'   # macOS

.. code-block:: python

    from prettyconf import config

    CREDENTIALS = config("GOOGLE_CREDENTIALS", cast=config.base64)  # bytes

The cast returns ``bytes``, and ``json.loads`` accepts them as they are. Pass an
encoding to get ``str`` instead:

.. code-block:: python

    from prettyconf.casts import Base64

    SIGNING_KEY = config("APPLE_SIGNING_KEY", cast=Base64("utf-8"))  # str

When the file has a format that another cast reads, put that cast between
brackets. The content is decoded as UTF-8 text, or with the encoding you gave
to ``Base64``, and handed to it:

.. code-block:: python

    CREDENTIALS = config(
        "GOOGLE_CREDENTIALS",
        cast=config.base64[config.json],
        wrapper=config.secret,
    )

    CREDENTIALS.reveal()["client_email"]

Wrapped base64 works too: whitespace and newlines are stripped before decoding,
so a value pasted from a wrapping ``base64`` still loads. A value that is not
valid base64 raises ``InvalidConfigurationError``. As with the other casts, the
error message does not include the rejected value, so a broken key does not end
up in your logs.

.. versionadded:: 3.0.0

.. versionchanged:: 3.1.0
    ``config.base64`` takes the cast of its content between brackets.


Custom casts
~~~~~~~~~~~~

A cast is an instance of a class that inherits from ``AbstractCast`` and
implements ``__call__``. Put the type it returns between the brackets:

.. code-block:: python

   from prettyconf import config
   from prettyconf.casts import AbstractCast
   from prettyconf.exceptions import InvalidConfigurationError


   class Percentage(AbstractCast[float]):
       def __call__(self, value) -> float:
           number = config.float(value)
           if not 0 <= number <= 100:
               raise InvalidConfigurationError("Value is not between 0 and 100")

           return number / 100


   DISCOUNT = config("DISCOUNT", default="10", cast=Percentage())

With ``AbstractCast[float]``, type checkers and IDEs know that ``DISCOUNT`` is a
``float``. See :ref:`type-checking`. When the value is wrong,
raise ``InvalidConfigurationError`` with the reason and leave the value out of
the message. ``prettyconf`` adds the name of the variable.

.. deprecated:: 3.1.0
    A cast that is not an ``AbstractCast`` instance, such as ``cast=int``,
    ``cast=bool`` or a plain function, still works but emits a
    ``DeprecationWarning``. It will stop working in the next major release.
    The native types give wrong results as casts: ``bool("false")`` is ``True``
    and ``list("a,b")`` is ``["a", ",", "b"]``. Use ``config.int``,
    ``config.boolean`` or ``config.list`` instead, or write a subclass.


Useful third-parties casts
~~~~~~~~~~~~~~~~~~~~~~~~~~

Django is a popular python web framework that imposes some structure on the way
its settings are configured. Here are a few 3rd party casts that help you adapt
strings into that inner structures:

* `dj-database-url`_ - Parses URLs like ``mysql://user:pass@server/db`` into
  Django ``DATABASES`` configuration format.
* `django-cache-url`_ - Parses URLs like ``memcached://server:port/prefix``
  into Django ``CACHES`` configuration format.
* `dj-email-url`_ - Parses URLs like
  ``smtp://user@domain.com:pass@smtp.example.com:465/?ssl=True`` with
  parameters used in Django ``EMAIL_*`` configurations.
* `dj-admins-setting`_ - Parses emails lists for the ``ADMINS`` configuration.

These libraries expose plain functions, so wrap the one you need in a cast:

.. code-block:: python

    import dj_database_url
    from prettyconf import config
    from prettyconf.casts import AbstractCast


    class DatabaseURL(AbstractCast[dict]):
        def __call__(self, value) -> dict:
            return dj_database_url.parse(value)


    DATABASES = {"default": config("DATABASE_URL", cast=DatabaseURL())}

Frameworks that do not impose a settings structure, like Flask_ and FastAPI_,
usually need nothing more than the builtin casts:

.. code-block:: python

    # FastAPI application module
    from fastapi import FastAPI
    from prettyconf import config

    app = FastAPI(
        debug=config("DEBUG", default=False, cast=config.boolean),
        title=config("APP_TITLE", default="My API"),
    )

.. _`Flask`: https://flask.palletsprojects.com/
.. _`FastAPI`: https://fastapi.tiangolo.com/


.. _dj-database-url: https://github.com/jazzband/dj-database-url
.. _django-cache-url: https://github.com/ghickman/django-cache-url
.. _dj-email-url: https://github.com/migonzalvar/dj-email-url
.. _dj-admins-setting: https://github.com/hernantz/dj-admins-setting
