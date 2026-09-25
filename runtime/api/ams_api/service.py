from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import os
from secrets import token_hex
from uuid import UUID
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import AuthService, Identity
from .database import Database
from .errors import ApiError
from .mail import Mailer
from .schemas import AcademyInput, AthleteInput, AthleteUpdateInput, AttendanceInput, BatchInput, BranchInput, CoachInput, DailyAttendanceInput, ExpenseInput, GuardianLinkInput, InvitationInput, InvoiceGenerateInput, InvoiceUpdateInput, MemberInput, PaymentInput, QrInput, RefundInput, Role, SessionInput, SubscriptionInput

ACADEMY_FIELDS = 'id, name, slug, active, timezone, "subscriptionPlan", "subscriptionStatus", "subscriptionStartsOn", "subscriptionEndsOn", "createdAt"'

def row(result):
    value = result.mappings().first()
    return dict(value) if value else None

def rows(result): return [dict(value) for value in result.mappings().all()]

class AcademyService:
    def __init__(self, db: Database) -> None:
        self.db = db; self.mailer = Mailer(); self.handoff_key = os.getenv("CREDENTIAL_HANDOFF_KEY", "")
        if len(self.handoff_key) < 32: raise RuntimeError("CREDENTIAL_HANDOFF_KEY must contain at least 32 characters.")

    async def owner(self, session: AsyncSession) -> None:
        if not (await session.scalar(text("SELECT app_private.is_platform_owner()"))):
            raise ApiError(403, "Platform owner access is required.")

    async def member(self, session: AsyncSession, actor: Identity, academy_id: UUID, admin=False):
        membership = row(await session.execute(text('SELECT id, "academyId", "userId", email, name, roles, "allBranches", active, "createdAt" FROM "Membership" WHERE "academyId"=:academy AND "userId"=:actor AND active'), {"academy": academy_id, "actor": actor.id}))
        academy = row(await session.execute(text('SELECT id FROM "Academy" WHERE id=:academy AND active'), {"academy": academy_id}))
        if not membership or not academy or (admin and "ADMIN" not in membership["roles"]):
            raise ApiError(403, "You do not have access to this workspace action.")
        return membership

    async def finance_member(self, session: AsyncSession, actor: Identity, academy_id: UUID):
        membership = await self.member(session, actor, academy_id)
        if not set(membership["roles"]) & {"ADMIN", "FINANCE"}: raise ApiError(403, "Finance access is required.")
        return membership

    async def audit(self, session: AsyncSession, actor: Identity, academy_id: UUID, action: str, detail: str) -> None:
        await session.execute(text('INSERT INTO "Audit" (id, "academyId", "actorId", action, detail) VALUES (gen_random_uuid(), :academy, :actor, :action, :detail)'), {"academy": academy_id, "actor": actor.id, "action": action, "detail": detail})

    async def scope(self, session: AsyncSession, academy_id: UUID, input: InvitationInput | MemberInput) -> None:
        if Role.ADMIN in input.roles and not input.allBranches: raise ApiError(400, "Administrators require access to all branches.")
        if input.allBranches and input.branchIds: raise ApiError(400, "Choose all branches or specific branches, not both.")
        if not input.allBranches and not input.branchIds: raise ApiError(400, "Select at least one branch.")
        count = await session.scalar(text('SELECT count(*) FROM "Branch" WHERE "academyId"=:academy AND id = ANY(CAST(:branches AS uuid[]))'), {"academy": academy_id, "branches": [str(value) for value in input.branchIds]})
        if count != len(input.branchIds): raise ApiError(400, "One or more branches are unavailable.")

    async def lock(self, session: AsyncSession, academy_id: UUID) -> None:
        # Serialize invitation and membership administration for one academy.
        await session.execute(text('SELECT id FROM "Academy" WHERE id=:academy FOR UPDATE'), {"academy": academy_id})

    async def invite(self, session: AsyncSession, actor: Identity, academy_id: UUID, input: InvitationInput):
        email = input.email.lower()
        existing = await session.scalar(text('SELECT 1 FROM "Membership" WHERE "academyId"=:academy AND email=:email AND active'), {"academy": academy_id, "email": email})
        if existing: raise ApiError(409, "This person already belongs to the academy.")
        # A new invite supersedes any earlier pending invite for this academy and email.
        await session.execute(text('UPDATE "Invitation" SET "expiresAt"=now() WHERE "academyId"=:academy AND email=:email AND "acceptedAt" IS NULL'), {"academy": academy_id, "email": email})
        token = token_hex(32)
        # Store only a hash. The raw capability goes in a URL fragment, which browsers do not
        # send to the server or include in Referer headers.
        invitation_id = await session.scalar(text('INSERT INTO "Invitation" (id, "academyId", email, roles, "allBranches", "branchIds", "tokenHash", "expiresAt") VALUES (gen_random_uuid(), :academy, :email, CAST(:roles AS "Role"[]), :all_branches, CAST(:branches AS uuid[]), :token_hash, :expires) RETURNING id'), {"academy": academy_id, "email": email, "roles": [role.value for role in input.roles], "all_branches": input.allBranches, "branches": [str(value) for value in input.branchIds], "token_hash": hashlib.sha256(token.encode()).hexdigest(), "expires": datetime.now(timezone.utc) + timedelta(days=7)})
        await self.audit(session, actor, academy_id, "invitation.created", f"Invited {email} as {', '.join(role.value for role in input.roles)}")
        return {"id": invitation_id, "invitationUrl": f"{os.getenv('WEB_ORIGIN', 'http://localhost:5173')}/accept-invitation#{token}"}

    async def me(self, actor: Identity):
        async with self.db.as_actor(actor) as session:
            platform_owner = bool(await session.scalar(text("SELECT app_private.is_platform_owner()")))
            memberships = rows(await session.execute(text('SELECT m.id AS "membershipId", m."userId", m.email, m.name AS "memberName", m.roles, m."allBranches", m.active, a.id, a.name, a.slug, a.active, a.timezone, a."subscriptionPlan", a."subscriptionStatus", a."subscriptionStartsOn", a."subscriptionEndsOn", a."createdAt" FROM "Membership" m JOIN "Academy" a ON a.id=m."academyId" WHERE m."userId"=:actor AND m.active AND a.active ORDER BY m."createdAt"'), {"actor": actor.id}))
            workspaces = []
            for item in memberships:
                branch_ids = [value for value in await session.scalars(text('SELECT "branchId" FROM "MemberBranch" WHERE "membershipId"=:membership'), {"membership": item["membershipId"]})]
                workspaces.append({"academy": {key: item[key] for key in ("id", "name", "slug", "active", "timezone", "subscriptionPlan", "subscriptionStatus", "subscriptionStartsOn", "subscriptionEndsOn", "createdAt")}, "membership": {"id": item["membershipId"], "userId": item["userId"], "name": item["memberName"], "email": item["email"], "roles": item["roles"], "allBranches": item["allBranches"], "active": item["active"], "branchIds": branch_ids}})
            return {"id": actor.id, "email": actor.email, "name": actor.name, "platformOwner": platform_owner, "passwordChangeRequired": actor.password_change_required, "workspaces": workspaces}

    async def academies(self, actor: Identity):
        async with self.db.as_actor(actor) as session:
            await self.owner(session)
            return rows(await session.execute(text(f'SELECT {ACADEMY_FIELDS} FROM "Academy" ORDER BY "createdAt" DESC')))

    async def create_academy(self, actor: Identity, input: AcademyInput):
        async with self.db.as_actor(actor) as session:
            await self.owner(session)
            academy = row(await session.execute(text(f'INSERT INTO "Academy" (id, name, slug, "subscriptionPlan", "subscriptionStatus", "subscriptionStartsOn", "subscriptionEndsOn") VALUES (gen_random_uuid(), :name, :slug, CAST(:plan AS "SubscriptionPlan"), CAST(:status AS "SubscriptionStatus"), :starts, :ends) RETURNING {ACADEMY_FIELDS}'), {"name": input.name, "slug": input.slug, "plan": input.subscriptionPlan.value, "status": input.subscriptionStatus.value, "starts": input.subscriptionStartsOn, "ends": input.subscriptionEndsOn}))
            # Switch to the new tenant so the first membership and audit pass RLS atomically.
            await session.execute(text("SELECT set_config('app.academy', :academy, true)"), {"academy": str(academy["id"])})
            user_id = await session.scalar(text("SELECT gen_random_uuid()"))
            await session.execute(text('INSERT INTO "UserCredential" ("userId",username,"passwordHash",name,email) VALUES (:user,:username,:password,:name,:email)'), {"user": user_id, "username": input.adminUsername, "password": AuthService.hash_password(input.temporaryPassword), "name": input.adminName, "email": input.adminEmail})
            await session.execute(text('INSERT INTO "Membership" (id,"academyId","userId",email,name,roles,"allBranches") VALUES (gen_random_uuid(),:academy,:user,:email,:name,ARRAY[\'ADMIN\']::"Role"[],true)'), {"academy": academy["id"], "user": user_id, "email": input.adminEmail, "name": input.adminName})
            handoff = row(await session.execute(text('INSERT INTO "CredentialHandoff" ("academyId","userId",username,email,"passwordCipher") VALUES (:academy,:user,:username,:email,pgp_sym_encrypt(:password,:key,\'cipher-algo=aes256\')) RETURNING id,"academyId",username,email,false AS copied,false AS "emailSent",NULL::text AS "emailError","createdAt"'), {"academy": academy["id"], "user": user_id, "username": input.adminUsername, "email": input.adminEmail, "password": input.temporaryPassword, "key": self.handoff_key}))
            await self.audit(session, actor, academy["id"], "academy.created", f"Created {academy['name']}")
            await self.audit(session, actor, academy["id"], "academy.admin.created", f"Created administrator {input.adminUsername}")
        handoff["academyName"] = academy["name"]
        handoff = await self.email_handoff(actor, handoff["id"])
        return {"academy": academy, "handoff": handoff}

    async def handoffs(self, actor: Identity):
        async with self.db.as_actor(actor) as session:
            await self.owner(session)
            return rows(await session.execute(text('SELECT h.id,h."academyId",a.name AS "academyName",h.username,h.email,h."copiedAt" IS NOT NULL AS copied,h."emailSentAt" IS NOT NULL AS "emailSent",h."emailError",h."createdAt" FROM "CredentialHandoff" h JOIN "Academy" a ON a.id=h."academyId" WHERE h."passwordCipher" IS NOT NULL ORDER BY h."createdAt" DESC')))

    async def reveal_handoff(self, actor: Identity, handoff_id: UUID):
        async with self.db.as_actor(actor) as session:
            await self.owner(session)
            password = await session.scalar(text('SELECT pgp_sym_decrypt("passwordCipher",:key) FROM "CredentialHandoff" WHERE id=:id AND "passwordCipher" IS NOT NULL'), {"id": handoff_id, "key": self.handoff_key})
            if not password: raise ApiError(404, "These credentials are no longer available.")
            return {"temporaryPassword": password}

    async def mark_handoff_copied(self, actor: Identity, handoff_id: UUID):
        async with self.db.as_actor(actor) as session:
            await self.owner(session)
            updated = await session.scalar(text('UPDATE "CredentialHandoff" SET "copiedAt"=COALESCE("copiedAt",now()),"passwordCipher"=CASE WHEN "emailSentAt" IS NOT NULL THEN NULL ELSE "passwordCipher" END WHERE id=:id AND "passwordCipher" IS NOT NULL RETURNING id'), {"id": handoff_id})
            if not updated: raise ApiError(404, "These credentials are no longer available.")

    async def email_handoff(self, actor: Identity, handoff_id: UUID):
        async with self.db.as_actor(actor) as session:
            await self.owner(session)
            value = row(await session.execute(text('SELECT h.id,h."academyId",a.name AS "academyName",h.username,h.email,pgp_sym_decrypt(h."passwordCipher",:key) AS password FROM "CredentialHandoff" h JOIN "Academy" a ON a.id=h."academyId" WHERE h.id=:id AND h."passwordCipher" IS NOT NULL'), {"id": handoff_id, "key": self.handoff_key}))
        if not value: raise ApiError(404, "These credentials are no longer available.")
        error = None
        try: await self.mailer.send_credentials(value["email"], value["academyName"], value["username"], value["password"])
        except Exception as exception: error = str(exception)[:300]
        async with self.db.as_actor(actor) as session:
            await self.owner(session)
            await session.execute(text('UPDATE "CredentialHandoff" SET "emailSentAt"=CASE WHEN :sent THEN now() ELSE "emailSentAt" END,"emailError"=:error,"passwordCipher"=CASE WHEN :sent AND "copiedAt" IS NOT NULL THEN NULL ELSE "passwordCipher" END WHERE id=:id'), {"id": handoff_id, "sent": error is None, "error": error})
            result = row(await session.execute(text('SELECT h.id,h."academyId",a.name AS "academyName",h.username,h.email,h."copiedAt" IS NOT NULL AS copied,h."emailSentAt" IS NOT NULL AS "emailSent",h."emailError",h."createdAt" FROM "CredentialHandoff" h JOIN "Academy" a ON a.id=h."academyId" WHERE h.id=:id'), {"id": handoff_id}))
            return result

    async def set_active(self, actor: Identity, academy_id: UUID, active: bool):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.owner(session)
            academy = row(await session.execute(text(f'UPDATE "Academy" SET active=:active WHERE id=:academy RETURNING {ACADEMY_FIELDS}'), {"academy": academy_id, "active": active}))
            if not academy: raise ApiError(404, "The record is unavailable.")
            await self.audit(session, actor, academy_id, "academy.activated" if active else "academy.suspended", academy["name"])
            return academy

    async def set_subscription(self, actor: Identity, academy_id: UUID, input: SubscriptionInput):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.owner(session)
            academy = row(await session.execute(text(f'UPDATE "Academy" SET "subscriptionPlan"=CAST(:plan AS "SubscriptionPlan"), "subscriptionStatus"=CAST(:status AS "SubscriptionStatus"), "subscriptionStartsOn"=:starts, "subscriptionEndsOn"=:ends WHERE id=:academy RETURNING {ACADEMY_FIELDS}'), {"academy": academy_id, "plan": input.plan.value, "status": input.status.value, "starts": input.startsOn, "ends": input.endsOn}))
            if not academy: raise ApiError(404, "The record is unavailable.")
            await self.audit(session, actor, academy_id, "academy.subscription.updated", f"Set {input.plan.value} subscription to {input.status.value}")
            return academy

    async def branches(self, actor: Identity, academy_id: UUID):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id)
            result = []
            for branch in rows(await session.execute(text('SELECT id, name, city, address FROM "Branch" WHERE "academyId"=:academy ORDER BY "createdAt"'), {"academy": academy_id})):
                branch["tables"] = rows(await session.execute(text('SELECT id, name FROM "TableResource" WHERE "academyId"=:academy AND "branchId"=:branch ORDER BY name'), {"academy": academy_id, "branch": branch["id"]}))
                result.append(branch)
            return result

    async def create_branch(self, actor: Identity, academy_id: UUID, input: BranchInput):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id, True)
            branch = row(await session.execute(text('INSERT INTO "Branch" (id, "academyId", name, city, address) VALUES (gen_random_uuid(), :academy, :name, :city, :address) RETURNING id, name, city, address'), {"academy": academy_id, "name": input.name, "city": input.city, "address": input.address}))
            await self.audit(session, actor, academy_id, "branch.created", f"Added {branch['name']}")
            return {**branch, "tables": []}

    async def create_table(self, actor: Identity, academy_id: UUID, branch_id: UUID, name: str):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id, True)
            if not await session.scalar(text('SELECT 1 FROM "Branch" WHERE id=:branch AND "academyId"=:academy'), {"branch": branch_id, "academy": academy_id}): raise ApiError(404, "Branch not found.")
            table = row(await session.execute(text('INSERT INTO "TableResource" (id, "academyId", "branchId", name) VALUES (gen_random_uuid(), :academy, :branch, :name) RETURNING id, name'), {"academy": academy_id, "branch": branch_id, "name": name}))
            await self.audit(session, actor, academy_id, "table.created", f"Added {table['name']}")
            return table

    async def update_branch(self, actor: Identity, academy_id: UUID, branch_id: UUID, input: BranchInput):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id, True)
            value = row(await session.execute(text('UPDATE "Branch" SET name=:name,city=:city,address=:address WHERE id=:id AND "academyId"=:academy RETURNING id,name,city,address'), {"academy": academy_id, "id": branch_id, **input.model_dump()}))
            if not value: raise ApiError(404, "Branch not found.")
            value["tables"] = rows(await session.execute(text('SELECT id,name FROM "TableResource" WHERE "branchId"=:id ORDER BY name'), {"id": branch_id}))
            await self.audit(session, actor, academy_id, "branch.updated", f"Updated {input.name}")
            return value

    async def delete_branch(self, actor: Identity, academy_id: UUID, branch_id: UUID):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id, True)
            if not await session.scalar(text('DELETE FROM "Branch" WHERE id=:id AND "academyId"=:academy RETURNING id'), {"id": branch_id, "academy": academy_id}): raise ApiError(404, "Branch not found.")
            await self.audit(session, actor, academy_id, "branch.deleted", f"Deleted branch {branch_id}")

    async def update_table(self, actor: Identity, academy_id: UUID, branch_id: UUID, table_id: UUID, name: str):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id, True)
            value = row(await session.execute(text('UPDATE "TableResource" SET name=:name WHERE id=:id AND "branchId"=:branch AND "academyId"=:academy RETURNING id,name'), {"academy": academy_id, "branch": branch_id, "id": table_id, "name": name}))
            if not value: raise ApiError(404, "Table not found.")
            await self.audit(session, actor, academy_id, "table.updated", f"Updated table {name}")
            return value

    async def delete_table(self, actor: Identity, academy_id: UUID, branch_id: UUID, table_id: UUID):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id, True)
            if not await session.scalar(text('DELETE FROM "TableResource" WHERE id=:id AND "branchId"=:branch AND "academyId"=:academy RETURNING id'), {"academy": academy_id, "branch": branch_id, "id": table_id}): raise ApiError(404, "Table not found.")
            await self.audit(session, actor, academy_id, "table.deleted", f"Deleted table {table_id}")

    async def members(self, actor: Identity, academy_id: UUID):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id, True)
            result = []
            for member in rows(await session.execute(text('SELECT id, "userId", name, email, roles, "allBranches", active FROM "Membership" WHERE "academyId"=:academy ORDER BY "createdAt"'), {"academy": academy_id})):
                member["branchIds"] = [value for value in await session.scalars(text('SELECT "branchId" FROM "MemberBranch" WHERE "membershipId"=:member'), {"member": member["id"]})]
                result.append(member)
            return result

    async def update_member(self, actor: Identity, academy_id: UUID, member_id: UUID, input: MemberInput):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.lock(session, academy_id); await self.member(session, actor, academy_id, True); await self.scope(session, academy_id, input)
            existing = row(await session.execute(text('SELECT id, email, roles, active FROM "Membership" WHERE id=:member AND "academyId"=:academy'), {"member": member_id, "academy": academy_id}))
            if not existing: raise ApiError(404, "The record is unavailable.")
            if existing["active"] and "ADMIN" in existing["roles"] and (not input.active or Role.ADMIN not in input.roles):
                count = await session.scalar(text('SELECT count(*) FROM "Membership" WHERE "academyId"=:academy AND active AND \'ADMIN\'=ANY(roles)'), {"academy": academy_id})
                if count <= 1: raise ApiError(409, "Keep at least one active academy administrator.")
            # Replace branch assignments atomically with the role change.
            await session.execute(text('DELETE FROM "MemberBranch" WHERE "academyId"=:academy AND "membershipId"=:member'), {"academy": academy_id, "member": member_id})
            for branch_id in input.branchIds:
                await session.execute(text('INSERT INTO "MemberBranch" ("academyId", "membershipId", "branchId") VALUES (:academy, :member, :branch)'), {"academy": academy_id, "member": member_id, "branch": branch_id})
            updated = row(await session.execute(text('UPDATE "Membership" SET roles=CAST(:roles AS "Role"[]), "allBranches"=:all_branches, active=:active WHERE id=:member RETURNING id, "userId", name, email, roles, "allBranches", active'), {"member": member_id, "roles": [role.value for role in input.roles], "all_branches": input.allBranches, "active": input.active}))
            updated["branchIds"] = list(input.branchIds)
            await self.audit(session, actor, academy_id, "membership.updated", f"Updated access for {existing['email']}")
            return updated

    async def invitations(self, actor: Identity, academy_id: UUID):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id, True)
            return rows(await session.execute(text('SELECT id, email, roles, "allBranches", "branchIds", "expiresAt", "acceptedAt", "createdAt" FROM "Invitation" WHERE "academyId"=:academy ORDER BY "createdAt" DESC'), {"academy": academy_id}))

    async def create_invitation(self, actor: Identity, academy_id: UUID, input: InvitationInput):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.lock(session, academy_id); await self.member(session, actor, academy_id, True); await self.scope(session, academy_id, input)
            return await self.invite(session, actor, academy_id, input)

    async def revoke(self, actor: Identity, academy_id: UUID, invitation_id: UUID):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id, True)
            invite = row(await session.execute(text('SELECT id, email FROM "Invitation" WHERE id=:id AND "academyId"=:academy AND "acceptedAt" IS NULL'), {"id": invitation_id, "academy": academy_id}))
            if not invite: raise ApiError(404, "The record is unavailable.")
            await session.execute(text('UPDATE "Invitation" SET "expiresAt"=now() WHERE id=:id'), {"id": invitation_id})
            await self.audit(session, actor, academy_id, "invitation.revoked", f"Revoked invitation for {invite['email']}")

    async def accept(self, actor: Identity, token: str):
        try:
            async with self.db.as_actor(actor) as session:
                # The SECURITY DEFINER function locks the invite and consumes it exactly once.
                academy_id = await session.scalar(text('SELECT app_private.accept_invitation(:hash, :name)'), {"hash": hashlib.sha256(token.encode()).hexdigest(), "name": actor.name})
                if not academy_id: raise ApiError(400, "Invitation unavailable.")
                return {"academyId": academy_id}
        except DBAPIError:
            raise ApiError(409, "Invitation unavailable for this account.")

    async def dashboard(self, actor: Identity, academy_id: UUID):
        async with self.db.as_actor(actor, academy_id) as session:
            member = await self.member(session, actor, academy_id)
            admin = "ADMIN" in member["roles"]
            revenue = await session.scalar(text('SELECT COALESCE((SELECT sum(amount) FROM "Payment" WHERE "academyId"=:academy AND "paidOn">=date_trunc(\'month\',current_date)::date),0)-COALESCE((SELECT sum(r.amount) FROM "Refund" r JOIN "Payment" p ON p.id=r."paymentId" WHERE r."academyId"=:academy AND r."refundedOn">=date_trunc(\'month\',current_date)::date),0)'), {"academy": academy_id}) if admin else Decimal("0")
            return {"branches": await session.scalar(text('SELECT count(*) FROM "Branch" WHERE "academyId"=:academy'), {"academy": academy_id}), "tables": await session.scalar(text('SELECT count(*) FROM "TableResource" WHERE "academyId"=:academy'), {"academy": academy_id}), "members": await session.scalar(text('SELECT count(*) FROM "Membership" WHERE "academyId"=:academy AND active'), {"academy": academy_id}) if admin else None, "invitations": await session.scalar(text('SELECT count(*) FROM "Invitation" WHERE "academyId"=:academy AND "acceptedAt" IS NULL AND "expiresAt">now()'), {"academy": academy_id}) if admin else None, "currentMonthRevenue": revenue}

    async def activity(self, actor: Identity, academy_id: UUID):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id, True)
            return rows(await session.execute(text('SELECT id, action, detail, "createdAt" FROM "Audit" WHERE "academyId"=:academy ORDER BY "createdAt" DESC LIMIT 50'), {"academy": academy_id}))

    async def athletes(self, actor: Identity, academy_id: UUID):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id)
            return rows(await session.execute(text('SELECT id, name, "membershipId", "homeBranchId", "monthlyFee", active FROM "Athlete" WHERE "academyId"=:academy AND active ORDER BY name'), {"academy": academy_id}))

    async def create_athlete(self, actor: Identity, academy_id: UUID, input: AthleteInput):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id, True)
            value = row(await session.execute(text('INSERT INTO "Athlete" ("academyId", name, "membershipId", "homeBranchId", "monthlyFee") VALUES (:academy, :name, :membership, :branch, :fee) RETURNING id, name, "membershipId", "homeBranchId", "monthlyFee", active'), {"academy": academy_id, "name": input.name, "membership": input.membershipId, "branch": input.homeBranchId, "fee": input.monthlyFee}))
            await self.audit(session, actor, academy_id, "athlete.created", f"Added {value['name']}")
            return value

    async def update_athlete(self, actor: Identity, academy_id: UUID, athlete_id: UUID, input: AthleteUpdateInput):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id, True)
            value = row(await session.execute(text('UPDATE "Athlete" SET "homeBranchId"=:branch,"monthlyFee"=:fee WHERE id=:id AND "academyId"=:academy RETURNING id,name,"membershipId","homeBranchId","monthlyFee",active'), {"academy": academy_id, "id": athlete_id, "branch": input.homeBranchId, "fee": input.monthlyFee}))
            if not value: raise ApiError(404, "Athlete not found.")
            await self.audit(session, actor, academy_id, "athlete.fees.updated", f"Updated fees for {value['name']}")
            return value

    async def coaches(self, actor: Identity, academy_id: UUID):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id)
            return rows(await session.execute(text('SELECT id,name,phone,email,notes,active,"createdAt" FROM "Coach" WHERE "academyId"=:academy ORDER BY name'), {"academy": academy_id}))

    async def create_coach(self, actor: Identity, academy_id: UUID, input: CoachInput):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id, True)
            value = row(await session.execute(text('INSERT INTO "Coach"("academyId",name,phone,email,notes,active) VALUES(:academy,:name,:phone,:email,:notes,:active) RETURNING id,name,phone,email,notes,active,"createdAt"'), {"academy": academy_id, **input.model_dump()}))
            await self.audit(session, actor, academy_id, "coach.created", f"Added coach {input.name}")
            return value

    async def update_coach(self, actor: Identity, academy_id: UUID, coach_id: UUID, input: CoachInput):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id, True)
            value = row(await session.execute(text('UPDATE "Coach" SET name=:name,phone=:phone,email=:email,notes=:notes,active=:active WHERE id=:id AND "academyId"=:academy RETURNING id,name,phone,email,notes,active,"createdAt"'), {"academy": academy_id, "id": coach_id, **input.model_dump()}))
            if not value: raise ApiError(404, "Coach not found.")
            await self.audit(session, actor, academy_id, "coach.updated", f"Updated coach {input.name}")
            return value

    @staticmethod
    def schedules_overlap(left, right) -> bool:
        if left["startTime"] >= right["endTime"] or left["endTime"] <= right["startTime"]: return False
        if left["recurrence"] == "ONCE" and right["recurrence"] == "ONCE": return left["oneOffDate"] == right["oneOffDate"]
        def occurs(once, weekly): return weekly["startsOn"] <= once["oneOffDate"] <= (weekly["endsOn"] or date.max) and once["oneOffDate"].weekday() in weekly["weekdays"]
        if left["recurrence"] == "ONCE": return occurs(left, right)
        if right["recurrence"] == "ONCE": return occurs(right, left)
        start = max(left["startsOn"], right["startsOn"]); end = min(left["endsOn"] or date.max, right["endsOn"] or date.max)
        return start <= end and any(start + timedelta(days=(day-start.weekday()) % 7) <= end for day in set(left["weekdays"]) & set(right["weekdays"]))

    async def batch_values(self, session: AsyncSession, academy_id: UUID):
        values = rows(await session.execute(text('SELECT id,"academyId",name,"branchId","tableId",recurrence,"oneOffDate",weekdays,"startsOn","endsOn","startTime","endTime",active FROM "Batch" WHERE "academyId"=:academy ORDER BY "startTime",name'), {"academy": academy_id}))
        for value in values:
            value["coachIds"] = list(await session.scalars(text('SELECT "coachId" FROM "BatchCoach" WHERE "batchId"=:id'), {"id": value["id"]}))
            value["athleteIds"] = list(await session.scalars(text('SELECT "athleteId" FROM "BatchAthlete" WHERE "batchId"=:id'), {"id": value["id"]}))
        return values

    async def batches(self, actor: Identity, academy_id: UUID):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id)
            return await self.batch_values(session, academy_id)

    async def save_batch(self, actor: Identity, academy_id: UUID, input: BatchInput, batch_id: UUID | None = None):
        if input.recurrence == "ONCE" and not input.oneOffDate or input.recurrence == "WEEKLY" and (input.oneOffDate or not input.weekdays): raise ApiError(400, "Choose a valid batch recurrence.")
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id, True)
            if not await session.scalar(text('SELECT 1 FROM "TableResource" WHERE id=:table AND "branchId"=:branch AND "academyId"=:academy'), {"table": input.tableId, "branch": input.branchId, "academy": academy_id}): raise ApiError(400, "Choose a table from the selected branch.")
            if len(set(input.coachIds)) != len(input.coachIds) or len(set(input.athleteIds)) != len(input.athleteIds): raise ApiError(400, "Assignments must be unique.")
            if await session.scalar(text('SELECT count(*) FROM "Coach" WHERE "academyId"=:academy AND active AND id=ANY(CAST(:ids AS uuid[]))'), {"academy": academy_id, "ids": [str(x) for x in input.coachIds]}) != len(input.coachIds): raise ApiError(400, "One or more coaches are unavailable.")
            if await session.scalar(text('SELECT count(*) FROM "Athlete" WHERE "academyId"=:academy AND active AND id=ANY(CAST(:ids AS uuid[]))'), {"academy": academy_id, "ids": [str(x) for x in input.athleteIds]}) != len(input.athleteIds): raise ApiError(400, "One or more athletes are unavailable.")
            proposed = input.model_dump()
            for existing in await self.batch_values(session, academy_id):
                if existing["id"] == batch_id or not existing["active"] or not input.active: continue
                resources = existing["tableId"] == input.tableId or set(existing["coachIds"]) & set(input.coachIds) or set(existing["athleteIds"]) & set(input.athleteIds)
                if resources and self.schedules_overlap(proposed, existing): raise ApiError(409, f"{existing['name']} already uses the selected table, coach, or athlete at that time.")
            params = {"academy": academy_id, "id": batch_id, **proposed}
            if batch_id:
                value = row(await session.execute(text('UPDATE "Batch" SET name=:name,"branchId"=:branchId,"tableId"=:tableId,recurrence=CAST(:recurrence AS "BatchRecurrence"),"oneOffDate"=:oneOffDate,weekdays=:weekdays,"startsOn"=:startsOn,"endsOn"=:endsOn,"startTime"=:startTime,"endTime"=:endTime,active=:active WHERE id=:id AND "academyId"=:academy RETURNING id'), params))
                if not value: raise ApiError(404, "Batch not found.")
                await session.execute(text('DELETE FROM "BatchCoach" WHERE "batchId"=:id'), {"id": batch_id})
                await session.execute(text('DELETE FROM "BatchAthlete" WHERE "batchId"=:id'), {"id": batch_id})
            else: batch_id = await session.scalar(text('INSERT INTO "Batch"("academyId",name,"branchId","tableId",recurrence,"oneOffDate",weekdays,"startsOn","endsOn","startTime","endTime",active) VALUES(:academy,:name,:branchId,:tableId,CAST(:recurrence AS "BatchRecurrence"),:oneOffDate,:weekdays,:startsOn,:endsOn,:startTime,:endTime,:active) RETURNING id'), params)
            for coach_id in input.coachIds: await session.execute(text('INSERT INTO "BatchCoach"("academyId","batchId","coachId") VALUES(:academy,:batch,:person)'), {"academy": academy_id, "batch": batch_id, "person": coach_id})
            for athlete_id in input.athleteIds: await session.execute(text('INSERT INTO "BatchAthlete"("academyId","batchId","athleteId") VALUES(:academy,:batch,:person)'), {"academy": academy_id, "batch": batch_id, "person": athlete_id})
            await self.audit(session, actor, academy_id, "batch.saved", f"Saved batch {input.name}")
            return next(item for item in await self.batch_values(session, academy_id) if item["id"] == batch_id)

    async def delete_batch(self, actor: Identity, academy_id: UUID, batch_id: UUID):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id, True)
            name = await session.scalar(text('DELETE FROM "Batch" WHERE id=:id AND "academyId"=:academy RETURNING name'), {"id": batch_id, "academy": academy_id})
            if not name: raise ApiError(404, "Batch not found.")
            await self.audit(session, actor, academy_id, "batch.deleted", f"Deleted batch {name}")

    async def daily_attendance(self, actor: Identity, academy_id: UUID, local_date: date):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id, True)
            athletes = rows(await session.execute(text('SELECT \'ATHLETE\' AS "personType",a.id AS "personId",a.name,d.status FROM "Athlete" a LEFT JOIN "AthleteDailyAttendance" d ON d."athleteId"=a.id AND d."localDate"=:date WHERE a."academyId"=:academy AND a.active'), {"academy": academy_id, "date": local_date}))
            coaches = rows(await session.execute(text('SELECT \'COACH\' AS "personType",c.id AS "personId",c.name,d.status FROM "Coach" c LEFT JOIN "CoachAttendance" d ON d."coachId"=c.id AND d."localDate"=:date WHERE c."academyId"=:academy AND c.active'), {"academy": academy_id, "date": local_date}))
            return sorted(athletes + coaches, key=lambda item: (item["personType"], item["name"]))

    async def save_daily_attendance(self, actor: Identity, academy_id: UUID, input: DailyAttendanceInput):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id, True)
            for entry in input.entries:
                table, column = ("AthleteDailyAttendance", "athleteId") if entry.personType == "ATHLETE" else ("CoachAttendance", "coachId")
                await session.execute(text(f'INSERT INTO "{table}"("academyId","{column}","localDate",status,"actorId") VALUES(:academy,:person,:date,CAST(:status AS "AttendanceStatus"),:actor) ON CONFLICT ("academyId","{column}","localDate") DO UPDATE SET status=EXCLUDED.status,"actorId"=EXCLUDED."actorId","updatedAt"=now()'), {"academy": academy_id, "person": entry.personId, "date": input.localDate, "status": entry.status, "actor": actor.id})
            await self.audit(session, actor, academy_id, "attendance.daily.saved", f"Saved {len(input.entries)} attendance records for {input.localDate}")

    async def refresh_invoice(self, session: AsyncSession, invoice_id: UUID | None):
        if not invoice_id: return
        await session.execute(text('''UPDATE "Invoice" i SET status=CASE WHEN i.status='VOID' THEN 'VOID'::"InvoiceStatus" WHEN x.net>=i.amount-i.discount THEN 'PAID'::"InvoiceStatus" WHEN x.net>0 THEN 'PARTIAL'::"InvoiceStatus" WHEN i."dueDate"<current_date THEN 'OVERDUE'::"InvoiceStatus" ELSE 'DUE'::"InvoiceStatus" END FROM (SELECT COALESCE(sum(p.amount),0)-COALESCE(sum(r.amount),0) net FROM "Payment" p LEFT JOIN (SELECT "paymentId",sum(amount) amount FROM "Refund" GROUP BY "paymentId") r ON r."paymentId"=p.id WHERE p."invoiceId"=:id) x WHERE i.id=:id'''), {"id": invoice_id})

    async def invoice_values(self, session: AsyncSession, academy_id: UUID, month: date | None = None):
        await session.execute(text('''UPDATE "Invoice" i SET status=CASE WHEN i.status='VOID' THEN 'VOID'::"InvoiceStatus" WHEN COALESCE(x.net,0)>=i.amount-i.discount THEN 'PAID'::"InvoiceStatus" WHEN COALESCE(x.net,0)>0 THEN 'PARTIAL'::"InvoiceStatus" WHEN i."dueDate"<current_date THEN 'OVERDUE'::"InvoiceStatus" ELSE 'DUE'::"InvoiceStatus" END FROM (SELECT p."invoiceId",sum(p.amount)-sum(COALESCE(r.amount,0)) net FROM "Payment" p LEFT JOIN (SELECT "paymentId",sum(amount) amount FROM "Refund" GROUP BY "paymentId") r ON r."paymentId"=p.id GROUP BY p."invoiceId") x WHERE i."academyId"=:academy AND x."invoiceId"=i.id'''), {"academy": academy_id})
        await session.execute(text('''UPDATE "Invoice" SET status=CASE WHEN "dueDate"<current_date THEN 'OVERDUE'::"InvoiceStatus" ELSE 'DUE'::"InvoiceStatus" END WHERE "academyId"=:academy AND status NOT IN ('VOID','PAID','PARTIAL') AND NOT EXISTS (SELECT 1 FROM "Payment" WHERE "invoiceId"="Invoice".id)'''), {"academy": academy_id})
        condition = 'AND i."billingMonth"=:month' if month else ''
        return rows(await session.execute(text(f'''SELECT i.id,i."athleteId",a.name AS "athleteName",i."branchId",i."billingMonth",i.amount,i.discount,i."dueDate",i.status,i.note,COALESCE(x.paid,0)-COALESCE(x.refunded,0) paid,GREATEST(i.amount-i.discount-(COALESCE(x.paid,0)-COALESCE(x.refunded,0)),0) balance FROM "Invoice" i JOIN "Athlete" a ON a.id=i."athleteId" LEFT JOIN (SELECT p."invoiceId",sum(p.amount) paid,sum(COALESCE(r.amount,0)) refunded FROM "Payment" p LEFT JOIN (SELECT "paymentId",sum(amount) amount FROM "Refund" GROUP BY "paymentId") r ON r."paymentId"=p.id GROUP BY p."invoiceId") x ON x."invoiceId"=i.id WHERE i."academyId"=:academy {condition} ORDER BY i."billingMonth" DESC,a.name'''), {"academy": academy_id, "month": month}))

    async def invoices(self, actor: Identity, academy_id: UUID, month: date | None):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.finance_member(session, actor, academy_id)
            return await self.invoice_values(session, academy_id, month)

    async def generate_invoices(self, actor: Identity, academy_id: UUID, input: InvoiceGenerateInput):
        month = input.billingMonth.replace(day=1)
        async with self.db.as_actor(actor, academy_id) as session:
            await self.finance_member(session, actor, academy_id)
            await session.execute(text('''INSERT INTO "Invoice"("academyId","athleteId","branchId","billingMonth",amount,"dueDate") SELECT :academy,id,"homeBranchId",:month,"monthlyFee",:due FROM "Athlete" WHERE "academyId"=:academy AND active AND "monthlyFee">0 ON CONFLICT ("academyId","athleteId","billingMonth") DO NOTHING'''), {"academy": academy_id, "month": month, "due": input.dueDate})
            await self.audit(session, actor, academy_id, "invoice.month.generated", f"Generated invoices for {month}")
            return await self.invoice_values(session, academy_id, month)

    async def update_invoice(self, actor: Identity, academy_id: UUID, invoice_id: UUID, input: InvoiceUpdateInput):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.finance_member(session, actor, academy_id)
            amount = await session.scalar(text('SELECT amount FROM "Invoice" WHERE id=:id AND "academyId"=:academy'), {"id": invoice_id, "academy": academy_id})
            if amount is None: raise ApiError(404, "Invoice not found.")
            if input.discount > amount: raise ApiError(400, "Discount cannot exceed the invoice amount.")
            await session.execute(text('UPDATE "Invoice" SET discount=:discount,"dueDate"=:due,note=:note,status=CASE WHEN :status=\'VOID\' THEN \'VOID\'::"InvoiceStatus" ELSE status END WHERE id=:id'), {"id": invoice_id, "discount": input.discount, "due": input.dueDate, "note": input.note, "status": input.status})
            if input.status != "VOID": await self.refresh_invoice(session, invoice_id)
            await self.audit(session, actor, academy_id, "invoice.updated", f"Updated invoice {invoice_id}")
            return next(item for item in await self.invoice_values(session, academy_id) if item["id"] == invoice_id)

    async def payments(self, actor: Identity, academy_id: UUID):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.finance_member(session, actor, academy_id)
            return rows(await session.execute(text('''SELECT p.id,p."invoiceId",p."athleteId",p."branchId",p.kind,p.amount,p."paidOn",p.method,p.reference,p.note,p."createdAt",a.name AS "athleteName",COALESCE(sum(r.amount),0) refunded FROM "Payment" p LEFT JOIN "Athlete" a ON a.id=p."athleteId" LEFT JOIN "Refund" r ON r."paymentId"=p.id WHERE p."academyId"=:academy GROUP BY p.id,a.name ORDER BY p."paidOn" DESC,p."createdAt" DESC'''), {"academy": academy_id}))

    async def validate_payment(self, session: AsyncSession, academy_id: UUID, input: PaymentInput, payment_id: UUID | None = None):
        if input.kind == "FEE":
            invoice = row(await session.execute(text('SELECT "athleteId","branchId",amount-discount due,status FROM "Invoice" WHERE id=:id AND "academyId"=:academy'), {"id": input.invoiceId, "academy": academy_id}))
            if not invoice or invoice["status"] == "VOID": raise ApiError(400, "Choose an active invoice.")
            omit = ' AND id<>:payment' if payment_id else ''
            paid = await session.scalar(text(f'SELECT COALESCE(sum(amount),0) FROM "Payment" WHERE "invoiceId"=:invoice{omit}'), {"invoice": input.invoiceId, "payment": payment_id})
            refund_omit = ' AND p.id<>:payment' if payment_id else ''
            refunded = await session.scalar(text(f'SELECT COALESCE(sum(r.amount),0) FROM "Refund" r JOIN "Payment" p ON p.id=r."paymentId" WHERE p."invoiceId"=:invoice{refund_omit}'), {"invoice": input.invoiceId, "payment": payment_id})
            if paid - refunded + input.amount > invoice["due"]: raise ApiError(400, "Payment exceeds the invoice balance.")
            return invoice["athleteId"], invoice["branchId"]
        if input.invoiceId: raise ApiError(400, "Ad-hoc income cannot reference an invoice.")
        return input.athleteId, input.branchId

    async def save_payment(self, actor: Identity, academy_id: UUID, input: PaymentInput, payment_id: UUID | None = None):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.finance_member(session, actor, academy_id)
            old_invoice = await session.scalar(text('SELECT "invoiceId" FROM "Payment" WHERE id=:id AND "academyId"=:academy'), {"id": payment_id, "academy": academy_id}) if payment_id else None
            athlete_id, branch_id = await self.validate_payment(session, academy_id, input, payment_id)
            params = {"academy": academy_id, "id": payment_id, "athlete": athlete_id, "branch": branch_id, **input.model_dump()}
            if payment_id:
                refunded = await session.scalar(text('SELECT COALESCE(sum(amount),0) FROM "Refund" WHERE "paymentId"=:id'), {"id": payment_id})
                if input.amount < refunded: raise ApiError(400, "Payment amount cannot be less than its refunds.")
                value = row(await session.execute(text('UPDATE "Payment" SET "invoiceId"=:invoiceId,"athleteId"=:athlete,"branchId"=:branch,kind=CAST(:kind AS "PaymentKind"),amount=:amount,"paidOn"=:paidOn,method=CAST(:method AS "PaymentMethod"),reference=:reference,note=:note WHERE id=:id AND "academyId"=:academy RETURNING id'), params))
                if not value: raise ApiError(404, "Payment not found.")
            else: payment_id = await session.scalar(text('INSERT INTO "Payment"("academyId","invoiceId","athleteId","branchId",kind,amount,"paidOn",method,reference,note) VALUES(:academy,:invoiceId,:athlete,:branch,CAST(:kind AS "PaymentKind"),:amount,:paidOn,CAST(:method AS "PaymentMethod"),:reference,:note) RETURNING id'), params)
            await self.refresh_invoice(session, old_invoice); await self.refresh_invoice(session, input.invoiceId)
            await self.audit(session, actor, academy_id, "payment.saved", f"Saved payment {payment_id}")
            return next(item for item in await self._payment_values(session, academy_id) if item["id"] == payment_id)

    async def _payment_values(self, session: AsyncSession, academy_id: UUID):
        return rows(await session.execute(text('''SELECT p.id,p."invoiceId",p."athleteId",p."branchId",p.kind,p.amount,p."paidOn",p.method,p.reference,p.note,p."createdAt",a.name AS "athleteName",COALESCE(sum(r.amount),0) refunded FROM "Payment" p LEFT JOIN "Athlete" a ON a.id=p."athleteId" LEFT JOIN "Refund" r ON r."paymentId"=p.id WHERE p."academyId"=:academy GROUP BY p.id,a.name ORDER BY p."paidOn" DESC,p."createdAt" DESC'''), {"academy": academy_id}))

    async def delete_payment(self, actor: Identity, academy_id: UUID, payment_id: UUID):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.finance_member(session, actor, academy_id)
            found = row(await session.execute(text('SELECT id,"invoiceId" FROM "Payment" WHERE id=:id AND "academyId"=:academy'), {"id": payment_id, "academy": academy_id}))
            if not found: raise ApiError(404, "Payment not found.")
            invoice_id = found["invoiceId"]
            await session.execute(text('DELETE FROM "Payment" WHERE id=:id'), {"id": payment_id})
            await self.refresh_invoice(session, invoice_id); await self.audit(session, actor, academy_id, "payment.deleted", f"Deleted payment {payment_id}")

    async def create_refund(self, actor: Identity, academy_id: UUID, payment_id: UUID, input: RefundInput):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.finance_member(session, actor, academy_id)
            payment = row(await session.execute(text('SELECT amount,"invoiceId" FROM "Payment" WHERE id=:id AND "academyId"=:academy'), {"id": payment_id, "academy": academy_id}))
            if not payment: raise ApiError(404, "Payment not found.")
            refunded = await session.scalar(text('SELECT COALESCE(sum(amount),0) FROM "Refund" WHERE "paymentId"=:id'), {"id": payment_id})
            if refunded + input.amount > payment["amount"]: raise ApiError(400, "Refund exceeds the remaining payment amount.")
            value = row(await session.execute(text('INSERT INTO "Refund"("academyId","paymentId",amount,"refundedOn",reason) VALUES(:academy,:payment,:amount,:date,:reason) RETURNING id,"paymentId",amount,"refundedOn",reason,"createdAt"'), {"academy": academy_id, "payment": payment_id, "amount": input.amount, "date": input.refundedOn, "reason": input.reason}))
            await self.refresh_invoice(session, payment["invoiceId"]); await self.audit(session, actor, academy_id, "refund.created", f"Refunded payment {payment_id}")
            return value

    async def refunds(self, actor: Identity, academy_id: UUID):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.finance_member(session, actor, academy_id)
            return rows(await session.execute(text('SELECT id,"paymentId",amount,"refundedOn",reason,"createdAt" FROM "Refund" WHERE "academyId"=:academy ORDER BY "refundedOn" DESC,"createdAt" DESC'), {"academy": academy_id}))

    async def expenses(self, actor: Identity, academy_id: UUID):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.finance_member(session, actor, academy_id)
            return rows(await session.execute(text('SELECT id,"branchId",amount,"incurredOn",category,vendor,note,"createdAt" FROM "Expense" WHERE "academyId"=:academy ORDER BY "incurredOn" DESC,"createdAt" DESC'), {"academy": academy_id}))

    async def save_expense(self, actor: Identity, academy_id: UUID, input: ExpenseInput, expense_id: UUID | None = None):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.finance_member(session, actor, academy_id)
            params = {"academy": academy_id, "id": expense_id, **input.model_dump()}
            if expense_id: value = row(await session.execute(text('UPDATE "Expense" SET "branchId"=:branchId,amount=:amount,"incurredOn"=:incurredOn,category=:category,vendor=:vendor,note=:note WHERE id=:id AND "academyId"=:academy RETURNING id,"branchId",amount,"incurredOn",category,vendor,note,"createdAt"'), params))
            else: value = row(await session.execute(text('INSERT INTO "Expense"("academyId","branchId",amount,"incurredOn",category,vendor,note) VALUES(:academy,:branchId,:amount,:incurredOn,:category,:vendor,:note) RETURNING id,"branchId",amount,"incurredOn",category,vendor,note,"createdAt"'), params))
            if not value: raise ApiError(404, "Expense not found.")
            await self.audit(session, actor, academy_id, "expense.saved", f"Saved {input.category} expense")
            return value

    async def delete_expense(self, actor: Identity, academy_id: UUID, expense_id: UUID):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.finance_member(session, actor, academy_id)
            if not await session.scalar(text('DELETE FROM "Expense" WHERE id=:id AND "academyId"=:academy RETURNING id'), {"id": expense_id, "academy": academy_id}): raise ApiError(404, "Expense not found.")
            await self.audit(session, actor, academy_id, "expense.deleted", f"Deleted expense {expense_id}")

    async def finance_summary(self, actor: Identity, academy_id: UUID, start: date, end: date):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.finance_member(session, actor, academy_id)
            collections = await session.scalar(text('SELECT COALESCE(sum(amount),0) FROM "Payment" WHERE "academyId"=:academy AND "paidOn" BETWEEN :start AND :end'), {"academy": academy_id, "start": start, "end": end})
            refunds = await session.scalar(text('SELECT COALESCE(sum(amount),0) FROM "Refund" WHERE "academyId"=:academy AND "refundedOn" BETWEEN :start AND :end'), {"academy": academy_id, "start": start, "end": end})
            expenses = await session.scalar(text('SELECT COALESCE(sum(amount),0) FROM "Expense" WHERE "academyId"=:academy AND "incurredOn" BETWEEN :start AND :end'), {"academy": academy_id, "start": start, "end": end})
            outstanding = await session.scalar(text('''SELECT COALESCE(sum(GREATEST(i.amount-i.discount-COALESCE(x.net,0),0)),0) FROM "Invoice" i LEFT JOIN (SELECT p."invoiceId",sum(p.amount)-sum(COALESCE(r.amount,0)) net FROM "Payment" p LEFT JOIN (SELECT "paymentId",sum(amount) amount FROM "Refund" GROUP BY "paymentId") r ON r."paymentId"=p.id GROUP BY p."invoiceId") x ON x."invoiceId"=i.id WHERE i."academyId"=:academy AND i.status<>'VOID' '''), {"academy": academy_id})
            trends = rows(await session.execute(text('''WITH months AS (SELECT generate_series(date_trunc('month',CAST(:end AS date))-interval '11 months',date_trunc('month',CAST(:end AS date)),interval '1 month')::date AS "month") SELECT m."month",COALESCE((SELECT sum(p.amount) FROM "Payment" p WHERE p."academyId"=:academy AND date_trunc('month',p."paidOn")=m."month"),0)-COALESCE((SELECT sum(r.amount) FROM "Refund" r WHERE r."academyId"=:academy AND date_trunc('month',r."refundedOn")=m."month"),0) revenue,COALESCE((SELECT sum(e.amount) FROM "Expense" e WHERE e."academyId"=:academy AND date_trunc('month',e."incurredOn")=m."month"),0) expenses FROM months m ORDER BY m."month"'''), {"academy": academy_id, "end": end}))
            distribution = rows(await session.execute(text('''SELECT p."branchId",COALESCE(b.name,'Unassigned') "branchName",sum(p.amount)-COALESCE(sum(r.amount),0) revenue FROM "Payment" p LEFT JOIN "Branch" b ON b.id=p."branchId" LEFT JOIN (SELECT "paymentId",sum(amount) amount FROM "Refund" GROUP BY "paymentId") r ON r."paymentId"=p.id WHERE p."academyId"=:academy AND p."paidOn" BETWEEN :start AND :end GROUP BY p."branchId",b.name ORDER BY revenue DESC'''), {"academy": academy_id, "start": start, "end": end}))
            return {"collections": collections, "refunds": refunds, "expenses": expenses, "outstanding": outstanding, "net": collections-refunds-expenses, "monthlyTrend": trends, "branchDistribution": distribution}

    async def link_guardian(self, actor: Identity, academy_id: UUID, input: GuardianLinkInput):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id, True)
            guardian = row(await session.execute(text('SELECT id, roles FROM "Membership" WHERE id=:id AND "academyId"=:academy'), {"id": input.guardianMembershipId, "academy": academy_id}))
            if not guardian or "GUARDIAN" not in guardian["roles"]: raise ApiError(400, "Choose a guardian membership from this academy.")
            if not await session.scalar(text('SELECT 1 FROM "Athlete" WHERE id=:athlete AND "academyId"=:academy'), {"athlete": input.athleteId, "academy": academy_id}): raise ApiError(404, "Athlete not found.")
            await session.execute(text('INSERT INTO "GuardianAthlete" ("academyId", "guardianMembershipId", "athleteId") VALUES (:academy,:guardian,:athlete) ON CONFLICT DO NOTHING'), {"academy": academy_id, "guardian": input.guardianMembershipId, "athlete": input.athleteId})
            await self.audit(session, actor, academy_id, "guardian.linked", "Linked guardian to athlete")

    async def sessions(self, actor: Identity, academy_id: UUID):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id)
            return rows(await session.execute(text('SELECT id, "branchId", "coachMembershipId", title, "startsAt", "endsAt", status FROM "TrainingSession" WHERE "academyId"=:academy ORDER BY "startsAt" DESC LIMIT 100'), {"academy": academy_id}))

    async def create_session(self, actor: Identity, academy_id: UUID, input: SessionInput):
        if input.endsAt <= input.startsAt: raise ApiError(400, "The session must end after it starts.")
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id, True)
            value = row(await session.execute(text("INSERT INTO \"TrainingSession\" (\"academyId\",\"branchId\",\"coachMembershipId\",title,\"startsAt\",\"endsAt\",status) VALUES (:academy,:branch,:coach,:title,:starts,:ends,'OPEN') RETURNING id,\"branchId\",\"coachMembershipId\",title,\"startsAt\",\"endsAt\",status"), {"academy": academy_id, "branch": input.branchId, "coach": input.coachMembershipId, "title": input.title, "starts": input.startsAt, "ends": input.endsAt}))
            await self.audit(session, actor, academy_id, "session.created", f"Created {value['title']}")
            return value

    async def add_roster(self, actor: Identity, academy_id: UUID, session_id: UUID, athlete_id: UUID):
        async with self.db.as_actor(actor, academy_id) as session:
            await self.member(session, actor, academy_id, True)
            await session.execute(text('INSERT INTO "SessionRoster" ("academyId","sessionId","athleteId") VALUES (:academy,:session,:athlete) ON CONFLICT DO NOTHING'), {"academy": academy_id, "session": session_id, "athlete": athlete_id})
            await self.audit(session, actor, academy_id, "session.roster.updated", "Added athlete to session roster")

    async def mark_attendance(self, actor: Identity, academy_id: UUID, session_id: UUID, athlete_id: UUID, input: AttendanceInput, source: str):
        async with self.db.as_actor(actor, academy_id) as session:
            member = await self.member(session, actor, academy_id)
            assigned = await session.scalar(text('SELECT 1 FROM "TrainingSession" WHERE id=:session AND "academyId"=:academy AND ("coachMembershipId"=:membership OR :admin)'), {"session": session_id, "academy": academy_id, "membership": member["id"], "admin": "ADMIN" in member["roles"]})
            if not assigned and source != "QR": raise ApiError(403, "You are not assigned to this session.")
            if source == "QR" and not await session.scalar(text("SELECT 1 FROM \"TrainingSession\" WHERE id=:session AND status='OPEN'"), {"session": session_id}): raise ApiError(409, "Session check-in is not open.")
            if not await session.scalar(text('SELECT 1 FROM "SessionRoster" WHERE "sessionId"=:session AND "athleteId"=:athlete AND "academyId"=:academy'), {"session": session_id, "athlete": athlete_id, "academy": academy_id}): raise ApiError(404, "Athlete is not on this session roster.")
            existing = row(await session.execute(text('SELECT id, status FROM "AthleteAttendance" WHERE "sessionId"=:session AND "athleteId"=:athlete'), {"session": session_id, "athlete": athlete_id}))
            if existing and source == "QR": return row(await session.execute(text('SELECT id,"sessionId","athleteId",status,source,"checkedAt" FROM "AthleteAttendance" WHERE id=:id'), {"id": existing["id"]}))
            value = row(await session.execute(text('INSERT INTO "AthleteAttendance" ("academyId","sessionId","athleteId",status,source,"actorId","correctionReason") VALUES (:academy,:session,:athlete,CAST(:status AS "AttendanceStatus"),:source,:actor,:reason) ON CONFLICT ("sessionId","athleteId") DO UPDATE SET status=EXCLUDED.status, source=EXCLUDED.source, "actorId"=EXCLUDED."actorId", "correctionReason"=EXCLUDED."correctionReason", "updatedAt"=now() RETURNING id,"sessionId","athleteId",status,source,"checkedAt"'), {"academy": academy_id, "session": session_id, "athlete": athlete_id, "status": input.status, "source": source, "actor": actor.id, "reason": input.correctionReason}))
            await self.audit(session, actor, academy_id, "attendance.marked", f"Recorded {input.status} attendance")
            return value

    async def create_qr(self, actor: Identity, academy_id: UUID, input: QrInput):
        if (input.kind == "SESSION") != bool(input.sessionId): raise ApiError(400, "Session QR codes require a session; staff QR codes do not.")
        async with self.db.as_actor(actor, academy_id) as session:
            member = await self.member(session, actor, academy_id)
            if input.kind == "SESSION" and "ADMIN" not in member["roles"]:
                allowed = await session.scalar(text('SELECT 1 FROM "TrainingSession" WHERE id=:session AND "academyId"=:academy AND "coachMembershipId"=:member'), {"session": input.sessionId, "academy": academy_id, "member": member["id"]})
                if not allowed: raise ApiError(403, "You are not assigned to this session.")
            token = token_hex(32); expires = datetime.now(timezone.utc) + timedelta(minutes=2)
            await session.execute(text('INSERT INTO "AttendanceQr" ("academyId",kind,"branchId","sessionId","tokenHash","expiresAt","createdBy") VALUES (:academy,CAST(:kind AS "QrKind"),:branch,:session,:hash,:expires,:actor)'), {"academy": academy_id, "kind": input.kind, "branch": input.branchId, "session": input.sessionId, "hash": hashlib.sha256(token.encode()).hexdigest(), "expires": expires, "actor": actor.id})
            origin = os.getenv("MOBILE_APP_ORIGIN", "http://localhost:5175")
            return {"token": token, "url": f"{origin}/check-in#{token}", "expiresAt": expires}

    async def redeem_qr(self, actor: Identity, input):
        digest = hashlib.sha256(input.token.encode()).hexdigest()
        async with self.db.as_actor(actor) as session:
            qr = row(await session.execute(text('SELECT id,"academyId",kind,"branchId","sessionId" FROM "AttendanceQr" WHERE "tokenHash"=:hash AND NOT closed AND "expiresAt">now()'), {"hash": digest}))
            if not qr: raise ApiError(400, "This check-in code has expired or is unavailable.")
            await session.execute(text("SELECT set_config('app.academy', :academy, true)"), {"academy": str(qr["academyId"])})
            membership = row(await session.execute(text('SELECT id, roles FROM "Membership" WHERE "academyId"=:academy AND "userId"=:actor AND active'), {"academy": qr["academyId"], "actor": actor.id}))
            if not membership: raise ApiError(403, "You do not belong to this academy.")
            if qr["kind"] == "STAFF":
                if not set(membership["roles"]) & {"ADMIN", "COACH", "FINANCE", "SCORER"}: raise ApiError(403, "This code is for academy staff.")
                local_date = await session.scalar(text("SELECT (now() AT TIME ZONE 'Asia/Kolkata')::date"))
                value = row(await session.execute(text('INSERT INTO "StaffAttendance" ("academyId","membershipId","branchId","localDate",source,"actorId") VALUES (:academy,:member,:branch,:date,\'QR\',:actor) ON CONFLICT ("academyId","membershipId","localDate") DO UPDATE SET "updatedAt"=now() RETURNING id,"membershipId","branchId","localDate",status,source,"checkedAt"'), {"academy": qr["academyId"], "member": membership["id"], "branch": qr["branchId"], "date": local_date, "actor": actor.id}))
                await self.audit(session, actor, qr["academyId"], "staff.attendance.checked_in", "Checked in via QR")
                return value
            athlete_id = input.athleteId
            if not athlete_id: raise ApiError(400, "Select an athlete to check in.")
            allowed = await session.scalar(text('SELECT 1 FROM "Athlete" a WHERE a.id=:athlete AND a."academyId"=:academy AND (a."membershipId"=:member OR EXISTS (SELECT 1 FROM "GuardianAthlete" g WHERE g."athleteId"=a.id AND g."guardianMembershipId"=:member))'), {"athlete": athlete_id, "academy": qr["academyId"], "member": membership["id"]})
            if not allowed: raise ApiError(403, "You cannot check in this athlete.")
            return await self.mark_attendance(actor, qr["academyId"], qr["sessionId"], athlete_id, AttendanceInput(status="PRESENT"), "QR")
