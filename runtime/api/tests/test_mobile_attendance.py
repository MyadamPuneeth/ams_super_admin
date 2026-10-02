from datetime import date, datetime, timezone

from ams_api.auth import AuthService
from test_foundation import ACADEMY, OTHER, BRANCH, ADMIN, client, tokens, request

ORIGIN = {"Origin": "http://localhost:5175", "X-AMS-Client": "mobile"}

def sign_in(client, username, password):
    return client.post("/api/auth/mobile/sign-in", headers=ORIGIN, json={"username": username, "password": password})

def admin_request(client, token, path, method='GET', body=None):
    response = client.request(method, path, headers={"Authorization": f"Bearer {token}", "Origin": ORIGIN['Origin']}, json=body)
    return response.status_code, None if response.status_code == 204 else response.json()

def test_one_academy_scanner_records_arrival_time(client, tokens):
    admin = tokens['admin']
    _, athlete = admin_request(client, admin, f'/api/academies/{ACADEMY}/athletes', 'POST', {'name': 'Scanner Athlete'})
    account = {'personType': 'ATHLETE', 'personId': athlete['id'], 'username': 'scanner.athlete',
        'temporaryPassword': 'temporary-password-123', 'name': 'Scanner Athlete', 'email': 'scanner.athlete@example.test'}
    assert admin_request(client, admin, f'/api/academies/{ACADEMY}/mobile-accounts', 'POST', account)[0] == 200
    assert sign_in(client, account['username'], account['temporaryPassword']).status_code == 204
    assert client.post('/api/auth/mobile/change-required', headers=ORIGIN, json={'newPassword': 'scanner-new-password-123'}).status_code == 204
    code_response = client.post(f'/api/academies/{ACADEMY}/my-check-in-code', headers=ORIGIN)
    assert code_response.status_code == 200
    code = code_response.json()['code']
    assert code.startswith('rallyone-member:')
    assert client.post(f'/api/academies/{ACADEMY}/scan-member', headers=ORIGIN, json={'code': code}).status_code == 403
    assert admin_request(client, admin, f'/api/academies/{OTHER}/scan-member', 'POST', {'code': code})[0] == 403
    assert admin_request(client, admin, f'/api/academies/{ACADEMY}/scan-member', 'POST', {'code': code[:-1] + ('0' if code[-1] != '0' else '1')})[0] == 400
    status, scan = admin_request(client, admin, f'/api/academies/{ACADEMY}/scan-member', 'POST', {'code': code})
    assert status == 200 and scan['name'] == 'Scanner Athlete' and scan['status'] == 'PRESENT'
    assert (datetime.now(timezone.utc) - datetime.fromisoformat(scan['checkedAt'])).total_seconds() < 10
    assert admin_request(client, admin, f'/api/academies/{ACADEMY}/scan-member', 'POST', {'code': code})[0] == 409
    month = client.get(f"/api/academies/{ACADEMY}/personal-attendance?month={scan['localDate'][:7]}-01", headers=ORIGIN)
    assert (month.json()['present'], month.json()['eligible']) == (1, 1)
    assert datetime.fromisoformat(month.json()['days'][0]['checkedAt']) == datetime.fromisoformat(scan['checkedAt'])
    assert client.post('/api/auth/mobile/sign-out', headers=ORIGIN).status_code == 204
    staff = {'personType': 'STAFF', 'personId': None, 'username': 'scanner.staff',
        'temporaryPassword': 'temporary-password-123', 'name': 'Scanner Staff', 'email': 'scanner.staff@example.test'}
    assert admin_request(client, admin, f'/api/academies/{ACADEMY}/mobile-accounts', 'POST', staff)[0] == 200
    assert sign_in(client, staff['username'], staff['temporaryPassword']).status_code == 204
    assert client.post('/api/auth/mobile/change-required', headers=ORIGIN, json={'newPassword': 'staff-new-password-123'}).status_code == 204
    staff_code = client.post(f'/api/academies/{ACADEMY}/my-check-in-code', headers=ORIGIN).json()['code']
    status, staff_scan = admin_request(client, admin, f'/api/academies/{ACADEMY}/scan-member', 'POST', {'code': staff_code})
    assert status == 200 and staff_scan['personType'] == 'STAFF' and staff_scan['status'] == 'PRESENT'
    assert admin_request(client, admin, f'/api/academies/{ACADEMY}/scan-member', 'POST', {'code': staff_code})[0] == 409
    staff_month = client.get(f"/api/academies/{ACADEMY}/personal-attendance?month={staff_scan['localDate'][:7]}-01", headers=ORIGIN)
    assert staff_month.json()['present'] == 1 and staff_month.json()['days'][0]['checkedAt']
    assert client.post('/api/auth/mobile/sign-out', headers=ORIGIN).status_code == 204

def test_mobile_accounts_attendance_and_revocation(client, tokens):
    admin = tokens["admin"]
    _, athlete = request(client, f"/api/academies/{ACADEMY}/athletes", admin, "POST", {"name": "Mobile Athlete"})
    table = request(client, f"/api/academies/{ACADEMY}/branches", admin)[1][0]["tables"][0]["id"]
    batch_ids = []
    for name, day, start, end in [
        ("Morning one", "2026-09-21", "08:00:00", "09:00:00"),
        ("Morning two", "2026-09-21", "09:00:00", "10:00:00"),
        ("Excused class", "2026-09-22", "08:00:00", "09:00:00"),
    ]:
        batch = {"name": name, "branchId": BRANCH, "tableId": table, "recurrence": "ONCE",
            "oneOffDate": day, "weekdays": [], "startsOn": day, "endsOn": day,
            "startTime": start, "endTime": end, "coachIds": [], "athleteIds": [athlete["id"]], "active": True}
        created = request(client, f"/api/academies/{ACADEMY}/batches", admin, "POST", batch)
        assert created[0] == 201
        batch_ids.append(created[1]['id'])
    account = {"personType": "ATHLETE", "personId": athlete["id"], "username": "mobile.athlete",
        "temporaryPassword": "temporary-password-123", "name": "Mobile Athlete", "email": "mobile.athlete@example.test"}
    status, provisioned = request(client, f"/api/academies/{ACADEMY}/mobile-accounts", admin, "POST", account)
    assert status == 200 and provisioned["membershipId"]
    assert sign_in(client, account["username"], "incorrect-password").status_code == 401
    assert sign_in(client, account["username"], account["temporaryPassword"]).status_code == 204
    assert client.get("/api/auth/mobile/me").json()["passwordChangeRequired"] is True
    assert client.get(f"/api/academies/{ACADEMY}/personal-attendance?month=2026-09-01", headers=ORIGIN).status_code == 403
    changed = client.post("/api/auth/mobile/change-required", headers=ORIGIN, json={"newPassword": "athlete-new-password-123"})
    assert changed.status_code == 204
    assert client.get("/api/auth/mobile/me").json()["passwordChangeRequired"] is False
    app = client.app
    original_auth = app.state.auth
    app.state.auth = AuthService(app.state.db)  # API restart: process-local signing key changes.
    assert client.get("/api/auth/mobile/me").status_code == 200
    app.state.auth = original_auth
    for day, status in [("2026-09-21", "PRESENT"), ("2026-09-22", "EXCUSED")]:
        mark = {"localDate": day, "entries": [{"personType": "ATHLETE", "personId": athlete["id"], "status": status}]}
        assert admin_request(client, admin, f"/api/academies/{ACADEMY}/daily-attendance", "PUT", mark)[0] == 204
    month = client.get(f"/api/academies/{ACADEMY}/personal-attendance?month=2026-09-01", headers=ORIGIN)
    assert month.status_code == 200 and (month.json()["present"], month.json()["eligible"], month.json()["rate"]) == (1, 1, 100)
    assert next(day for day in month.json()["days"] if day["localDate"] == "2026-09-22")["excused"] == 1
    previous = next(item for item in admin_request(client, admin, f"/api/academies/{ACADEMY}/batches")[1] if item['id'] == batch_ids[0])
    edited = {key: previous[key] for key in ('name','branchId','tableId','recurrence','oneOffDate','weekdays','startsOn','endsOn','startTime','endTime','coachIds','athleteIds','active')}
    edited['athleteIds'] = []
    assert admin_request(client, admin, f"/api/academies/{ACADEMY}/batches/{batch_ids[0]}", 'PUT', edited)[0] == 200
    unchanged = client.get(f"/api/academies/{ACADEMY}/personal-attendance?month=2026-09-01", headers=ORIGIN)
    assert (unchanged.json()['present'], unchanged.json()['eligible']) == (1, 1)
    assert admin_request(client, admin, f"/api/academies/{ACADEMY}/mobile-accounts/reset-password", "POST",
        {"membershipId": provisioned["membershipId"], "temporaryPassword": "replacement-password-123"})[0] == 204
    assert client.get("/api/auth/mobile/me").status_code == 401


    assert sign_in(client, account["username"], "replacement-password-123").status_code == 204
    assert client.get("/api/auth/mobile/me").json()["passwordChangeRequired"] is True
    assert client.post("/api/auth/mobile/sign-out", headers=ORIGIN).status_code == 204
    assert client.get("/api/auth/mobile/me").status_code == 401

    _, coach = admin_request(client, admin, f"/api/academies/{ACADEMY}/coaches", "POST",
        {"name": "Mobile Coach", "phone": "9999999999", "email": "coach.mobile@example.test", "notes": None, "active": True})
    staff = {"personType": "COACH", "personId": coach["id"], "username": "mobile.coach",
        "temporaryPassword": "temporary-password-123", "name": "Mobile Coach", "email": "coach.mobile@example.test"}
    _, staff_member = admin_request(client, admin, f"/api/academies/{ACADEMY}/mobile-accounts", "POST", staff)
    today = date.today().isoformat()
    weekdays = [date.today().weekday()]
    assert admin_request(client, admin, f"/api/academies/{ACADEMY}/staff-workdays", "PUT",
        {"membershipId": staff_member["membershipId"], "weekdays": weekdays})[0] == 200
    assert sign_in(client, staff["username"], staff["temporaryPassword"]).status_code == 204
    assert client.post("/api/auth/mobile/change-required", headers=ORIGIN, json={"newPassword": "coach-new-password-123"}).status_code == 204
    assert admin_request(client, admin, f"/api/academies/{ACADEMY}/daily-attendance", "PUT",
        {"localDate": today, "entries": [{"personType": "COACH", "personId": coach["id"], "status": "PRESENT"}]})[0] == 204
    manual = client.get(f"/api/academies/{ACADEMY}/personal-attendance?month={today[:7]}-01", headers=ORIGIN)
    assert manual.status_code == 200 and manual.json()["present"] == 1
    current = client.get(f"/api/academies/{ACADEMY}/personal-attendance?month={today[:7]}-01", headers=ORIGIN)
    assert current.status_code == 200 and current.json()["present"] == 1
    assert admin_request(client, admin, f"/api/academies/{ACADEMY}/members/{staff_member['membershipId']}", "PATCH",
        {"roles": ["COACH"], "allBranches": True, "branchIds": [], "active": False})[0] == 200
    assert client.get("/api/auth/mobile/me").status_code == 401



def test_coach_uses_same_password_on_web_and_mobile(client, tokens):
    admin = tokens["admin"]
    _, coach = admin_request(client, admin, f"/api/academies/{ACADEMY}/coaches", "POST",
        {"name": "Web Coach", "phone": "9999999998", "email": "web.coach@example.test", "notes": None, "active": True})
    _, athlete = admin_request(client, admin, f"/api/academies/{ACADEMY}/athletes", "POST",
        {"name": "Web Athlete", "homeBranchId": BRANCH, "monthlyFee": 800})
    table = admin_request(client, admin, f"/api/academies/{ACADEMY}/branches")[1][0]["tables"][0]["id"]
    _, batch = admin_request(client, admin, f"/api/academies/{ACADEMY}/batches", "POST",
        {"name": "Web coach class", "branchId": BRANCH, "tableId": table, "recurrence": "ONCE", "oneOffDate": "2026-11-01",
         "weekdays": [], "startsOn": "2026-11-01", "endsOn": "2026-11-01", "startTime": "14:00:00", "endTime": "15:00:00",
         "coachIds": [coach["id"]], "athleteIds": [athlete["id"]], "active": True})
    account = {"personType": "COACH", "personId": coach["id"], "username": "web.coach", "temporaryPassword": "temporary-password-123",
        "name": "Web Coach", "email": "web.coach@example.test"}
    assert admin_request(client, admin, f"/api/academies/{ACADEMY}/mobile-accounts", "POST", account)[0] == 200
    web_origin = {"Origin": "http://localhost:5173"}
    assert client.post("/api/auth/password/sign-in", headers=web_origin, json={"username": account["username"], "password": account["temporaryPassword"]}).status_code == 204
    assert client.post("/api/auth/password/change-required", headers=web_origin, json={"newPassword": "coach-password-one-123"}).status_code == 204
    old_web_session = client.cookies.get("ams_user_session")
    assert client.get("/api/me").json()["workspaces"][0]["membership"]["roles"] == ["COACH"]
    visible_coaches = client.get(f"/api/academies/{ACADEMY}/coaches")
    assert visible_coaches.status_code == 200
    assert visible_coaches.json()[0]["phone"] == ""
    assert visible_coaches.json()[0]["email"] is None
    assert [item["id"] for item in client.get(f"/api/academies/{ACADEMY}/athletes").json()] == [athlete["id"]]
    assert client.get(f"/api/academies/{ACADEMY}/athletes").json()[0]["monthlyFee"] == "0"
    assert [item["id"] for item in client.get(f"/api/academies/{ACADEMY}/batches").json()] == [batch["id"]]
    assert client.get(f"/api/academies/{ACADEMY}/daily-attendance?localDate=2026-11-01").status_code == 200
    assert client.get(f"/api/academies/{ACADEMY}/invoices?month=2026-11-01").status_code == 403
    assert client.post(f"/api/academies/{ACADEMY}/mobile-accounts", headers=web_origin, json=account).status_code == 403
    assert sign_in(client, account["username"], "coach-password-one-123").status_code == 204
    assert client.post("/api/auth/password/change", headers=web_origin,
        json={"currentPassword": "wrong-password-123", "newPassword": "coach-password-two-123"}).status_code == 401
    assert client.post("/api/auth/password/change", headers=web_origin,
        json={"currentPassword": "coach-password-one-123", "newPassword": "coach-password-two-123"}).status_code == 204
    assert client.get("/api/auth/mobile/me").status_code == 401
    client.cookies.clear(); client.cookies.set("ams_user_session", old_web_session)
    assert client.get("/api/me").status_code == 401
    client.cookies.clear()
    assert sign_in(client, account["username"], "coach-password-two-123").status_code == 204
    assert client.post("/api/auth/mobile/change", headers=ORIGIN,
        json={"currentPassword": "coach-password-two-123", "newPassword": "coach-password-three-123"}).status_code == 204
    assert client.get("/api/auth/mobile/me").status_code == 200
