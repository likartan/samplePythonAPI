from collections.abc import Iterator

import pytest

from app.database import TicketRepository
from app.models import TicketCreate, TicketFilters, TicketPriority, TicketStatus, TicketUpdate


@pytest.fixture
def repository(tmp_path) -> Iterator[TicketRepository]:
    ticket_repository = TicketRepository(tmp_path / "tickets.duckdb")
    yield ticket_repository
    ticket_repository.close()


def create_tickets(repository: TicketRepository) -> tuple[int, int, int]:
    vpn_ticket = repository.create(
        TicketCreate(
            title="Laptop cannot connect to VPN",
            description="Remote access is blocked while traveling.",
            requester="Avery Stone",
            priority=TicketPriority.high,
        )
    )
    dashboard_ticket = repository.create(
        TicketCreate(
            title="New finance dashboard access",
            description="Grant read-only access for monthly reporting.",
            requester="Mina Patel",
            priority=TicketPriority.medium,
        )
    )
    display_ticket = repository.create(
        TicketCreate(
            title="Broken conference room display",
            description="The display does not wake over HDMI.",
            requester="Jon Bell",
            priority=TicketPriority.low,
        )
    )
    repository.update(dashboard_ticket.id, TicketUpdate(status=TicketStatus.resolved))
    return vpn_ticket.id, dashboard_ticket.id, display_ticket.id


def test_filters_by_status_and_priority(repository: TicketRepository) -> None:
    vpn_id, dashboard_id, _ = create_tickets(repository)

    assert [ticket.id for ticket in repository.list(TicketFilters(status=TicketStatus.resolved))] == [dashboard_id]
    assert [ticket.id for ticket in repository.list(TicketFilters(priority=TicketPriority.high))] == [vpn_id]


def test_search_is_trimmed_case_insensitive_and_matches_content(repository: TicketRepository) -> None:
    vpn_id, dashboard_id, _ = create_tickets(repository)

    assert [ticket.id for ticket in repository.list(TicketFilters(search="  CONNECT  "))] == [vpn_id]
    assert [ticket.id for ticket in repository.list(TicketFilters(search="REPORTING"))] == [dashboard_id]


def test_combines_filters(repository: TicketRepository) -> None:
    _, dashboard_id, _ = create_tickets(repository)

    filters = TicketFilters(
        status=TicketStatus.resolved,
        priority=TicketPriority.medium,
        search="dashboard",
    )

    assert [ticket.id for ticket in repository.list(filters)] == [dashboard_id]