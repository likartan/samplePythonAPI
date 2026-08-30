# Ticket Comments Specification

This document explains how ticket comments work in this project. It is written
for developers who are new to the codebase and need to understand the complete
path from a user click to a saved comment.

## 1. What The Feature Does

A dashboard user can add a text comment to an existing ticket. The dashboard
then displays all comments belonging to that ticket in the order in which they
were added.

Comments are deliberately a small feature:

- comments are available through the NiceGUI dashboard only;
- there is no REST endpoint for comments;
- comments cannot be edited or deleted through the UI;
- comments do not have an author, status, or attachment; and
- comments are stored in DuckDB so they survive page refreshes and application
  restarts.

## 2. Where The Code Lives

The feature crosses three layers:

```text
NiceGUI dashboard (app/ui.py)
        |
        v
TicketRepository (app/database.py)
        |
        v
DuckDB table: ticket_comments
```

### `app/database.py`

Owns the comments table and the operations that write and read comments. The
UI should call these repository methods instead of executing SQL directly.

### `app/ui.py`

Owns the comment button, dialog, input validation, notifications, and display
of comments on each ticket card.

### `tests/test_repository_comments.py`

Checks that comments are saved in order and that comments for one ticket are
not returned for another ticket.

## 3. Database Schema

Application startup creates this table if it does not already exist:

```sql
CREATE TABLE IF NOT EXISTS ticket_comments (
    id INTEGER PRIMARY KEY DEFAULT nextval('ticket_id_seq'),
    ticket_id INTEGER NOT NULL,
    comment VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL
)
```

Column meanings:

| Column | Meaning |
| --- | --- |
| `id` | Unique database-generated comment ID. |
| `ticket_id` | ID of the ticket that owns the comment. |
| `comment` | The trimmed comment text. It cannot be empty in a valid application operation. |
| `created_at` | UTC timestamp assigned when the comment is saved. |

The schema is initialized by `TicketRepository._initialize()`. Initialization
is idempotent, so opening an existing database does not recreate or erase
comments.

## 4. Repository Contract

### `add_comment(ticket_id, comment)`

This method performs the following steps:

1. Removes whitespace at the beginning and end of `comment`.
2. Rejects an empty result with `ValueError("Comment cannot be empty")`.
3. Calls `get(ticket_id)` to verify that the ticket exists.
4. Inserts the ticket ID, trimmed text, and current timestamp into
   `ticket_comments`.
5. Returns the trimmed text.

An unknown ticket raises `TicketNotFoundError`. The method does not silently
create a comment for a nonexistent ticket.

Examples:

```python
repository.add_comment(12, "  Investigating the issue.  ")
# returns: "Investigating the issue."

repository.add_comment(12, "   ")
# raises: ValueError("Comment cannot be empty")
```

### `list_comments(ticket_id)`

This method:

1. verifies that the ticket exists by calling `get(ticket_id)`;
2. selects only rows whose `ticket_id` matches the requested ticket; and
3. orders rows by `created_at ASC, id ASC`.

It returns a `list[str]`, containing only comment text. The secondary `id`
ordering makes comments with the same timestamp deterministic.

An existing ticket with no comments returns an empty list. An unknown ticket
raises `TicketNotFoundError`.

## 5. Dashboard Flow

### Opening the dialog

Each rendered ticket card has a **Comment** button. The button captures that
ticket's ID and calls `open_comment_dialog(ticket_id)`.

The dialog contains:

- a textarea labelled `Comment`;
- a **Cancel** button, which closes the dialog without changing the database;
  and
- a **Save** button, which submits the text.

### Saving a comment

When **Save** is clicked, `submit_comment()`:

1. reads the textarea value;
2. trims it;
3. rejects blank text and shows a negative notification;
4. calls `repository.add_comment()` in NiceGUI's IO worker so the database
   operation does not block the UI event loop;
5. closes the dialog after a successful insert;
6. shows `Comment added`; and
7. refreshes the ticket list.

Refreshing is important: it causes each ticket to be rendered again, which
calls `list_comments(ticket.id)` and displays the newly saved comment.

If the repository rejects the comment, the dialog remains open and the error
message is shown to the user. The current UI specifically handles
`ValueError` for blank comments; unexpected failures follow the surrounding
NiceGUI error-handling behavior and should be logged rather than exposed as
database details.

### Displaying comments

When `render_ticket(ticket)` builds a card, it first calls
`repository.list_comments(ticket.id)`.

- If the returned list is empty, the card displays `No comments yet.`
- Otherwise, each comment is displayed as its own text row under the
  `Comments` heading.
- The rows use the repository's ascending order, so the oldest comment appears
  first and the newest appears last.

## 6. Isolation Rules

Comments belong to exactly one ticket through `ticket_id`.

For example, if ticket 1 has `First comment` and ticket 2 has `Second comment`:

```python
repository.list_comments(1)  # ["First comment"]
repository.list_comments(2)  # ["Second comment"]
```

The query always includes `WHERE ticket_id = ?`, so listing one ticket cannot
display another ticket's comments.

## 7. Testing Requirements

The focused tests use an in-memory DuckDB database. Each test creates its own
ticket and closes the repository afterward.

The tests must prove that:

1. two comments can be added to one ticket;
2. comments are returned in insertion order;
3. comments for separate tickets remain isolated; and
4. test data does not persist between test runs.

Run the focused test with:

```powershell
python -m pytest tests/test_repository_comments.py
```

The standard-library fallback is also available when `pytest` is not installed:

```powershell
python -m unittest discover -s tests -p 'test_repository_comments.py'
```

## 8. Out Of Scope

The current feature does not provide:

- comment authorship or authentication;
- comment update or deletion;
- comment pagination;
- API serialization of comments;
- file uploads or rich text; or
- notifications to other users.

Any of these additions would require an explicit change to the repository
contract, UI behavior, and tests.