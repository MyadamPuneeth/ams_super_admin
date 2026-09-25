"""SQLAlchemy mappings for the existing, migration-owned PostgreSQL schema."""
from sqlalchemy import Boolean, Column, Date, DateTime, MetaData, String, Table
from sqlalchemy.dialects.postgresql import ARRAY, UUID

metadata = MetaData()
academy = Table("Academy", metadata, Column("id", UUID(as_uuid=True), primary_key=True), Column("name", String), Column("slug", String), Column("active", Boolean), Column("timezone", String), Column("subscriptionPlan", String), Column("subscriptionStatus", String), Column("subscriptionStartsOn", Date), Column("subscriptionEndsOn", Date), Column("createdAt", DateTime(timezone=True)))
branch = Table("Branch", metadata, Column("id", UUID(as_uuid=True), primary_key=True), Column("academyId", UUID(as_uuid=True)), Column("name", String), Column("city", String), Column("address", String), Column("createdAt", DateTime(timezone=True)))
table_resource = Table("TableResource", metadata, Column("id", UUID(as_uuid=True), primary_key=True), Column("academyId", UUID(as_uuid=True)), Column("branchId", UUID(as_uuid=True)), Column("name", String))
membership = Table("Membership", metadata, Column("id", UUID(as_uuid=True), primary_key=True), Column("academyId", UUID(as_uuid=True)), Column("userId", UUID(as_uuid=True)), Column("email", String), Column("name", String), Column("roles", ARRAY(String)), Column("allBranches", Boolean), Column("active", Boolean), Column("createdAt", DateTime(timezone=True)))
member_branch = Table("MemberBranch", metadata, Column("academyId", UUID(as_uuid=True)), Column("membershipId", UUID(as_uuid=True)), Column("branchId", UUID(as_uuid=True)))
invitation = Table("Invitation", metadata, Column("id", UUID(as_uuid=True), primary_key=True), Column("academyId", UUID(as_uuid=True)), Column("email", String), Column("roles", ARRAY(String)), Column("allBranches", Boolean), Column("branchIds", ARRAY(UUID(as_uuid=True))), Column("tokenHash", String), Column("expiresAt", DateTime(timezone=True)), Column("acceptedAt", DateTime(timezone=True)), Column("createdAt", DateTime(timezone=True)))
audit = Table("Audit", metadata, Column("id", UUID(as_uuid=True), primary_key=True), Column("academyId", UUID(as_uuid=True)), Column("actorId", UUID(as_uuid=True)), Column("action", String), Column("detail", String), Column("createdAt", DateTime(timezone=True)))
