# Support Ticket Application Specification

## 1. Purpose and Product Boundary

This repository defines a deliberately small support-ticket application for a debugging workshop. It provides:

- a JSON API built with FastAPI;
- a browser dashboard built with NiceGUI;
- Pydantic models for validation and serialization; and
- local persistence in DuckDB.

This document specifies the intended working application. The current branch contains deliberate defects and does not conform to this specification. Section 11 records the observed discrepancies so that broken behavior is not mistaken for required behavior.

Requirements marked **Inferred** are not stated completely by the existing README or implementation. They were selected to make the intended contract coherent and testable.

The application is a local workshop system, not a production service. Authentication, authorization, pagination, multi-process database access, schema migrations, formal accessibility certification, and production deployment are outside its scope.

## 2. User Workflows

### 2.1 API client

An API client can:

1. create a ticket;
2. list tickets, optionally filtered by status, priority, and search text;
3. retrieve one ticket by ID;
4. partially update a ticket;
5. permanently delete a ticket; and
6. determine whether the application and database are available.

### 2.2 Dashboard user

A dashboard user can:

1. create a ticket;
2. browse tickets;
3. filter tickets by status and priority;
4. search ticket titles and descriptions;
5. inspect all ticket details;
6. change a ticket's status; and
7. explicitly refresh the current result set.

General ticket editing and deletion are API-only operations. Audit history is not a product feature.

### 2.3 Access model

Anyone who can access the application can read and mutate tickets. There are no users, sessions, roles, or permissions.

## 3. Architecture and Responsibilities

The dependency direction is:

```text
app.main -> app.api / app.ui -> app.database -> app.models
```

### `app/models.py`

Defines ticket status and priority values, creation and update payloads, filter input, and the serialized ticket representation. It owns field-level validation.

### `app/database.py`

Owns the DuckDB connection, idempotent schema initialization, sample-data seeding, ticket CRUD operations, filtering, ordering, and conversion from database rows to domain models.

### `app/api.py`

Defines the `/api` HTTP routes. It translates domain and repository outcomes into stable HTTP responses without exposing database internals.

### `app/ui.py`

Defines the NiceGUI dashboard at `/`. It invokes the repository through task-focused controls and presents loading, empty, success, and failure states.

### `app/main.py`

Composes the application, selects the database path, initializes and seeds the repository, registers the API and UI, defines health behavior, and closes the repository during shutdown.

One repository instance and one DuckDB connection are shared by the API and UI within the process.

## 4. Domain Model and Invariants

### 4.1 Enumerations

Ticket status is exactly one of:

- `open`
- `in_progress`
- `resolved`
- `closed`

Ticket priority is exactly one of:

- `low`
- `medium`
- `high`
- `urgent`

Status may change directly from any value to any other value. A constrained transition workflow is out of scope.

### 4.2 Ticket fields

| Field | Type | Rules |
| --- | --- | --- |
| `id` | integer | Positive, unique, database-assigned, immutable, and never reused after deletion. |
| `title` | string | Required, trimmed, 1 to 120 characters. |
| `description` | string | Required, trimmed, 1 to 2,000 characters. **Inferred.** |
| `requester` | string | Required, trimmed, 1 to 100 characters. **Inferred.** |
| `priority` | enum | Optional on creation; defaults to `medium`. |
| `status` | enum | Assigned `open` on creation; clients cannot set it in the creation payload. |
| `created_at` | timestamp | Assigned by the system once and immutable. |
| `updated_at` | timestamp | Initially equals `created_at`; refreshed by a successful nonempty update. |

API timestamps are ISO 8601 values representing UTC. Clients cannot assign either timestamp. Numeric ID ordering does not replace timestamp ordering.

### 4.3 Creation

A creation payload contains `title`, `description`, `requester`, and optional `priority`. Unknown or invalid enum values and fields that fail validation are rejected. The persisted ticket is returned with its generated identity, `open` status, and timestamps.

### 4.4 Partial updates

A partial update can include any subset of `title`, `description`, `requester`, `priority`, and `status`.

- Text fields follow the same rules as creation.
- Explicit `null` is invalid for every field.
- An empty object is a valid no-op and returns the requested ticket unchanged.
- A no-op does not change `updated_at`.
- A successful nonempty update changes `updated_at`.

## 5. API Contract

FastAPI's standard validation response is used for malformed request data. No custom global error envelope is required.

### 5.1 Health

#### `GET /health`

Runs a lightweight query against DuckDB.

- `200 OK` with `{"status": "ok"}` when the query succeeds.
- `503 Service Unavailable` with a generic detail message when the database cannot be queried.

### 5.2 List tickets

#### `GET /api/tickets`

Optional query parameters:

| Parameter | Behavior |
| --- | --- |
| `status` | Exact enum match. |
| `priority` | Exact enum match. |
| `search` | Trimmed, case-insensitive substring match against title or description. **Inferred.** |

Supplied filters are combined with logical `AND`. Omitted or blank search text applies no search restriction. A blank `status` or `priority` parameter is invalid; clients must omit unused enum filters. Repeated query parameters are outside the contract.

Results are ordered by `created_at` descending, then `id` descending. The response is `200 OK` with a JSON array; no matches produce an empty array. Pagination is not required.

### 5.3 Create ticket

#### `POST /api/tickets`

Accepts a creation payload and returns `201 Created` with the persisted ticket.

### 5.4 Retrieve ticket

#### `GET /api/tickets/{ticket_id}`

Returns `200 OK` with the ticket. An unknown ID returns:

```json
{
  "detail": "Ticket <id> not found"
}
```

with `404 Not Found`.

### 5.5 Update ticket

#### `PATCH /api/tickets/{ticket_id}`

Accepts a partial update and returns `200 OK` with the persisted ticket. An unknown ID uses the uniform `404` response defined above.

### 5.6 Delete ticket

#### `DELETE /api/tickets/{ticket_id}`

Permanently deletes only the specified ticket and returns `204 No Content` with no body. An unknown ID uses the uniform `404` response defined above.

### 5.7 Error boundaries

- Invalid path values, query enums, and request payloads use FastAPI's standard `422 Unprocessable Entity` response.
- Missing tickets return the uniform `404` response.
- Unexpected database or server failures return `500 Internal Server Error` with a generic detail message.
- SQL, database paths, stack traces, and internal exception text are never returned to clients.
- Original unexpected exceptions are logged server-side.

## 6. Dashboard Behavior

The dashboard at `/` provides:

- a create-ticket form for title, description, requester, and priority;
- status and priority filters;
- free-text search;
- a refresh command;
- ticket cards containing title, full description, requester, priority, status, creation time, and update time; and
- a status selector for each ticket.

Changing a filter applies it automatically. Search input is debounced. Refresh reloads data using the current criteria. Filters follow the same combination, matching, and ordering rules as the API.

During a mutation, controls that could repeat that mutation are disabled. After a successful creation or status change, the UI:

1. displays a success notification;
2. refreshes the visible result set; and
3. clears the creation form only when creation succeeded.

Failures display a readable notification and preserve user input. The page has explicit loading and empty states.

The dashboard must be usable on desktop and narrow mobile viewports. Controls have proper labels, support keyboard operation, display visible focus and validation feedback, and remain visible and legible. Loading and refresh behavior must not cause incoherent layout shifts. Formal WCAG certification is not required.

## 7. Persistence, Startup, and Configuration

### 7.1 DuckDB

The application uses one local DuckDB database. `TICKET_DB_PATH` selects its location and defaults to `data/tickets.duckdb` relative to the working directory.

Schema initialization is idempotent. The intended schema contains a `tickets` table and a sequence that supplies ticket IDs. The unused `ticket_audit` table is not part of the intended schema.

Each repository mutation is atomic. A process-local lock protects access to the shared connection. Multi-process writes and schema migration management are outside scope.

### 7.2 Sample data

On startup, the application inserts the following deterministic records only when the ticket table is empty:

| Title | Requester | Priority |
| --- | --- | --- |
| Laptop cannot connect to VPN | Avery Stone | `high` |
| New finance dashboard access | Mina Patel | `medium` |
| Broken conference room display | Jon Bell | `low` |

Their descriptions are the existing sample descriptions in `app/database.py`. Each sample starts with `open` status. Repeated startup never duplicates samples and never modifies a nonempty database.

If schema initialization or sample seeding fails, application startup fails and the original cause is logged. The application does not start in a partially initialized mode.

### 7.3 Runtime

- Python 3.11 or newer is required.
- Dependencies are installed from `requirements.txt`.
- The primary development command is `uvicorn app.main:app --reload` from the repository root.
- `python -m app.main` may remain as a secondary startup path.
- `NICEGUI_SECRET` may use a local-development default but must be explicitly configured outside local development.

## 8. Acceptance Criteria

Conformance is demonstrated with focused automated tests.

### 8.1 Models

- All enum values serialize and validate correctly.
- Creation trims text and enforces required lengths.
- Creation defaults priority and does not accept status or timestamps.
- Updates accept subsets and reject explicit `null` and invalid values.

### 8.2 Repository

- An isolated temporary DuckDB database initializes successfully.
- Initialization and empty-database seeding are idempotent.
- A nonempty database is never seeded.
- Create, get, update, empty update, and delete affect only the requested ticket.
- Missing IDs produce `TicketNotFoundError` consistently.
- Filters work independently and in combination.
- Search is case-insensitive and matches title or description substrings.
- Results use the required deterministic ordering.
- Row conversion maps every field correctly.

### 8.3 API

- Every route returns the documented success status and body.
- Unknown IDs return the uniform `404` response for get, update, and delete.
- Invalid payloads, IDs, and enum filters return `422`.
- Unexpected failures do not expose internal details.
- Health returns `200` for a queryable database and `503` otherwise.

### 8.4 UI

- The page loads and displays seeded tickets.
- A user can create a ticket with the selected priority.
- Filters, debounced search, and refresh use current criteria.
- A status change updates the selected ticket only.
- Empty, loading, success, validation, and failure states are visible.
- Core workflows remain usable at desktop and narrow mobile widths.

Exhaustive browser compatibility and load testing are not required.

## 9. Explicitly Out of Scope

- authentication, authorization, users, and roles;
- audit history;
- attachments, comments, assignment, categories, or service-level agreements;
- constrained status transitions;
- pagination and client-selected sorting;
- soft deletion and archival;
- multi-process DuckDB coordination;
- schema migration tooling;
- production deployment, monitoring, and backup policy; and
- formal accessibility certification.

## 10. Repository Understanding

The application is intentionally layered but compact. `main.py` constructs one repository and passes it to both interfaces. The API and UI should remain thin adapters: validation belongs in models, persistence rules belong in the repository, and application composition belongs in `main.py`.

The central data path is:

```text
HTTP or UI input
    -> Pydantic validation
    -> TicketRepository operation
    -> DuckDB
    -> Ticket model
    -> JSON response or dashboard rendering
```

Most current failures are local violations of that path: inputs are forwarded incorrectly, SQL refers to incorrect columns or tables, and rows are mapped into the wrong fields.

## 11. Current Implementation Discrepancies

This section is diagnostic, not normative. It describes the repository as inspected on 2026-08-20.

### 11.1 Startup and models

- `app/models.py` has an unterminated string for the `urgent` priority, preventing Python from importing the application.
- Creation permits empty title, description, and requester values.
- Creation limits description to 20 characters and requester to 8, rejecting the supplied samples and ordinary input.
- Creation and update use inconsistent text constraints.
- Python 3.11 is required by `StrEnum` but is not documented in the README.

### 11.2 Initialization and seeding

- Seed counting selects a nonexistent `total` column.
- The seed guard checks whether the count is less than zero, so it cannot detect an already-populated database.
- Sample values violate the current creation constraints.
- The audit table is created but never written or read.

### 11.3 Repository CRUD and queries

- Creation inserts into misspelled column `requestor` instead of `requester`.
- Listing selects from nonexistent table `ticket` instead of `tickets`.
- Status and priority filter columns are reversed.
- Search compares wildcard strings with equality rather than using substring matching.
- Search includes requester even though the intended contract searches title and description.
- Results are sorted oldest first rather than newest first.
- An empty update returns ticket 1 instead of the requested ticket.
- Explicit `null` updates can reach `NOT NULL` database columns.
- Delete uses `id != ?`, deleting tickets other than the requested ticket.
- Row conversion swaps the status and priority positions returned by `SELECT *`.

### 11.4 API

- List forwarding ignores priority and treats status as search text.
- Create persists a ticket and then retrieves `created.id + 1000`, producing an internal error.
- A missing ticket on retrieval is translated to `500` with `database exploded` instead of `404`.
- Delete adds one to the requested ID before calling the repository.
- Unexpected repository failures are not translated into a generic error boundary.
- Health reports process availability without checking DuckDB.

### 11.5 Dashboard

- Active filters cause the UI to discard all filter values.
- Creation swaps requester and description and forces `urgent`, ignoring selected priority.
- Status changes target `ticket_id + 1`.
- CSS hides all Quasar buttons and rotates form fields, preventing normal use.
- Filter controls are not laid out in their intended row.
- Loading, empty, success, and general error states are incomplete.
- Ticket cards omit timestamps.

### 11.6 Tooling and documentation

- No tests or test configuration exist.
- The README instructs users to run `pytest`, but pytest is not declared in `requirements.txt`.
- Installation steps, the supported Python version, and environment configuration are incomplete.

## 12. Suggested Repair Sequence

1. Repair the priority enum syntax so the package can import.
2. Add isolated model tests and align creation and update validation with Section 4.
3. Repair schema initialization, row mapping, and idempotent seeding; verify them against a temporary database.
4. Repair repository CRUD, filtering, search, ordering, and missing-ID behavior with repository tests.
5. Repair API argument forwarding and HTTP error translation; add API integration tests.
6. Repair dashboard field mapping, filtering, mutation targets, layout, and user states; add UI smoke tests.
7. Make health database-aware and verify startup failure and shutdown behavior.
8. Update the README and dependency declarations to match the supported runtime and test commands.

The repair is complete when the acceptance criteria in Section 8 pass and the discrepancy list no longer describes observable behavior.