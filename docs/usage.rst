=====
Usage
=====

To use EsignAnyWhere Python Client in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'esignanywhere_python_client.apps.EsignanywherePythonClientConfig',
        ...
    )

Add EsignAnyWhere Python Client's URL patterns:

.. code-block:: python

    from esignanywhere_python_client import urls as esignanywhere_python_client_urls


    urlpatterns = [
        ...
        url(r'^', include(esignanywhere_python_client_urls)),
        ...
    ]
