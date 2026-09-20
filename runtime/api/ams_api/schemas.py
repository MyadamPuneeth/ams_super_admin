from datetime import date, datetime
from enum import StrEnum
from typing import Annotated
from uuid import UUID
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

class Role(StrEnum):
    ADMIN = "ADMIN"
    COACH = "COACH"
    FINANCE = "FINANCE"
    SCORER = "SCORER"
    ATHLETE = "ATHLETE"
    GUARDIAN = "GUARDIAN"

def trim(value: str) -> str:
    return value.strip()

def valid_email(value: str) -> str:
    value = value.strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
        raise ValueError("Enter a valid email address.")
    return value

class AcademyInput(ApiModel):
    name: Annotated[str, Field(min_length=2, max_length=100)]
    slug: Annotated[str, Field(min_length=3, max_length=50, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")]
    adminEmail: Annotated[str, Field(min_length=3, max_length=254)]
    _name = field_validator("name", mode="before")(trim)
    _email = field_validator("adminEmail", mode="before")(valid_email)

class BranchInput(ApiModel):
    name: Annotated[str, Field(min_length=2, max_length=100)]
    city: Annotated[str, Field(min_length=2, max_length=100)]
    address: Annotated[str, Field(min_length=3, max_length=300)]
    _name = field_validator("name", mode="before")(trim)
    _city = field_validator("city", mode="before")(trim)
    _address = field_validator("address", mode="before")(trim)

class TableInput(ApiModel):
    name: Annotated[str, Field(min_length=1, max_length=60)]
    _name = field_validator("name", mode="before")(trim)

class ScopeInput(ApiModel):
    roles: Annotated[list[Role], Field(min_length=1, max_length=6)]
    allBranches: bool
    branchIds: Annotated[list[UUID], Field(max_length=100)]
    @field_validator("roles")
    @classmethod
    def unique_roles(cls, value: list[Role]) -> list[Role]:
        if len(set(value)) != len(value): raise ValueError("Roles must be unique.")
        return value
    @field_validator("branchIds")
    @classmethod
    def unique_branches(cls, value: list[UUID]) -> list[UUID]:
        if len(set(value)) != len(value): raise ValueError("Branches must be unique.")
        return value

class InvitationInput(ScopeInput):
    email: Annotated[str, Field(min_length=3, max_length=254)]
    _email = field_validator("email", mode="before")(valid_email)

class MemberInput(ScopeInput):
    active: bool

class ActiveInput(ApiModel): active: bool
class AcceptInput(ApiModel): token: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
class DemoInput(ApiModel): userId: UUID

class AcademyDto(BaseModel): id: UUID; name: str; slug: str; active: bool; timezone: str; createdAt: datetime
class TableDto(BaseModel): id: UUID; name: str
class BranchDto(BaseModel): id: UUID; name: str; city: str; address: str; tables: list[TableDto]
class MemberDto(BaseModel): id: UUID; userId: UUID; name: str; email: str; roles: list[Role]; allBranches: bool; active: bool; branchIds: list[UUID]
class WorkspaceDto(BaseModel): academy: AcademyDto; membership: MemberDto
class MeDto(BaseModel): id: UUID; email: str; name: str; platformOwner: bool; workspaces: list[WorkspaceDto]
class InvitationDto(BaseModel): id: UUID; email: str; roles: list[Role]; allBranches: bool; branchIds: list[UUID]; expiresAt: datetime; acceptedAt: datetime | None; createdAt: datetime
class InvitationCreatedDto(BaseModel): id: UUID; invitationUrl: str
class AcademyCreatedDto(InvitationCreatedDto): academy: AcademyDto
class AuditDto(BaseModel): id: UUID; action: str; detail: str; createdAt: datetime
class DashboardDto(BaseModel): branches: int; tables: int; members: int | None; invitations: int | None
class DemoProfileDto(BaseModel): id: UUID; name: str; email: str; label: str
class AuthConfigDto(BaseModel): demo: bool; profiles: list[DemoProfileDto]
class TokenDto(BaseModel): accessToken: str
class AcceptDto(BaseModel): academyId: UUID

class AthleteInput(ApiModel):
    name: Annotated[str, Field(min_length=2, max_length=100)]
    membershipId: UUID | None = None
    _name = field_validator("name", mode="before")(trim)
class GuardianLinkInput(ApiModel): guardianMembershipId: UUID; athleteId: UUID
class SessionInput(ApiModel):
    branchId: UUID; coachMembershipId: UUID | None = None; title: Annotated[str, Field(min_length=2, max_length=120)]
    startsAt: datetime; endsAt: datetime
    _title = field_validator("title", mode="before")(trim)
class RosterInput(ApiModel): athleteId: UUID
class AttendanceInput(ApiModel):
    status: Annotated[str, Field(pattern="^(PRESENT|ABSENT|EXCUSED)$")]
    correctionReason: Annotated[str | None, Field(max_length=300)] = None
    @field_validator("correctionReason", mode="before")
    @classmethod
    def reason(cls, value): return trim(value) if value else None
class QrInput(ApiModel): kind: Annotated[str, Field(pattern="^(SESSION|STAFF)$")]; branchId: UUID; sessionId: UUID | None = None
class RedeemQrInput(ApiModel): token: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]; athleteId: UUID | None = None
class AthleteDto(BaseModel): id: UUID; name: str; membershipId: UUID | None; active: bool
class SessionDto(BaseModel): id: UUID; branchId: UUID; coachMembershipId: UUID | None; title: str; startsAt: datetime; endsAt: datetime; status: str
class AttendanceDto(BaseModel): id: UUID; sessionId: UUID | None = None; athleteId: UUID | None = None; membershipId: UUID | None = None; branchId: UUID | None = None; localDate: date | None = None; status: str; source: str; checkedAt: datetime
class QrDto(BaseModel): token: str; url: str; expiresAt: datetime
