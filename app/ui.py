import logging
from datetime import UTC, datetime

from nicegui import run, ui

from app.database import TicketRepository
from app.models import Ticket, TicketCreate, TicketFilters, TicketPriority, TicketStatus, TicketUpdate


logger = logging.getLogger(__name__)


def mount_ui(repository: TicketRepository) -> None:
    @ui.page("/")
    def ticket_dashboard() -> None:
        def current_tickets() -> list[Ticket]:
            return repository.list(filters=current_filters())

        def current_filters() -> TicketFilters:
            return TicketFilters(
                status=None if status_filter.value == "all" else TicketStatus(status_filter.value),
                priority=None if priority_filter.value == "all" else TicketPriority(priority_filter.value),
                search=search.value.strip() if search.value and search.value.strip() else None,
            )

        def set_filter_controls_enabled(enabled: bool) -> None:
            for control in (status_filter, priority_filter, search, refresh_button):
                control.enable() if enabled else control.disable()

        def set_form_controls_enabled(enabled: bool) -> None:
            for control in (title, requester, priority_input, description, create_button):
                control.enable() if enabled else control.disable()

        async def refresh() -> None:
            loading_row.set_visibility(True)
            set_filter_controls_enabled(False)
            try:
                tickets = await run.io_bound(current_tickets)
            except Exception:
                logger.exception("Could not load tickets")
                tickets_container.clear()
                with tickets_container:
                    ui.label("Tickets could not be loaded. Try refreshing.").classes("text-red-700")
            else:
                tickets_container.clear()
                with tickets_container:
                    if not tickets:
                        ui.label("No tickets match the current filters.").classes("text-gray-500")
                    for ticket in tickets:
                        render_ticket(ticket)
            finally:
                set_filter_controls_enabled(True)
                loading_row.set_visibility(False)

        async def create_ticket() -> None:
            validation_results = [field.validate() for field in (title, requester, description)]
            if not all(validation_results):
                ui.notify("Review the highlighted fields.", color="negative")
                return

            set_form_controls_enabled(False)
            try:
                ticket = TicketCreate(
                    title=title.value.strip(),
                    description=description.value.strip(),
                    requester=requester.value.strip(),
                    priority=TicketPriority(priority_input.value),
                )
                await run.io_bound(repository.create, ticket)
            except ValueError as error:
                ui.notify(str(error), color="negative")
                return
            except Exception:
                logger.exception("Could not create ticket")
                ui.notify("Ticket could not be created. Try again.", color="negative")
                return
            finally:
                set_form_controls_enabled(True)

            title.set_value("")
            description.set_value("")
            requester.set_value("")
            priority_input.set_value(TicketPriority.medium.value)
            ui.notify("Ticket created", color="positive")
            await refresh()

        def render_ticket(ticket: Ticket) -> None:
            with ui.card().classes("w-full rounded-lg border border-gray-200 shadow-sm"):
                with ui.row().classes("w-full flex-col items-start gap-4 md:flex-row md:justify-between"):
                    with ui.column().classes("min-w-0 flex-1 gap-1"):
                        ui.label(ticket.title).classes("text-lg font-semibold")
                        ui.label(ticket.description).classes("break-words text-gray-700")
                        ui.label(f"Requester: {ticket.requester}").classes("text-sm text-gray-500")
                        with ui.row().classes("flex-wrap gap-x-4 gap-y-1 pt-1 text-xs text-gray-500"):
                            ui.label(f"Created: {format_timestamp(ticket.created_at)}")
                            ui.label(f"Updated: {format_timestamp(ticket.updated_at)}")
                    with ui.column().classes("w-full gap-2 md:w-48"):
                        status_select = ui.select(
                            [status.value for status in TicketStatus],
                            value=ticket.status.value,
                            label="Status",
                            on_change=lambda event, ticket_id=ticket.id: update_status(ticket_id, event.value),
                        ).classes("w-full")
                        status_select.props("aria-label=Ticket status")
                        ui.label(f"Priority: {ticket.priority.value}").classes("text-sm font-medium uppercase text-gray-500")

        async def update_status(ticket_id: int, status_value: str) -> None:
            try:
                await run.io_bound(repository.update, ticket_id, TicketUpdate(status=TicketStatus(status_value)))
            except Exception:
                logger.exception("Could not update ticket %s", ticket_id)
                ui.notify("Ticket status could not be updated. Try again.", color="negative")
                await refresh()
                return
            ui.notify("Ticket updated", color="positive")
            await refresh()

        def format_timestamp(value: datetime) -> str:
            timestamp = value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
            return timestamp.strftime("%Y-%m-%d %H:%M UTC")

        ui.add_head_html(
            """
            <style>
                body { background: #f7f5ef; }
                .nicegui-content { max-width: 1180px; margin: 0 auto; }
            </style>
            """
        )

        with ui.column().classes("mx-auto w-full max-w-6xl gap-6 px-4 py-6 sm:px-6"):
            with ui.row().classes("w-full flex-wrap items-center justify-between gap-3"):
                with ui.column().classes("gap-1"):
                    ui.label("Ticket Desk").classes("text-3xl font-bold text-gray-900")
                    ui.label("Create, triage, and resolve support tickets.").classes("text-gray-600")
                refresh_button = ui.button(icon="refresh", on_click=refresh).props("flat round")
                refresh_button.tooltip("Refresh tickets")

            with ui.card().classes("w-full rounded-lg border border-gray-200 shadow-sm"):
                ui.label("New ticket").classes("text-xl font-semibold")
                with ui.element("div").classes("grid w-full grid-cols-1 gap-4 md:grid-cols-2"):
                    title = ui.input(
                        "Title",
                        validation={
                            "Title is required": lambda value: bool(value and value.strip()),
                            "Use 120 characters or fewer": lambda value: len(value.strip()) <= 120,
                        },
                    ).classes("w-full")
                    requester = ui.input(
                        "Requester",
                        validation={
                            "Requester is required": lambda value: bool(value and value.strip()),
                            "Use 100 characters or fewer": lambda value: len(value.strip()) <= 100,
                        },
                    ).classes("w-full")
                    priority_input = ui.select(
                        [priority.value for priority in TicketPriority],
                        value=TicketPriority.medium.value,
                        label="Priority",
                    ).classes("w-full")
                    description = ui.textarea(
                        "Description",
                        validation={
                            "Description is required": lambda value: bool(value and value.strip()),
                            "Use 2,000 characters or fewer": lambda value: len(value.strip()) <= 2000,
                        },
                    ).classes("w-full md:col-span-2")
                create_button = ui.button("Create ticket", icon="add", on_click=create_ticket).props("color=primary")

            with ui.row().classes("w-full flex-wrap items-end gap-3"):
                status_filter = ui.select(
                    ["all", *[status.value for status in TicketStatus]],
                    value="all",
                    label="Status",
                ).classes("w-full sm:w-44")
                priority_filter = ui.select(
                    ["all", *[priority.value for priority in TicketPriority]],
                    value="all",
                    label="Priority",
                ).classes("w-full sm:w-44")
                search = ui.input("Search").props("clearable").classes("w-full sm:min-w-64 sm:flex-1")

            with ui.row().classes("items-center gap-2 text-sm text-gray-500") as loading_row:
                ui.spinner(size="sm")
                ui.label("Loading tickets...")
            loading_row.set_visibility(False)

            tickets_container = ui.column().classes("w-full gap-3")

            status_filter.on("update:model-value", lambda _: refresh())
            priority_filter.on("update:model-value", lambda _: refresh())
            search.on(
                "update:model-value",
                lambda _: refresh(),
                throttle=0.3,
                leading_events=False,
                trailing_events=True,
            )

            ui.timer(0.01, refresh, once=True)
