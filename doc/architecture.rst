Architecture
============

The application uses a compact layered design. Dependencies point from
composition and interface modules toward persistence and domain models:

.. code-block:: text

   app.main -> app.api / app.ui -> app.database -> app.models

Application composition
-----------------------

``app.main`` creates one :class:`~app.database.TicketRepository`, optionally
seeds it, registers the API and dashboard, and closes the repository during the
FastAPI lifespan shutdown. The API and UI share that repository instance and
its DuckDB connection within one process.

HTTP adapter
------------

``app.api`` builds the ``/api`` router. FastAPI validates path, query, and body
input using the models from ``app.models``. The router delegates persistence to
the repository and translates repository outcomes into HTTP responses.

Dashboard adapter
-----------------

``app.ui`` mounts the NiceGUI dashboard at ``/``. Blocking DuckDB work is sent
through NiceGUI's I/O-bound runner so UI handlers remain asynchronous. The UI
constructs the same filter and update models used by API clients.

Persistence
-----------

:class:`~app.database.TicketRepository` owns the DuckDB connection, schema,
sample seeding, CRUD statements, filtering, and row-to-model conversion. A
process-local lock serializes access to the shared connection. Multi-process
coordination and schema migrations are outside this workshop application's
scope.

Domain models
-------------

``app.models`` defines the allowed status and priority values, write payloads,
filter input, and serialized ticket shape. Pydantic performs input validation
before data reaches the repository.

Request flow
------------

.. code-block:: text

   HTTP or UI input
       -> Pydantic validation
       -> TicketRepository operation
       -> DuckDB
       -> Ticket model
       -> JSON response or dashboard rendering

Intended behavior and workshop defects
---------------------------------------

This repository is designed for debugging practice. The architecture above is
stable, but individual implementations can deliberately violate the intended
contract. See :doc:`SPEC` for normative requirements and its current
implementation discrepancy list before interpreting unusual behavior as a
design decision.