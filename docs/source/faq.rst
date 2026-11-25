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

But this code has some issues:

#. If *envvar* ``DEBUG=False`` this code will print ``True`` because
   ``os.environ.get("DEBUG", False)`` will return the string `'False'` instead
   of a boolean `False`. And a non-empty string has a ``True`` boolean value.
#. We can't (dis|en)able debug with *envvars* ``DEBUG=yes|no``, ``DEBUG=1|0``,
   ``DEBUG=True|False``.
#. If we want to use this configuration during development we need to define
   this *envvar* all the time. We can't define this setting in a configuration
   file that will be used if `DEBUG` *envvar* is not defined.


Is prettyconf tied to Django_, Flask_ or FastAPI_?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No, prettyconf was designed to be framework agnostic, be it for the web or cli
applications. You call ``config()`` the same way in any of them.

.. _`Django`: https://www.djangoproject.com/
.. _`Flask`: https://flask.palletsprojects.com/
.. _`FastAPI`: https://fastapi.tiangolo.com/


What is the difference between prettyconf and python-decouple_?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is no substantial difference between both libraries. ``prettyconf`` is
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


How does prettyconf compare to python-dotenv_?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

python-dotenv_ reads the key, value pair from .env file and adds them to
environment variable. It is good for some tools that simply proxy the env to
some other process, like docker-compose_ or pipenv_.

On the other hand, prettyconf does not populate the ``os.environ`` dictionary,
because it is designed to discover configuration from diferent sources, the
environment being just one of them.

.. _`python-dotenv`: https://github.com/theskumar/python-dotenv
.. _`pipenv`: https://pipenv.pypa.io/en/latest/shell.html#automatic-loading-of-env
.. _`docker-compose`: https://docs.docker.com/compose/how-tos/environment-variables/


How does prettyconf compare to pydantic-settings_?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

pydantic-settings_ declares the settings as a class. Each setting is an
attribute with a type annotation, and pydantic_ reads and validates all of them
when the class is instantiated. If two settings are wrong, the error lists the
two.

prettyconf reads one setting per ``config()`` call, at the line where you call
it. There is no class to declare, so a Django ``settings.py`` or a module of
constants stays written the way it already is. The price is in the errors: a
wrong setting raises when its line runs, and you only find the next wrong one
after fixing the first.

+----------------+----------------------------------+-------------------------------------+
|                | prettyconf                       | pydantic-settings                   |
+================+==================================+=====================================+
| Declaration    | one ``config()`` call per        | a class with annotated attributes   |
|                | setting                          |                                     |
+----------------+----------------------------------+-------------------------------------+
| Validation     | when each call runs, stops at    | when the class is instantiated,     |
|                | the first error                  | reports every error                 |
+----------------+----------------------------------+-------------------------------------+
| Types          | ``cast=config.int``, see         | the annotation of the attribute     |
|                | :doc:`casts`                     |                                     |
+----------------+----------------------------------+-------------------------------------+
| Secrets        | ``wrapper=config.secret``, see   | ``SecretStr`` and ``Secret[T]``     |
|                | :doc:`wrappers`                  |                                     |
+----------------+----------------------------------+-------------------------------------+
| Prefixes       | ``config["AUTH0_"]``             | ``env_prefix``                      |
+----------------+----------------------------------+-------------------------------------+
| ``.env`` file  | found by walking up from the     | the path given in ``env_file``      |
|                | file that called ``config()``    |                                     |
+----------------+----------------------------------+-------------------------------------+
| Dependencies   | none                             | pydantic, python-dotenv,            |
|                |                                  | typing-extensions and               |
|                |                                  | typing-inspection                   |
+----------------+----------------------------------+-------------------------------------+

pydantic-settings also reads from more places: a directory with one file per
secret, YAML and TOML files, and the secret managers of AWS, Azure and Google
Cloud. prettyconf reads environment variables, ``.env`` and ``.ini`` files,
command line arguments and the AWS Parameter Store, and you write a loader for
anything else.

The dependencies weigh differently in each project. pydantic has a compiled
core, and prettyconf is plain Python with nothing to install besides itself. If
your project already uses pydantic, as every FastAPI_ project does,
pydantic-settings costs you nothing new and gives you the settings as one
validated object. If it does not, prettyconf gets you typed settings and
secrets without bringing pydantic in.

.. _`pydantic-settings`: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
.. _`pydantic`: https://docs.pydantic.dev/
