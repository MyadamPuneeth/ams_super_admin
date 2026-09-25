from datetime import date, datetime, time
from decimal import Decimal
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

class SubscriptionPlan(StrEnum):
    STARTER = "STARTER"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"

class SubscriptionStatus(StrEnum):
    TRIAL = "TRIAL"
    ACTIVE = "ACTIVE"
    PAST_DUE = "PAST_DUE"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

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
    adminName: Annotated[str, Field(min_length=2, max_length=100)]
    adminUsername: Annotated[str, Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9._-]+$")]
    temporaryPassword: Annotated[str, Field(min_length=12, max_length=128)]
    subscriptionPlan: SubscriptionPlan = SubscriptionPlan.STARTER
    subscriptionStatus: SubscriptionStatus = SubscriptionStatus.TRIAL
    subscriptionStartsOn: date = Field(default_factory=date.today)
    subscriptionEndsOn: date | None = None
    _name = field_validator("name", mode="before")(trim)
    _admin_name = field_validator("adminName", mode="before")(trim)
    _email = field_validator("adminEmail", mode="before")(valid_email)
    @field_validator("adminUsername", mode="before")
    @classmethod
    def normalize_admin_username(cls, value: str) -> str: return value.strip().lower()
    @field_validator("subscriptionEndsOn")
    @classmethod
    def valid_subscription_dates(cls, value: date | None, info):
        start = info.data.get("subscriptionStartsOn")
        if value and start and value < start: raise ValueError("Subscription end date cannot be before its start date.")
        return value

class SubscriptionInput(ApiModel):
    plan: SubscriptionPlan
    status: SubscriptionStatus
    startsOn: date
    endsOn: date | None = None
    @field_validator("endsOn")
    @classmethod
    def valid_dates(cls, value: date | None, info):
        start = info.data.get("startsOn")
        if value and start and value < start: raise ValueError("Subscription end date cannot be before its start date.")
        return value

class PlatformSignInInput(ApiModel):
    username: Annotated[str, Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9._-]+$")]
    password: Annotated[str, Field(min_length=12, max_length=128)]
    @field_validator("username", mode="before")
    @classmethod
    def normalize_username(cls, value: str) -> str: return value.strip().lower()

class PasswordSignInInput(PlatformSignInInput): pass
class PasswordChangeInput(ApiModel): newPassword: Annotated[str, Field(min_length=12, max_length=128)]

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

class AcademyDto(BaseModel):
    id: UUID; name: str; slug: str; active: bool; timezone: str; createdAt: datetime
    subscriptionPlan: SubscriptionPlan; subscriptionStatus: SubscriptionStatus
    subscriptionStartsOn: date; subscriptionEndsOn: date | None
class TableDto(BaseModel): id: UUID; name: str
class BranchDto(BaseModel): id: UUID; name: str; city: str; address: str; tables: list[TableDto]
class MemberDto(BaseModel): id: UUID; userId: UUID; name: str; email: str; roles: list[Role]; allBranches: bool; active: bool; branchIds: list[UUID]
class WorkspaceDto(BaseModel): academy: AcademyDto; membership: MemberDto
class MeDto(BaseModel): id: UUID; email: str; name: str; platformOwner: bool; passwordChangeRequired: bool = False; workspaces: list[WorkspaceDto]
class InvitationDto(BaseModel): id: UUID; email: str; roles: list[Role]; allBranches: bool; branchIds: list[UUID]; expiresAt: datetime; acceptedAt: datetime | None; createdAt: datetime
class InvitationCreatedDto(BaseModel): id: UUID; invitationUrl: str
class HandoffDto(BaseModel): id: UUID; academyId: UUID; academyName: str; username: str; email: str; copied: bool; emailSent: bool; emailError: str | None; createdAt: datetime
class HandoffSecretDto(BaseModel): temporaryPassword: str
class AcademyCreatedDto(BaseModel): academy: AcademyDto; handoff: HandoffDto
class AuditDto(BaseModel): id: UUID; action: str; detail: str; createdAt: datetime
class DashboardDto(BaseModel): branches: int; tables: int; members: int | None; invitations: int | None; currentMonthRevenue: Decimal
class DemoProfileDto(BaseModel): id: UUID; name: str; email: str; label: str
class AuthConfigDto(BaseModel): demo: bool; profiles: list[DemoProfileDto]
class TokenDto(BaseModel): accessToken: str
class AcceptDto(BaseModel): academyId: UUID

class AthleteInput(ApiModel):
    name: Annotated[str, Field(min_length=2, max_length=100)]
    membershipId: UUID | None = None
    homeBranchId: UUID | None = None
    monthlyFee: Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)] = Decimal("0")
    _name = field_validator("name", mode="before")(trim)
class AthleteUpdateInput(ApiModel):
    homeBranchId: UUID | None = None
    monthlyFee: Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]
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
class AthleteDto(BaseModel): id: UUID; name: str; membershipId: UUID | None; homeBranchId: UUID | None; monthlyFee: Decimal; active: bool
class SessionDto(BaseModel): id: UUID; branchId: UUID; coachMembershipId: UUID | None; title: str; startsAt: datetime; endsAt: datetime; status: str
class AttendanceDto(BaseModel): id: UUID; sessionId: UUID | None = None; athleteId: UUID | None = None; membershipId: UUID | None = None; branchId: UUID | None = None; localDate: date | None = None; status: str; source: str; checkedAt: datetime
class QrDto(BaseModel): token: str; url: str; expiresAt: datetime

class CoachInput(ApiModel):
    name: Annotated[str, Field(min_length=2, max_length=100)]
    phone: Annotated[str, Field(min_length=5, max_length=30)]
    email: Annotated[str | None, Field(max_length=254)] = None
    notes: Annotated[str | None, Field(max_length=500)] = None
    active: bool = True
    _name = field_validator("name", mode="before")(trim)
    @field_validator("email", mode="before")
    @classmethod
    def coach_email(cls, value): return valid_email(value) if value else None
class CoachDto(CoachInput): id: UUID; createdAt: datetime

class BatchInput(ApiModel):
    name: Annotated[str, Field(min_length=2, max_length=100)]
    branchId: UUID; tableId: UUID
    recurrence: Annotated[str, Field(pattern="^(ONCE|WEEKLY)$")]
    oneOffDate: date | None = None
    weekdays: Annotated[list[int], Field(max_length=7)] = []
    startsOn: date; endsOn: date | None = None
    startTime: time; endTime: time
    coachIds: Annotated[list[UUID], Field(max_length=20)] = []
    athleteIds: Annotated[list[UUID], Field(max_length=500)] = []
    active: bool = True
    _name = field_validator("name", mode="before")(trim)
    @field_validator("weekdays")
    @classmethod
    def valid_weekdays(cls, value):
        if len(set(value)) != len(value) or any(day < 0 or day > 6 for day in value): raise ValueError("Choose unique weekdays.")
        return value
    @field_validator("endTime")
    @classmethod
    def valid_batch_time(cls, value, info):
        if info.data.get("startTime") and value <= info.data["startTime"]: raise ValueError("End time must be after start time.")
        return value
    @field_validator("endsOn")
    @classmethod
    def valid_batch_dates(cls, value, info):
        if value and info.data.get("startsOn") and value < info.data["startsOn"]: raise ValueError("Recurrence end cannot be before its start.")
        return value
class BatchDto(BaseModel):
    id: UUID; academyId: UUID; name: str; branchId: UUID; tableId: UUID; recurrence: str; oneOffDate: date | None
    weekdays: list[int]; startsOn: date; endsOn: date | None; startTime: time; endTime: time; coachIds: list[UUID]; athleteIds: list[UUID]; active: bool

class DailyAttendanceEntry(ApiModel):
    personType: Annotated[str, Field(pattern="^(ATHLETE|COACH)$")]
    personId: UUID
    status: Annotated[str, Field(pattern="^(PRESENT|ABSENT|EXCUSED)$")]
class DailyAttendanceInput(ApiModel): localDate: date; entries: Annotated[list[DailyAttendanceEntry], Field(max_length=1000)]
class DailyAttendanceDto(BaseModel): personType: str; personId: UUID; name: str; status: str | None

Money = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]
class InvoiceGenerateInput(ApiModel): billingMonth: date; dueDate: date
class InvoiceUpdateInput(ApiModel): discount: Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]; dueDate: date; note: Annotated[str | None, Field(max_length=500)] = None; status: Annotated[str | None, Field(pattern="^(DUE|VOID)$")] = None
class InvoiceDto(BaseModel): id: UUID; athleteId: UUID; athleteName: str; branchId: UUID | None; billingMonth: date; amount: Decimal; discount: Decimal; dueDate: date; status: str; paid: Decimal; balance: Decimal; note: str | None
class PaymentInput(ApiModel):
    invoiceId: UUID | None = None; athleteId: UUID | None = None; branchId: UUID | None = None
    kind: Annotated[str, Field(pattern="^(FEE|AD_HOC)$")]; amount: Money; paidOn: date
    method: Annotated[str, Field(pattern="^(CASH|UPI|CARD|BANK_TRANSFER|OTHER)$")]
    reference: Annotated[str | None, Field(max_length=100)] = None; note: Annotated[str | None, Field(max_length=500)] = None
class PaymentDto(PaymentInput): id: UUID; athleteName: str | None; refunded: Decimal; createdAt: datetime
class RefundInput(ApiModel): amount: Money; refundedOn: date; reason: Annotated[str, Field(min_length=2, max_length=500)]
class RefundDto(RefundInput): id: UUID; paymentId: UUID; createdAt: datetime
class ExpenseInput(ApiModel): branchId: UUID | None = None; amount: Money; incurredOn: date; category: Annotated[str, Field(min_length=2, max_length=100)]; vendor: Annotated[str | None, Field(max_length=100)] = None; note: Annotated[str | None, Field(max_length=500)] = None
class ExpenseDto(ExpenseInput): id: UUID; createdAt: datetime
class TrendDto(BaseModel): month: date; revenue: Decimal; expenses: Decimal
class BranchRevenueDto(BaseModel): branchId: UUID | None; branchName: str; revenue: Decimal
class FinanceSummaryDto(BaseModel): collections: Decimal; refunds: Decimal; expenses: Decimal; outstanding: Decimal; net: Decimal; monthlyTrend: list[TrendDto]; branchDistribution: list[BranchRevenueDto]
