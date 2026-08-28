import unittest

from app.database import TicketRepository
from app.models import TicketCreate, TicketPriority


class TicketCommentRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = TicketRepository(":memory:")
        self.ticket = self.repository.create(
            TicketCreate(
                title="Login issue",
                description="User cannot sign in.",
                requester="Sam",
                priority=TicketPriority.medium,
            )
        )

    def tearDown(self) -> None:
        self.repository.close()

    def test_add_and_list_comments_for_ticket(self) -> None:
        self.repository.add_comment(self.ticket.id, "Investigating the login flow.")
        self.repository.add_comment(self.ticket.id, "Escalated to backend team.")

        comments = self.repository.list_comments(self.ticket.id)

        self.assertEqual(
            comments,
            ["Investigating the login flow.", "Escalated to backend team."],
        )

    def test_comments_are_isolated_by_ticket(self) -> None:
        second_ticket = self.repository.create(
            TicketCreate(
                title="Billing issue",
                description="Invoice mismatch.",
                requester="Alex",
                priority=TicketPriority.high,
            )
        )

        self.repository.add_comment(self.ticket.id, "Need more details from customer.")
        self.repository.add_comment(second_ticket.id, "Check invoice history.")

        self.assertEqual(self.repository.list_comments(self.ticket.id), ["Need more details from customer."])
        self.assertEqual(self.repository.list_comments(second_ticket.id), ["Check invoice history."])


if __name__ == "__main__":
    unittest.main()