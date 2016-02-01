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


What is the difference between prettyconf and python-decouple_?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is no subtantial difference between both libraries. ``prettyconf`` is
highly inspired in ``python-decouple`` and provides almost the same API.

The implementation of ``prettyconf`` is more extensible and flexible to make
behaviour configurations easier.

Why you created a library similar to python-decouple instead of use it?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

I made some_ contributions_ for python-decouple_ previously, but I needed
to change its behaviour as described above and this change is backward
incompatible, so, it could break software that relies on the old behaviour.
Besides that it's hard to make this change on ``python-decouple`` due to 
the way it's implemented.

.. _some: https://github.com/henriquebastos/python-decouple/pull/4
.. _contributions: https://github.com/henriquebastos/python-decouple/pull/5

Why use ``prettyconf`` instead of ``python-decouple``?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use any of them. Both are good libraries and provides a similar set of
features.


.. _`python-decouple`: https://github.com/henriquebastos/python-decouple

