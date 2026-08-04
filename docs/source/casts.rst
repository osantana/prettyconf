Casts
-----

Builtin Casts
~~~~~~~~~~~~~

#. ``config.boolean`` - converts values like ``On|Off``, ``1|0``, ``yes|no``,
   ``true|false``, ``t|f`` into booleans.
#. ``config.eval`` - safely evaluate strings with Python literals to Python
   objects (alias to Python's ``ast.literal_eval``).
#. ``config.list`` - converts comma separated strings into lists.
#. ``config.tuple`` - converts comma separated strings into tuples.
#. ``config.json`` - unserialize a string with JSON object into Python.
#. ``config.base64`` - decodes a whole file encoded as a single base64
   string, see :ref:`base64`.
#. ``config.option`` - get a return value based on specific options:

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


.. _base64:

Encoding a whole file in one variable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some credentials only ever exist as files — a Google service account
``.json``, an Apple ``.p8`` signing key — but a configuration variable has to be
a single line. ``config.base64`` decodes a file that was encoded as one
base64 string:

.. code-block:: sh

    # generate the value, without line wrapping
    $ base64 -w0 service-account.json      # GNU coreutils
    $ base64 -i service-account.json | tr -d '\n'   # macOS

.. code-block:: python

    from prettyconf import config

    CREDENTIALS = config("GOOGLE_CREDENTIALS", cast=config.base64)  # bytes

The cast returns ``bytes``, which is what most crypto libraries expect and what
``json.loads`` accepts. Pass an encoding to get ``str`` instead:

.. code-block:: python

    from prettyconf.casts import Base64

    SIGNING_KEY = config("APPLE_SIGNING_KEY", cast=Base64("utf-8"))  # str

Wrapped base64 works too: whitespace and newlines are stripped before decoding,
so a value pasted from a wrapping ``base64`` still loads. A value that is not
valid base64 raises ``InvalidConfigurationError``, and — like every other cast —
the rejected value never appears in the error message, so a broken key does not
end up in your logs.

.. versionadded:: 3.0.0


Custom casts
~~~~~~~~~~~~

You can implement your own custom casting function:

.. code-block:: python

   def number_list(value) -> list[int]:
       return [int(v) for v in value.split(";")]

   NUMBERS = config("NUMBERS", default="1;2;3", cast=number_list)

Annotating the return type of your cast is what lets a type checker infer that
``NUMBERS`` is a ``list[int]``. See :ref:`type-checking`.


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

Frameworks that do not impose a settings structure, like Flask_ and FastAPI_,
usually need nothing more than the builtin casts. A cast is just a callable, so
anything that turns a string into the value your framework expects will do:

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
