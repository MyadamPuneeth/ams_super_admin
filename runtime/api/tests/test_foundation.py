import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

import asyncpg
import pytest
from fastapi.testclient import TestClient

from ams_api.auth import AuthService
from ams_api.main import app

ACADEMY = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
OTHER = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
BRANCH = "a1111111-1111-4111-8111-111111111111"
HIDDEN_BRANCH = "a2222222-2222-4222-8222-222222222222"
EXTERNAL_BRANCH = "b1111111-1111-4111-8111-111111111111"
ADMIN = "11111111-1111-4111-8111-111111111111"
COACH = "22222222-2222-4222-8222-222222222222"
OWNER = "44444444-4444-4444-8444-444444444444"
RECIPIENT = "55555555-5555-4555-8555-555555555555"

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as value: yield value

def request(client, path, token=None, method="GET", body=None):
    response = client.request(method, path, headers={"Authorization": f"Bearer {token}"} if token else {}, json=body)
    return response.status_code, None if response.status_code == 204 else response.json()

def login(client, user_id): return request(client, "/api/auth/demo", method="POST", body={"userId": user_id})[1]["accessToken"]

@pytest.fixture(scope="module")
def tokens(client): return {"admin": login(client, ADMIN), "coach": login(client, COACH), "owner": login(client, OWNER), "recipient": login(client, RECIPIENT)}

class TestFoundation:
    def test_01_authentication(self, client, tokens):
        assert request(client, "/api/me")[0] == 401
        assert request(client, "/api/me", tokens["admin"] + "a")[0] == 401
        assert request(client, "/api/auth/demo", method="POST", body={"userId": "99999999-9999-4999-8999-999999999999"})[0] == 401
        assert [item["academy"]["id"] for item in request(client, "/api/me", tokens["admin"])[1]["workspaces"]] == [ACADEMY]

    def test_02_authorization_and_branch_scope(self, client, tokens):
        assert request(client, f"/api/academies/{OTHER}/branches", tokens["admin"])[0] == 403
        assert request(client, f"/api/academies/{ACADEMY}/members", tokens["coach"])[0] == 403
        assert request(client, "/api/platform/academies", tokens["admin"])[0] == 403
        assert [item["id"] for item in request(client, f"/api/academies/{ACADEMY}/branches", tokens["coach"])[1]] == [BRANCH]
        assert request(client, f"/api/academies/{ACADEMY}/dashboard", tokens["coach"])[1]["members"] is None
        assert request(client, f"/api/academies/{ACADEMY}/branches", tokens["coach"], "POST", {"name": "Denied", "city": "Pune", "address": "Test road"})[0] == 403

    def test_03_rls_is_enforced_by_postgres(self):
        async def check():
            connection = await asyncpg.connect(os.environ["DATABASE_URL"])
            try:
                role = await connection.fetchrow("SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname=current_user")
                assert not role["rolsuper"] and not role["rolbypassrls"]
                async with connection.transaction():
                    await connection.execute("SELECT set_config('app.actor', $1, true), set_config('app.academy', $2, true)", COACH, ACADEMY)
                    assert [str(row["id"]) for row in await connection.fetch('SELECT id FROM "Branch"')] == [BRANCH]
                    assert not await connection.fetch('SELECT * FROM "Invitation"')
                    assert not await connection.fetch('SELECT * FROM "Audit"')
                    assert await connection.execute('UPDATE "Membership" SET roles=ARRAY[\'ADMIN\']::"Role"[]') == "UPDATE 0"
                assert not await connection.fetch('SELECT * FROM "Branch"')
            finally: await connection.close()
        asyncio.run(check())

    def test_04_relationship_and_audit_policy(self):
        async def check():
            connection = await asyncpg.connect(os.environ["DATABASE_URL"])
            try:
                async with connection.transaction():
                    await connection.execute("SELECT set_config('app.actor', $1, true), set_config('app.academy', $2, true)", ADMIN, ACADEMY)
                    with pytest.raises(asyncpg.ForeignKeyViolationError):
                        await connection.execute('INSERT INTO "TableResource"(id,"academyId","branchId",name) VALUES(gen_random_uuid(),$1,$2,\'Intruder\')', ACADEMY, EXTERNAL_BRANCH)
                async with connection.transaction():
                    await connection.execute("SELECT set_config('app.actor', $1, true), set_config('app.academy', $2, true)", ADMIN, ACADEMY)
                    with pytest.raises(asyncpg.InsufficientPrivilegeError): await connection.execute('DELETE FROM "Audit"')
            finally: await connection.close()
        asyncio.run(check())

    def test_05_branch_and_table_creation(self, client, tokens):
        status, branch = request(client, f"/api/academies/{ACADEMY}/branches", tokens["admin"], "POST", {"name": "Koramangala", "city": "Bengaluru", "address": "17, Club Road"})
        assert status == 201
        assert request(client, f"/api/academies/{ACADEMY}/branches/{branch['id']}/tables", tokens["admin"], "POST", {"name": "Table 1"})[0] == 201
        assert request(client, f"/api/academies/{ACADEMY}/branches/{branch['id']}/tables", tokens["admin"], "POST", {"name": "Table 1"})[0] == 409
        assert request(client, f"/api/academies/{ACADEMY}/branches/{EXTERNAL_BRANCH}/tables", tokens["admin"], "POST", {"name": "Intruder"})[0] == 404
        assert any(item["id"] == branch["id"] and len(item["tables"]) == 1 for item in request(client, f"/api/academies/{ACADEMY}/branches", tokens["admin"])[1])
        assert request(client, f"/api/academies/{ACADEMY}/branches", tokens["admin"], "POST", {"name": "  ", "city": "  ", "address": "   "})[0] == 400

    def test_06_revoked_invitation(self, client, tokens):
        body = {"email": "priya@example.test", "roles": ["COACH"], "allBranches": False, "branchIds": [BRANCH]}
        assert request(client, f"/api/academies/{ACADEMY}/invitations", tokens["coach"], "POST", body)[0] == 403
        assert request(client, f"/api/academies/{ACADEMY}/invitations", tokens["admin"], "POST", {**body, "branchIds": [EXTERNAL_BRANCH]})[0] == 400
        assert request(client, f"/api/academies/{ACADEMY}/invitations", tokens["admin"], "POST", {**body, "roles": ["ADMIN"]})[0] == 400
        _, invitation = request(client, f"/api/academies/{ACADEMY}/invitations", tokens["admin"], "POST", body)
        token = urlparse(invitation["invitationUrl"]).fragment
        assert request(client, f"/api/academies/{ACADEMY}/invitations/{invitation['id']}/revoke", tokens["admin"], "POST")[0] == 204
        assert request(client, "/api/invitations/accept", tokens["recipient"], "POST", {"token": token})[0] == 409

    def test_07_single_use_invitation(self, client, tokens):
        body = {"email": "priya@example.test", "roles": ["COACH"], "allBranches": False, "branchIds": [BRANCH]}
        _, invitation = request(client, f"/api/academies/{ACADEMY}/invitations", tokens["admin"], "POST", body)
        token = urlparse(invitation["invitationUrl"]).fragment
        assert request(client, "/api/invitations/accept", tokens["coach"], "POST", {"token": token})[0] == 409
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(lambda _: request(client, "/api/invitations/accept", tokens["recipient"], "POST", {"token": token})[0], range(2)))
        assert sorted(outcomes) == [200, 409]
        assert len(request(client, f"/api/academies/{ACADEMY}/branches", tokens["recipient"])[1]) == 1
        invitations = request(client, f"/api/academies/{ACADEMY}/invitations", tokens["admin"])[1]
        assert "tokenHash" not in str(invitations) and any(item["acceptedAt"] for item in invitations)

    def test_08_platform_onboarding(self, client, tokens):
        assert request(client, f"/api/academies/{ACADEMY}/branches", tokens["owner"])[0] == 403
        body = {"name": "Champions Academy", "slug": "champions", "adminName": "Maya Singh", "adminEmail": "maya@example.test", "adminUsername": "maya.admin", "temporaryPassword": "temporary-pass-123"}
        status, created = request(client, "/api/platform/academies", tokens["owner"], "POST", body)
        assert status == 201 and "invitationUrl" not in created
        assert created["handoff"]["emailSent"] is False

        before = len(request(client, "/api/platform/academies", tokens["owner"])[1])
        duplicate = {**body, "name": "Duplicate Academy", "slug": "duplicate-academy"}
        assert request(client, "/api/platform/academies", tokens["owner"], "POST", duplicate)[0] == 409
        assert len(request(client, "/api/platform/academies", tokens["owner"])[1]) == before

        pending = request(client, "/api/platform/credential-handoffs", tokens["owner"])[1]
        handoff = next(item for item in pending if item["id"] == created["handoff"]["id"])
        assert body["temporaryPassword"] not in str(pending)
        assert request(client, f"/api/platform/credential-handoffs/{handoff['id']}/reveal", tokens["owner"], "POST")[1]["temporaryPassword"] == body["temporaryPassword"]

        origin = {"Origin": "http://localhost:5173"}
        signed_in = client.post("/api/auth/password/sign-in", headers=origin, json={"username": "MAYA.ADMIN", "password": body["temporaryPassword"]})
        assert signed_in.status_code == 204 and signed_in.cookies.get("ams_user_session")
        me = client.get("/api/me").json()
        assert me["passwordChangeRequired"] is True
        workspace = next(item for item in me["workspaces"] if item["academy"]["id"] == created["academy"]["id"])
        assert workspace["membership"]["roles"] == ["ADMIN"]
        assert client.get(f"/api/academies/{created['academy']['id']}/dashboard").status_code == 403
        assert client.post("/api/auth/password/change-required", headers=origin, json={"newPassword": "replacement-pass-456"}).status_code == 204
        assert client.get("/api/me").json()["passwordChangeRequired"] is False
        assert client.get(f"/api/academies/{created['academy']['id']}/dashboard").status_code == 200
        assert client.post("/api/auth/password/sign-out", headers=origin).status_code == 204

        assert request(client, f"/api/platform/credential-handoffs/{handoff['id']}/copied", tokens["owner"], "POST")[0] == 204
        assert any(item["id"] == handoff["id"] for item in request(client, "/api/platform/credential-handoffs", tokens["owner"])[1])
        async def delivered(*_): pass
        client.app.state.service.mailer.send_credentials = delivered
        delivered_handoff = request(client, f"/api/platform/credential-handoffs/{handoff['id']}/retry-email", tokens["owner"], "POST")[1]
        assert delivered_handoff["copied"] and delivered_handoff["emailSent"]
        assert all(item["id"] != handoff["id"] for item in request(client, "/api/platform/credential-handoffs", tokens["owner"])[1])
        assert request(client, f"/api/platform/credential-handoffs/{handoff['id']}/reveal", tokens["owner"], "POST")[0] == 404

        lockout = {**body, "name": "Lockout Academy", "slug": "lockout-academy", "adminEmail": "locked@example.test", "adminUsername": "locked.admin"}
        assert request(client, "/api/platform/academies", tokens["owner"], "POST", lockout)[0] == 201
        for _ in range(5):
            response = client.post("/api/auth/password/sign-in", headers=origin, json={"username": lockout["adminUsername"], "password": "incorrect-pass-123"})
            assert response.status_code == 401 and response.json()["message"] == "Invalid username or password."
        assert client.post("/api/auth/password/sign-in", headers=origin, json={"username": lockout["adminUsername"], "password": lockout["temporaryPassword"]}).status_code == 401
        client.cookies.set("ams_user_session", "invalid")
        assert client.get("/api/me").status_code == 401
        client.cookies.delete("ams_user_session")

    def test_09_revocation_and_last_admin(self, client, tokens):
        members = request(client, f"/api/academies/{ACADEMY}/members", tokens["admin"])[1]
        coach_member = next(item for item in members if item["userId"] == COACH)
        patch = {"roles": ["COACH"], "allBranches": False, "branchIds": [BRANCH], "active": False}
        assert request(client, f"/api/academies/{ACADEMY}/members/{coach_member['id']}", tokens["admin"], "PATCH", patch)[0] == 200
        assert request(client, f"/api/academies/{ACADEMY}/branches", tokens["coach"])[0] == 403
        admin_member = next(item for item in members if item["userId"] == ADMIN)
        assert request(client, f"/api/academies/{ACADEMY}/members/{admin_member['id']}", tokens["admin"], "PATCH", {"roles": ["ADMIN"], "allBranches": True, "branchIds": [], "active": False})[0] == 409
        assert request(client, f"/api/academies/{ACADEMY}/members/{coach_member['id']}", tokens["admin"], "PATCH", {**patch, "active": True, "branchIds": [HIDDEN_BRANCH]})[0] == 200
        assert [item["id"] for item in request(client, f"/api/academies/{ACADEMY}/branches", tokens["coach"])[1]] == [HIDDEN_BRANCH]

    def test_10_suspension(self, client, tokens):
        assert request(client, f"/api/platform/academies/{ACADEMY}", tokens["owner"], "PATCH", {"active": False})[0] == 200
        assert request(client, f"/api/academies/{ACADEMY}/branches", tokens["admin"])[0] == 403
        assert not request(client, "/api/me", tokens["admin"])[1]["workspaces"]
        assert request(client, f"/api/platform/academies/{ACADEMY}", tokens["owner"], "PATCH", {"active": True})[0] == 200
        assert request(client, f"/api/academies/{ACADEMY}/branches", tokens["admin"])[0] == 200

    def test_11_audit_projection(self, client, tokens):
        status, activity = request(client, f"/api/academies/{ACADEMY}/activity", tokens["admin"])
        assert status == 200
        assert any(entry["action"] == "membership.updated" for entry in activity)
        assert any(entry["action"] == "invitation.accepted" for entry in activity)
        assert "invitationUrl" not in str(activity)

    def test_12_demo_auth_rejected_in_production(self, client):
        previous = os.environ["NODE_ENV"]
        os.environ["NODE_ENV"] = "production"
        try:
            with pytest.raises(RuntimeError, match="DEV_AUTH requires"): AuthService(client.app.state.db)
        finally: os.environ["NODE_ENV"] = previous

    def test_13_attendance_persists_and_staff_qr_is_idempotent(self, client, tokens):
        _, athlete = request(client, f"/api/academies/{ACADEMY}/athletes", tokens["admin"], "POST", {"name": "Rhea Iyer"})
        starts = "2026-09-20T10:00:00Z"; ends = "2026-09-20T11:00:00Z"
        _, session = request(client, f"/api/academies/{ACADEMY}/sessions", tokens["admin"], "POST", {"branchId": BRANCH, "title": "Morning training", "startsAt": starts, "endsAt": ends})
        assert request(client, f"/api/academies/{ACADEMY}/sessions/{session['id']}/roster", tokens["admin"], "POST", {"athleteId": athlete["id"]})[0] == 204
        status, record = request(client, f"/api/academies/{ACADEMY}/sessions/{session['id']}/attendance/{athlete['id']}", tokens["admin"], "PUT", {"status": "PRESENT", "correctionReason": "Arrived on time"})
        assert status == 200 and record["status"] == "PRESENT"
        _, qr = request(client, f"/api/academies/{ACADEMY}/attendance-qr", tokens["admin"], "POST", {"kind": "STAFF", "branchId": BRANCH})
        staff = request(client, "/api/attendance-qr/redeem", tokens["admin"], "POST", {"token": qr["token"]})
        again = request(client, "/api/attendance-qr/redeem", tokens["admin"], "POST", {"token": qr["token"]})
        assert staff[0] == 200 and again[0] == 200 and staff[1]["id"] == again[1]["id"]

    def test_14_platform_subscription(self, client, tokens):
        academy = request(client, "/api/platform/academies", tokens["owner"])[1][0]
        assert academy["subscriptionPlan"] == "STARTER" and academy["subscriptionStartsOn"]
        invalid = {"plan": "PRO", "status": "ACTIVE", "startsOn": "2026-10-01", "endsOn": "2026-09-01"}
        assert request(client, f"/api/platform/academies/{academy['id']}/subscription", tokens["owner"], "PATCH", invalid)[0] == 400
        valid = {**invalid, "endsOn": "2027-10-01"}
        status, updated = request(client, f"/api/platform/academies/{academy['id']}/subscription", tokens["owner"], "PATCH", valid)
        assert status == 200 and updated["subscriptionPlan"] == "PRO" and updated["subscriptionStatus"] == "ACTIVE"

    def test_15_platform_owner_password_and_lockout(self, client):
        origin = {"Origin": "http://localhost:5174"}
        signed_in = client.post("/api/platform/auth/sign-in", headers=origin, json={"username": "PLATFORM.OWNER", "password": "correct-horse-battery"})
        assert signed_in.status_code == 204 and signed_in.cookies.get("ams_platform_session")
        assert client.get("/api/me").json()["platformOwner"] is True
        assert client.post("/api/platform/auth/sign-out", headers=origin).status_code == 204
        assert client.get("/api/me").status_code == 401
        for _ in range(5):
            rejected = client.post("/api/platform/auth/sign-in", headers=origin, json={"username": "platform.owner", "password": "incorrect-password"})
            assert rejected.status_code == 401 and rejected.json()["message"] == "Invalid username or password."
        assert client.post("/api/platform/auth/sign-in", headers=origin, json={"username": "platform.owner", "password": "correct-horse-battery"}).status_code == 401

    def test_16_operations_attendance_and_finance(self, client, tokens):
        assert request(client, f"/api/academies/{OTHER}/coaches", tokens["admin"])[0] == 403
        _, coach = request(client, f"/api/academies/{ACADEMY}/coaches", tokens["admin"], "POST", {"name": "Kiran Coach", "phone": "9876543210", "email": None, "notes": None, "active": True})
        _, athlete = request(client, f"/api/academies/{ACADEMY}/athletes", tokens["admin"], "POST", {"name": "Finance Athlete", "homeBranchId": BRANCH, "monthlyFee": 1000})
        table_id = request(client, f"/api/academies/{ACADEMY}/branches", tokens["admin"])[1][0]["tables"][0]["id"]
        batch = {"name": "Evening Batch", "branchId": BRANCH, "tableId": table_id, "recurrence": "WEEKLY", "oneOffDate": None, "weekdays": [0, 2, 4], "startsOn": "2026-09-01", "endsOn": None, "startTime": "18:00:00", "endTime": "19:00:00", "coachIds": [coach["id"]], "athleteIds": [athlete["id"]], "active": True}
        assert request(client, f"/api/academies/{ACADEMY}/batches", tokens["admin"], "POST", batch)[0] == 201
        assert request(client, f"/api/academies/{ACADEMY}/batches", tokens["admin"], "POST", {**batch, "name": "Conflict"})[0] == 409

        register = request(client, f"/api/academies/{ACADEMY}/daily-attendance?localDate=2026-09-24", tokens["admin"])[1]
        assert any(item["personId"] == coach["id"] for item in register) and any(item["personId"] == athlete["id"] for item in register)
        attendance = {"localDate": "2026-09-24", "entries": [{"personType": "COACH", "personId": coach["id"], "status": "PRESENT"}, {"personType": "ATHLETE", "personId": athlete["id"], "status": "EXCUSED"}]}
        assert request(client, f"/api/academies/{ACADEMY}/daily-attendance", tokens["admin"], "PUT", attendance)[0] == 204
        assert {item["status"] for item in request(client, f"/api/academies/{ACADEMY}/daily-attendance?localDate=2026-09-24", tokens["admin"])[1] if item["personId"] in {coach["id"], athlete["id"]}} == {"PRESENT", "EXCUSED"}

        generate = {"billingMonth": "2026-09-01", "dueDate": "2026-09-10"}
        invoices = request(client, f"/api/academies/{ACADEMY}/invoices/generate", tokens["admin"], "POST", generate)[1]
        again = request(client, f"/api/academies/{ACADEMY}/invoices/generate", tokens["admin"], "POST", generate)[1]
        invoice = next(item for item in invoices if item["athleteId"] == athlete["id"])
        assert len([item for item in again if item["athleteId"] == athlete["id"]]) == 1
        payment = {"invoiceId": invoice["id"], "athleteId": athlete["id"], "branchId": BRANCH, "kind": "FEE", "amount": 400, "paidOn": "2026-09-24", "method": "UPI", "reference": "UPI-1", "note": None}
        assert request(client, f"/api/academies/{ACADEMY}/payments", tokens["admin"], "POST", {**payment, "amount": 1001})[0] == 400
        _, paid = request(client, f"/api/academies/{ACADEMY}/payments", tokens["admin"], "POST", payment)
        assert next(item for item in request(client, f"/api/academies/{ACADEMY}/invoices?month=2026-09-01", tokens["admin"])[1] if item["id"] == invoice["id"])["status"] == "PARTIAL"
        assert request(client, f"/api/academies/{ACADEMY}/payments/{paid['id']}/refunds", tokens["admin"], "POST", {"amount": 50, "refundedOn": "2026-09-24", "reason": "Correction"})[0] == 201
        assert request(client, f"/api/academies/{ACADEMY}/payments/{paid['id']}/refunds", tokens["admin"], "POST", {"amount": 351, "refundedOn": "2026-09-24", "reason": "Too much"})[0] == 400
        _, expense = request(client, f"/api/academies/{ACADEMY}/expenses", tokens["admin"], "POST", {"branchId": BRANCH, "amount": 100, "incurredOn": "2026-09-24", "category": "Equipment", "vendor": "Local shop", "note": None})
        summary = request(client, f"/api/academies/{ACADEMY}/finance-summary?start=2026-09-01&end=2026-09-30", tokens["admin"])[1]
        assert float(summary["collections"]) >= 400 and float(summary["refunds"]) >= 50 and float(summary["expenses"]) >= 100
        assert any(item["branchId"] == BRANCH for item in summary["branchDistribution"])
        assert request(client, f"/api/academies/{ACADEMY}/expenses/{expense['id']}", tokens["admin"], "DELETE")[0] == 204
        assert request(client, f"/api/academies/{ACADEMY}/payments/{paid['id']}", tokens["admin"], "DELETE")[0] == 204
