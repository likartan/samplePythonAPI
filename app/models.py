"""Validated domain models for support tickets and repository filters."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class TicketStatus(StrEnum):
    """Lifecycle states accepted for a ticket."""

    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class TicketPriority(StrEnum):
    """Priority levels accepted for a ticket."""

    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class TicketCreate(BaseModel):
    """Input required to create a ticket."""

    title: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=2000)
    requester: str = Field(min_length=1, max_length=100)
    priority: TicketPriority = TicketPriority.medium


class TicketUpdate(BaseModel):
    """Fields that can be supplied when partially updating a ticket."""

    title: str | None = Field(default=None, min_length=3, max_length=120)
    description: str | None = Field(default=None, min_length=3, max_length=2000)
    requester: str | None = Field(default=None, min_length=2, max_length=80)
    priority: TicketPriority | None = None
    status: TicketStatus | None = None


class Ticket(BaseModel):
    """Persisted ticket returned by the repository and HTTP API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    requester: str
    priority: TicketPriority
    status: TicketStatus
    created_at: datetime
    updated_at: datetime


class TicketFilters(BaseModel):
    """Optional criteria combined when listing tickets."""

    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    search: str | None = None
