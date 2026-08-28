Getting Started
===============

Prerequisites
-------------

The application requires Python 3.11 or newer. Run all commands from the
repository root so that the ``app`` package and the default ``data`` directory
resolve correctly.

Installation
------------

Create and activate a virtual environment, then install the pinned runtime,
test, and documentation dependencies:

.. code-block:: powershell

   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt

Running the application
-----------------------

Start the development server with:

.. code-block:: powershell

   python -m uvicorn app.main:app --reload

Open ``http://localhost:8000`` for the dashboard. FastAPI exposes interactive
OpenAPI documentation at ``http://localhost:8000/docs`` and the health endpoint
at ``http://localhost:8000/health``.

Configuration
-------------

``TICKET_DB_PATH``
   Selects the DuckDB file. The default is ``data/tickets.duckdb`` relative to
   the current working directory. Use ``:memory:`` for a process-local database.

``NICEGUI_SECRET``
   Configures the NiceGUI storage secret. The application uses ``dev-secret``
   when the variable is absent; configure an explicit value outside local
   development.

``PORT``
   Selects the port used by ``python -m app.main``. The default is ``8000``.

Running tests
-------------

.. code-block:: powershell

   python -m pytest

The existing tests use temporary DuckDB files and focus on repository filter
and search behavior.

Building this documentation
---------------------------

Build a fresh HTML site and fail on warnings with:

.. code-block:: powershell

   python -m sphinx -M html doc _build --fail-on-warning --nitpicky --fresh-env

Open ``_build/html/index.html`` after the command succeeds.