Casts
-----

Buitin Casts
~~~~~~~~~~~~

#. ``config.boolean`` - converts values like ``On|Off``, ``1|0``, ``yes|no``,
   ``true|false``, ``t|f`` into booleans.
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
~~~~~~~~~~~~

You can implement your own custom casting function:

.. code-block:: python

   def number_list(value):
       return [int(v) for v in value.split(";")]

   NUMBERS = config("NUMBERS", default="1;2;3", cast=number_list)


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


.. _dj-database-url: https://github.com/kennethreitz/dj-database-url
.. _django-cache-url: https://github.com/ghickman/django-cache-url
.. _dj-email-url: https://github.com/migonzalvar/dj-email-url
.. _dj-admins-setting: https://github.com/hernantz/dj-admins-setting
