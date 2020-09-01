Requirements
------------

* Python 2.7+ or 3.4+


Installation
------------

First you need to install ``prettyconf`` library:

.. code-block:: sh

    pip install prettyconf

The ``AwsParameterStore`` configuration loader depends on the ``boto3`` package.
If you need to use it, install ``prettyconf`` with the optional feature ``aws``:

.. code-block:: sh

    pip install prettyconf[aws]
