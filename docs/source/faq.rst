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
   of a boolean `False`. And a non-empty string has a ``True`` boolean value.
#. We can't (dis|en)able debug with *envvars* ``DEBUG=yes|no``, ``DEBUG=1|0``,
   ``DEBUG=True|False``.
#. If we want to use this configuration during development we need to define
   this *envvar* all the time. We can't define this setting in a configuration
   file that will be used if `DEBUG` *envvar* is not defined.


Is prettyconf tied to Django_ or Flask_?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No, prettyconf was designed to be framework agnostic, be it for the web or cli
applications.

.. _`Django`: https://www.djangoproject.com/
.. _`Flask`: http://flask.pocoo.org/


What is the difference between prettyconf and python-decouple_?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is no subtantial difference between both libraries. ``prettyconf`` is
highly inspired in ``python-decouple`` and provides almost the same API.

The implementation of ``prettyconf`` is more extensible and flexible to make
behaviour configurations easier.

You can use any of them. Both are good libraries and provides a similar set of
features.

.. _`python-decouple`: https://github.com/henriquebastos/python-decouple


Why you created a library similar to python-decouple instead of use it?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

I made some_ contributions_ for python-decouple_ previously, but I needed
to change its behaviour as described above and this change is backward
incompatible, so, it could break software that relies on the old behaviour.
Besides that it's hard to make this change on ``python-decouple`` due to
the way it's implemented.

See the lookup order of configurations below

+---------------+------------------+------------------------+-------------------------+
| Lookup Order  | prettyconf       | python-decouple (<3.0) | python-decouple (>=3.0) |
+===============+==================+========================+=========================+
| 1             | ENVVAR           | .env                   | ENVVAR                  |
+---------------+------------------+------------------------+-------------------------+
| 2             | .env             | settings.ini           | .env                    |
+---------------+------------------+------------------------+-------------------------+
| 3             | \*.cfg or \*.ini | ENVVAR                 | settings.ini            |
+---------------+------------------+------------------------+-------------------------+

.. _some: https://github.com/henriquebastos/python-decouple/pull/4
.. _contributions: https://github.com/henriquebastos/python-decouple/pull/5


How does prettyconf compare to python-dotenv?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

python-dotenv_ reads the key, value pair from .env file and adds them to
environment variable. It is good for some tools that simply proxy the env to
some other process, like docker-compose_ or pipenv_.

On the other hand, prettyconf does not populate the ``os.environ`` dictionary,
because it is designed to discover configuration from diferent sources, the
environment being just one of them.

.. _`python-dotenv`: https://github.com/theskumar/python-dotenv
.. _`pipenv`: https://pipenv.readthedocs.io/en/latest/advanced/#automatic-loading-of-env
.. _`docker-compose`: https://docs.docker.com/compose/env-file/
