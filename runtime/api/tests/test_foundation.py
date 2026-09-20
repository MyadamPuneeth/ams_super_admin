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
        _, created = request(client, "/api/platform/academies", tokens["owner"], "POST", {"name": "Champions Academy", "slug": "champions", "adminEmail": "priya@example.test"})
        assert request(client, "/api/invitations/accept", tokens["recipient"], "POST", {"token": urlparse(created["invitationUrl"]).fragment})[0] == 200
        workspace = next(item for item in request(client, "/api/me", tokens["recipient"])[1]["workspaces"] if item["academy"]["id"] == created["academy"]["id"])
        assert workspace["membership"]["roles"] == ["ADMIN"]

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

    def test_12_demo_auth_rejected_in_production(self):
        previous = os.environ["NODE_ENV"]
        os.environ["NODE_ENV"] = "production"
        try:
            with pytest.raises(RuntimeError, match="DEV_AUTH requires"): AuthService()
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
