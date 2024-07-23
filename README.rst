=============================
EsignAnyWhere Python Client
=============================

.. image:: https://badge.fury.io/py/esignanywhere-python-client.svg/?style=flat-square
    :target: https://badge.fury.io/py/esignanywhere-python-client

.. image:: https://readthedocs.org/projects/pip/badge/?version=latest&style=flat-square
    :target: https://esignanywhere-python-client.readthedocs.io/en/latest/

.. image:: https://img.shields.io/coveralls/github/frankhood/esignanywhere-python-client/main?style=flat-square
    :target: https://coveralls.io/github/frankhood/esignanywhere-python-client?branch=main
    :alt: Coverage Status

Your project description goes here

Documentation
-------------

The full documentation is at https://esignanywhere-python-client.readthedocs.io.

Quickstart
----------

Install EsignAnyWhere Python Client::

    pip install esignanywhere-python-client

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'esignanywhere_python_client',
        ...
    )

Features
--------

* eSignAnyWhere DTO automatically generated
* eSignAnyWhere Client for docs creation on platform

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox


Development commands
---------------------

::

    pip install -r requirements_dev.txt
    invoke -l
