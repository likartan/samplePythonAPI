Python API Reference
====================

This reference is generated from the currently checked-out Python modules.
Because importing ``app.main`` constructs the default application and opens a
database, its factory is documented manually to keep documentation builds free
of application side effects.

Models
------

.. automodule:: app.models
   :members:

Repository
----------

.. automodule:: app.database
   :members:

API router
----------

.. automodule:: app.api
   :members:

Dashboard
---------

.. automodule:: app.ui
   :members:

Application factory
-------------------

.. py:function:: create_app(database_path: str | None = None, seed: bool = True) -> fastapi.FastAPI

   Create the FastAPI application, repository, API router, and NiceGUI page.

   :param database_path: DuckDB path. When omitted, use ``TICKET_DB_PATH`` or
      ``data/tickets.duckdb``.
   :param seed: Insert the default tickets when the database is empty.
   :returns: The composed FastAPI application.

HTTP API
--------

The application registers these routes:

.. list-table::
   :header-rows: 1
   :widths: 18 30 52

   * - Method
     - Path
     - Purpose
   * - ``GET``
     - ``/health``
     - Report application health.
   * - ``GET``
     - ``/api/tickets``
     - List tickets with optional status, priority, and search filters.
   * - ``POST``
     - ``/api/tickets``
     - Create a ticket.
   * - ``GET``
     - ``/api/tickets/{ticket_id}``
     - Retrieve one ticket.
   * - ``PATCH``
     - ``/api/tickets/{ticket_id}``
     - Partially update one ticket.
   * - ``DELETE``
     - ``/api/tickets/{ticket_id}``
     - Permanently delete one ticket.

For request rules, status codes, response bodies, and intended error behavior,
see the :doc:`SPEC`.