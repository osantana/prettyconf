prettyconf
==========

|Build Status| |Coverage Status|

Pretty Conf is a Python library created to make easy the separation of
configuration and code following the recomendations of `12 Factor`_ topic about
configs.


Requirements
------------

* Python 2.7+ or 3.4+


Installation
------------

First you need to install ``prettyconf`` library:

.. code-block:: sh

    pip install prettyconf

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

You can use the ``cast=`` argument to convert a configuration string into a
specific value type:

.. code-block:: python

    DEBUG = config("DEBUG", default=False, cast=config.boolean)

The ``boolean`` cast converts strings like ``On|Off``, ``1|0``, ``yes|no``,
``true|False`` into Python boolean value ``True`` or ``False``.

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

You can implement your own custom cast:

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


FAQ
---

Why not use environment variables directly?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is a common pattern to read configurations in environment variable that
look similar to the code below:

.. code-block:: python

    if os.environ.get("DEBUG", False):
        print(True)
    else:
        print(False)

But this code have some issues:

#. If *envvar* ``DEBUG=False`` this code will print ``True`` because
   ``os.environ.get("DEBUG", False)`` will return an string `'False'` instead
   of a boolean `False`. And a non-empty string has boolean value ``True``.
#. We can't (dis|en)able debug with *envvars* ``DEBUG=yes|no``, ``DEBUG=1|0``,
   ``DEBUG=True|False``.
#. If we want to use this configuration during development we need to define
   this *envvar* all the time. We can't define this setting in a configuration
   file that will be used if `DEBUG` *envvar* is not defined.


What is the difference between prettyconf and python-decouple_?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is no subtantial difference between both libraries. ``prettyconf`` is
highly inspired in ``python-decouple`` and provides almost the same API.

There is an small difference in configuration variables lookup order:

+---------------+-----------------+---------------------+
| Lookup Order  | ``prettyconf``  | ``python-decouple`` |
+---------------+-----------------+---------------------+
| 1             | *envvar*        | ``.env``            |
+---------------+-----------------+---------------------+
| 2             | ``.env``        | ``settings.ini``    |
+---------------+-----------------+---------------------+
| 3             | ``*.cfg|*.ini`` | *envvar*            |
+---------------+-----------------+---------------------+


Why you created a library similar to python-decouple instead of with it?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

I contributed with 'python-decouple' in the past but I needed to change its
behaviour as described above and this change is backward-incompatible with
current version of ``python-decouple``. Besides that it's hard to make this
change due to implementation details of this library.


Why use ``prettyconf`` instead of ``python-decouple``?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use any of them. Both are good libraries and provides a similar set of
features.


.. _`12 Factor`: http://12factor.net/
.. _`python-decouple`: https://github.com/henriquebastos/python-decouple
.. _dj-database-url: https://github.com/kennethreitz/dj-database-url
.. _django-cache-url: https://github.com/ghickman/django-cache-url


.. |Build Status| image:: https://travis-ci.org/osantana/prettyconf.png?branch=master
   :target: https://travis-ci.org/osantana/prettyconf
.. |Coverage Status| image:: https://coveralls.io/repos/osantana/prettyconf/badge.svg?branch=master
   :target: https://coveralls.io/r/osantana/prettyconf?branch=master
