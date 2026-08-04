prettyconf
==========

|Coverage Status| |Docs| |Codacy|

Pretty Conf is a Python library created to make easy the separation of
configuration and code following the recommendations of `12 Factor`_'s topic
about configs.

It is strongly inspired in `python-decouple`_ and both provides a similar
API. It is framework agnostic and works the same way under Django, Flask,
FastAPI or a plain command line script.


Installation
------------

.. code-block:: sh

    pip install prettyconf

The ``AwsParameterStore`` loader depends on ``boto3``. Install the optional
``aws`` feature if you need it:

.. code-block:: sh

    pip install prettyconf[aws]

``prettyconf`` requires Python 3.10 or newer.


Documentation
-------------

You can find ``prettyconf`` documentation at `Read the Docs`_ website.


Development
-----------

The project uses uv_ and a ``Makefile`` as its entry point. ``make setup``
bootstraps everything, installing uv first if it is missing:

.. code-block:: sh

    make setup

The remaining targets are listed by ``make help``:

============================ ==================================================
``make test``                run the test suite (``ARGS="-k name"`` to filter)
``make coverage``            run the test suite with a coverage report
``make lint``                check the code with ruff
``make format``              reformat and auto-fix the code with ruff
``make typecheck``           check the types with ty
``make docs``                build the HTML documentation
``make build``               build the sdist and the wheel
``make update-deps``         upgrade every dependency and refresh ``uv.lock``
============================ ==================================================

Any target accepts a ``PYTHON`` variable to run against another supported
interpreter, each one in its own virtualenv:

.. code-block:: sh

    make test PYTHON=3.10

Pull requests should keep ``make lint``, ``make typecheck`` and ``make test``
passing, and should describe the change well enough that a reviewer does not
need to open the linked issue. Releases are published to PyPI by GitHub
Actions when a GitHub release is created, which is what ``make release`` does.


.. _`12 Factor`: https://12factor.net/
.. _`Read the Docs`: https://prettyconf.readthedocs.io/
.. _`python-decouple`: https://github.com/henriquebastos/python-decouple
.. _uv: https://docs.astral.sh/uv/

.. |Coverage Status| image:: https://coveralls.io/repos/osantana/prettyconf/badge.svg?branch=main
   :target: https://coveralls.io/r/osantana/prettyconf?branch=main
.. |Docs| image:: https://readthedocs.org/projects/prettyconf/badge/?version=latest
   :target: https://readthedocs.org/projects/prettyconf/?badge=latest
.. |Codacy| image:: https://app.codacy.com/project/badge/Grade/e5caa8df7068427b829fb1f9760de3bc
    :target: https://app.codacy.com/gh/osantana/prettyconf/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade
