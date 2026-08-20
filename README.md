# Ticketing System

A support ticket management application built with **FastAPI**, **NiceGUI**, and **DuckDB**. It provides a REST API for ticket CRUD operations and a web-based dashboard for creating, filtering, and resolving tickets.

> ⚠️ **Note:** This codebase contains **deliberate bugs** intended for a training/debugging exercise. See [Known Bugs](#known-bugs) for a full list.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Data Models](#data-models)
- [Database Schema](#database-schema)
- [Web UI](#web-ui)
- [Known Bugs](#known-bugs)

---

## Overview

The Ticketing System is an IT helpdesk-style application where users can:

- **Create** support tickets with a title, description, requester name, and priority level.
- **List** all tickets, optionally filtered by status, priority, or free-text search.
- **Update** ticket status, priority, and other fields as work progresses.
- **Delete** tickets that are no longer needed.
- **View** tickets through a NiceGUI-powered web dashboard at `/`.

The app uses an embedded DuckDB database (no external database server required) and ships with seed data on first run.

---

## Tech Stack

| Component       | Technology  | Purpose                                      |
|-----------------|-------------|----------------------------------------------|
| Web framework   | FastAPI     | REST API endpoints and application server    |
| UI framework    | NiceGUI     | Web-based dashboard built on top of FastAPI  |
| Database        | DuckDB      | Embedded analytical database (file-based)    |
| Data validation | Pydantic    | Request/response models and validation       |
| ASGI server     | Uvicorn     | Serves the FastAPI application               |

---

## Project Structure

```
samplePythonAPI/
├── README.md              # This documentation
├── requirements.txt       # Python dependencies
└── app/
    ├── __init__.py         # Package marker
    ├── main.py             # Application factory and entry point
    ├── api.py              # REST API router (ticket CRUD endpoints)
    ├── database.py         # DuckDB repository (data access layer)
    ├── models.py           # Pydantic models and enums
    └── ui.py               # NiceGUI web dashboard
```

---

## Getting Started

### Prerequisites

- Python 3.12+

### Installation

```powershell
# Create and activate a virtual environment (optional but recommended)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```powershell
uvicorn app.main:app --reload
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

- The **web dashboard** is served at `/`
- The **API** is available at `/api/tickets`
- The **health check** is at `/health`
- Interactive **API docs** (Swagger UI) are auto-generated at `/docs`

### Running Tests

```powershell
pytest
```

---

## Configuration

The application can be configured via environment variables:

| Variable          | Default              | Description                                      |
|-------------------|----------------------|--------------------------------------------------|
| `TICKET_DB_PATH`  | `data/tickets.duckdb`| Path to the DuckDB database file. Use `:memory:` for an in-memory database. |
| `PORT`            | `8000`               | Port the server listens on (when run via `python -m app.main`). |
| `NICEGUI_SECRET`  | `dev-secret`         | Secret key for NiceGUI browser storage encryption. |

Example:

```powershell
$env:TICKET_DB_PATH = "data/my_tickets.duckdb"
$env:PORT = "9000"
uvicorn app.main:app --reload
```

---

## Architecture

The application follows a layered architecture:

```
┌──────────────────────────────────────────────┐
│                  main.py                      │
│         Application factory & entry           │
│   Creates FastAPI app, wires up routes        │
└──────────┬───────────────────────┬───────────┘
           │                       │
           ▼                       ▼
┌──────────────────┐    ┌──────────────────────┐
│     api.py        │    │       ui.py           │
│  REST API layer   │    │   NiceGUI dashboard   │
│  /api/tickets/*   │    │   served at /         │
└────────┬──────────┘    └──────────┬───────────┘
         │                          │
         ▼                          ▼
┌──────────────────────────────────────────────┐
│                database.py                     │
│          TicketRepository class                │
│     Data access layer (CRUD operations)        │
│     Manages DuckDB connection & threading      │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│                  models.py                     │
│       Pydantic models & enums                  │
│  Ticket, TicketCreate, TicketUpdate, etc.      │
└──────────────────────────────────────────────┘
```

### Key Design Decisions

- **Single repository instance:** `main.py` creates one `TicketRepository` and passes it to both the API router and the UI, so they share the same database connection.
- **Thread-safe database access:** `TicketRepository` uses a `threading.Lock` to serialize DuckDB operations, since DuckDB connections are not thread-safe by default.
- **Lifespan management:** The FastAPI lifespan context manager ensures the database connection is properly closed on shutdown.
- **Embedded database:** DuckDB stores data in a single file (`data/tickets.duckdb`), requiring no external database server.

---

## API Reference

All endpoints are prefixed with `/api`.

### `GET /health`

Returns service health status.

**Response:**
```json
{ "status": "ok" }
```

---

### `GET /api/tickets`

List all tickets, optionally filtered.

**Query Parameters:**

| Parameter  | Type             | Required | Description                              |
|------------|------------------|----------|------------------------------------------|
| `status`   | `open`, `in_progress`, `resolved`, `closed` | No | Filter by ticket status. |
| `priority` | `low`, `medium`, `high`, `urgent`           | No | Filter by priority.      |
| `search`   | `string`         | No       | Free-text search across title, description, and requester. |

**Response:** `200 OK` — Array of [`Ticket`](#ticket) objects.

---

### `POST /api/tickets`

Create a new ticket.

**Request Body:** [`TicketCreate`](#ticketcreate) object.

```json
{
  "title": "Laptop cannot connect to VPN",
  "description": "Requester is blocked from accessing internal systems.",
  "requester": "Avery Stone",
  "priority": "high"
}
```

**Response:** `201 Created` — The created [`Ticket`](#ticket) object.

---

### `GET /api/tickets/{ticket_id}`

Retrieve a single ticket by ID.

**Response:** `200 OK` — [`Ticket`](#ticket) object, or `404` if not found.

---

### `PATCH /api/tickets/{ticket_id}`

Partially update a ticket. Only provided fields are updated.

**Request Body:** [`TicketUpdate`](#ticketupdate) object (all fields optional).

```json
{
  "status": "resolved",
  "priority": "low"
}
```

**Response:** `200 OK` — Updated [`Ticket`](#ticket) object, or `404` if not found.

---

### `DELETE /api/tickets/{ticket_id}`

Delete a ticket by ID.

**Response:** `204 No Content`, or `404` if not found.

---

## Data Models

### Enums

#### `TicketStatus`

| Value          | Description                        |
|----------------|------------------------------------|
| `open`         | Ticket is newly created            |
| `in_progress`  | Someone is actively working on it  |
| `resolved`     | Issue has been fixed               |
| `closed`       | Ticket is fully closed             |

#### `TicketPriority`

| Value    | Description                      |
|----------|----------------------------------|
| `low`    | Low priority                     |
| `medium` | Medium priority (default)        |
| `high`   | High priority                    |
| `urgent` | Urgent — needs immediate attention |

### Models

#### `TicketCreate`

Used when creating a new ticket.

| Field         | Type             | Required | Default   | Constraints              |
|---------------|------------------|----------|-----------|--------------------------|
| `title`       | `string`         | Yes      | —         | 0–120 characters         |
| `description` | `string`         | Yes      | —         | 0–2000 characters        |
| `requester`   | `string`         | Yes      | —         | 0–80 characters          |
| `priority`    | `TicketPriority` | No       | `medium`  | One of the enum values   |

#### `TicketUpdate`

Used when partially updating a ticket. All fields are optional — only provided fields are updated.

| Field         | Type             | Default | Constraints (when provided) |
|---------------|------------------|---------|------------------------------|
| `title`       | `string`         | `null`  | 3–120 characters             |
| `description` | `string`         | `null`  | 3–2000 characters            |
| `requester`   | `string`         | `null`  | 2–80 characters              |
| `priority`    | `TicketPriority` | `null`  | One of the enum values       |
| `status`      | `TicketStatus`   | `null`  | One of the enum values       |

#### `Ticket`

The full ticket representation returned by the API.

| Field         | Type             | Description                          |
|---------------|------------------|--------------------------------------|
| `id`          | `integer`        | Unique auto-incremented ID           |
| `title`       | `string`         | Short summary of the issue           |
| `description` | `string`         | Detailed description                 |
| `requester`   | `string`         | Name of the person requesting help   |
| `priority`    | `TicketPriority` | Priority level                       |
| `status`      | `TicketStatus`   | Current status                       |
| `created_at`  | `datetime`       | When the ticket was created          |
| `updated_at`  | `datetime`       | When the ticket was last updated     |

#### `TicketFilters`

Used internally for filtering ticket queries.

| Field      | Type             | Default | Description             |
|------------|------------------|---------|-------------------------|
| `status`   | `TicketStatus`   | `null`  | Filter by status        |
| `priority` | `TicketPriority` | `null`  | Filter by priority      |
| `search`   | `string`         | `null`  | Free-text search term   |

---

## Database Schema

The application uses DuckDB with two tables:

### `tickets` table

| Column        | Type       | Description                                      |
|---------------|------------|--------------------------------------------------|
| `id`          | `INTEGER`  | Primary key, auto-incremented via `ticket_id_seq`|
| `title`       | `VARCHAR`  | Ticket title                                     |
| `description` | `VARCHAR`  | Detailed description                             |
| `requester`   | `VARCHAR`  | Requester name                                   |
| `priority`    | `VARCHAR`  | Priority (`low`, `medium`, `high`, `urgent`)     |
| `status`      | `VARCHAR`  | Status (`open`, `in_progress`, `resolved`, `closed`) |
| `created_at`  | `TIMESTAMP`| Creation timestamp (UTC)                         |
| `updated_at`  | `TIMESTAMP`| Last update timestamp (UTC)                      |

### `ticket_audit` table

| Column       | Type       | Description                          |
|--------------|------------|--------------------------------------|
| `ticket_id`  | `INTEGER`  | Reference to the ticket              |
| `message`    | `VARCHAR`  | Audit log message                    |
| `created_at` | `TIMESTAMP`| When the audit entry was created     |

### Seed Data

On first run (when the database is empty), the app seeds three sample tickets:

1. **"Laptop cannot connect to VPN"** — High priority, requested by Avery Stone
2. **"New finance dashboard access"** — Medium priority, requested by Mina Patel
3. **"Broken conference room display"** — Low priority, requested by Jon Bell

---

## Web UI

The NiceGUI dashboard is served at `/` and provides:

- **Ticket list** — Displays all tickets as cards with title, description, requester, status dropdown, and priority label.
- **Filters** — Status dropdown, priority dropdown, and search box. The list updates automatically when filters change.
- **Create form** — Title, requester, priority, and description fields with a "Create ticket" button.
- **Inline status updates** — Each ticket card has a status dropdown that updates the ticket immediately when changed.
- **Refresh button** — Manually reloads the ticket list.

---

## Known Bugs

> ⚠️ This project is a **training exercise** with intentionally introduced bugs. Below is a summary. See the [bug analysis](#) for details.

### Fatal (app won't start or core operations fail)

| # | File         | Bug                                                                 |
|---|--------------|---------------------------------------------------------------------|
| 1 | `models.py`  | Missing closing quote on `urgent = "urgent` — syntax error         |
| 2 | `database.py`| `seed_defaults()` queries non-existent `total` column              |
| 3 | `database.py`| `create()` inserts into `requestor` column (should be `requester`) |
| 4 | `database.py`| `list()` queries `ticket` table (should be `tickets`)              |
| 5 | `database.py`| `delete()` deletes all tickets *except* the target (`id != ?`)     |
| 6 | `api.py`     | `create_ticket()` returns ticket at `created.id + 1000`            |
| 7 | `api.py`     | `delete_ticket()` deletes `ticket_id + 1` instead of `ticket_id`  |

### Functional (wrong behavior, wrong data)

| #  | File         | Bug                                                                  |
|----|--------------|----------------------------------------------------------------------|
| 8  | `models.py`  | `TicketCreate` field length limits too restrictive (description: 20, requester: 8) |
| 9  | `database.py`| `seed_defaults()` condition `count < 0` never true (should be `> 0`)|
| 10 | `database.py`| `list()` swaps status/priority filter columns                       |
| 11 | `database.py`| `list()` search uses `=` instead of `LIKE`                          |
| 12 | `database.py`| `update()` returns ticket ID 1 instead of the actual ticket         |
| 13 | `database.py`| `_row_to_ticket()` swaps status and priority keys                   |
| 14 | `api.py`     | `list_tickets()` ignores filter parameters                          |
| 15 | `api.py`     | `get_ticket()` returns 500 instead of 404 on not found              |
| 16 | `ui.py`      | `create_ticket()` swaps description/requester values, ignores priority |
| 17 | `ui.py`      | `update_status()` updates `ticket_id + 1` instead of `ticket_id`   |
| 18 | `ui.py`      | `current_tickets()` filter logic is inverted                        |

### UI/CSS

| #  | File    | Bug                                                        |
|----|---------|------------------------------------------------------------|
| 19 | `ui.py` | CSS `.q-btn { display: none }` hides all buttons           |
| 20 | `ui.py` | CSS `.q-field { transform: rotate(1deg) }` tilts all inputs|
