import os
from contextlib import asynccontextmanager
from datetime import date
from uuid import UUID, uuid4
from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException
from .auth import AuthService, DEMO_PROFILES, PLATFORM_COOKIE, USER_COOKIE, Identity, actor
from .database import Database
from .errors import ApiError, api_error, body, http_error, unexpected_error, validation_error
from .schemas import *
from .service import AcademyService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Refuse traffic before verifying that the request role cannot bypass tenant RLS.
    app.state.db = Database(); await app.state.db.verify_runtime_role()
    app.state.auth = AuthService(app.state.db); app.state.service = AcademyService(app.state.db)
    yield
    await app.state.db.close()

production = os.getenv("NODE_ENV") == "production"
app = FastAPI(title="AMS API", version="0.2.0", docs_url=None if production else "/api/docs", openapi_url=None if production else "/api/openapi.json", lifespan=lifespan)
origins = [value.strip() for value in os.getenv("WEB_ORIGINS", "http://localhost:5173,http://localhost:5174,http://localhost:5175").split(",") if value.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_exception_handler(ApiError, api_error); app.add_exception_handler(StarletteHTTPException, http_error); app.add_exception_handler(RequestValidationError, validation_error); app.add_exception_handler(Exception, unexpected_error)

@app.middleware("http")
async def security(request: Request, call_next):
    request.state.request_id = str(uuid4())
    if request.method in {"POST", "PUT", "PATCH", "DELETE"} and (request.cookies.get(PLATFORM_COOKIE) or request.cookies.get(USER_COOKIE) or request.url.path.startswith(("/api/platform/auth/", "/api/auth/password/"))):
        if request.headers.get("origin") not in origins: return body(403, "Request origin is not allowed.", request)
    try:
        response = await call_next(request)
    except IntegrityError:
        # Constraint failures are safe conflicts; database details stay private.
        response = body(409, "This change is not allowed in the current state.", request)
    response.headers.update({"X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY", "Referrer-Policy": "no-referrer"})
    return response

def service(request: Request) -> AcademyService: return request.app.state.service

@app.post("/api/platform/auth/sign-in", tags=["platform"], status_code=204)
async def platform_sign_in(input: PlatformSignInInput, request: Request, response: Response):
    token = await request.app.state.auth.platform_sign_in(input.username, input.password)
    response.delete_cookie(USER_COOKIE, path="/api", secure=production, httponly=True, samesite="strict")
    response.set_cookie(PLATFORM_COOKIE, token, max_age=28_800, httponly=True, secure=production, samesite="strict", path="/api")

@app.post("/api/platform/auth/sign-out", tags=["platform"], status_code=204)
async def platform_sign_out(response: Response): response.delete_cookie(PLATFORM_COOKIE, path="/api", secure=production, httponly=True, samesite="strict")

@app.get("/api/auth/config", tags=["authentication"], response_model=AuthConfigDto)
async def auth_config(request: Request): return {"demo": request.app.state.auth.demo, "profiles": DEMO_PROFILES if request.app.state.auth.demo else []}
@app.post("/api/auth/demo", tags=["authentication"], response_model=TokenDto)
async def demo(input: DemoInput, request: Request): return {"accessToken": request.app.state.auth.issue_demo(input.userId)}
@app.post("/api/auth/password/sign-in", tags=["authentication"], status_code=204)
async def password_sign_in(input: PasswordSignInInput, request: Request, response: Response):
    token = await request.app.state.auth.password_sign_in(input.username, input.password)
    response.delete_cookie(PLATFORM_COOKIE, path="/api", secure=production, httponly=True, samesite="strict")
    response.set_cookie(USER_COOKIE, token, max_age=28_800, httponly=True, secure=production, samesite="strict", path="/api")
@app.post("/api/auth/password/change-required", tags=["authentication"], status_code=204)
async def password_change(input: PasswordChangeInput, request: Request, response: Response, identity: Identity = Depends(actor)):
    token = await request.app.state.auth.change_password(identity, input.newPassword)
    response.set_cookie(USER_COOKIE, token, max_age=28_800, httponly=True, secure=production, samesite="strict", path="/api")
@app.post("/api/auth/password/sign-out", tags=["authentication"], status_code=204)
async def password_sign_out(response: Response): response.delete_cookie(USER_COOKIE, path="/api", secure=production, httponly=True, samesite="strict")
@app.get("/api/me", tags=["workspaces"], response_model=MeDto)
async def me(identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.me(identity)
@app.post("/api/invitations/accept", tags=["workspaces"], response_model=AcceptDto)
async def accept(input: AcceptInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.accept(identity, input.token)
@app.get("/api/platform/academies", tags=["platform"], response_model=list[AcademyDto])
async def academies(identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.academies(identity)
@app.post("/api/platform/academies", tags=["platform"], status_code=201, response_model=AcademyCreatedDto)
async def create_academy(input: AcademyInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.create_academy(identity, input)
@app.get("/api/platform/credential-handoffs", tags=["platform"], response_model=list[HandoffDto])
async def credential_handoffs(identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.handoffs(identity)
@app.post("/api/platform/credential-handoffs/{handoff_id}/reveal", tags=["platform"], response_model=HandoffSecretDto)
async def reveal_credentials(handoff_id: UUID, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.reveal_handoff(identity, handoff_id)
@app.post("/api/platform/credential-handoffs/{handoff_id}/copied", tags=["platform"], status_code=204)
async def copied_credentials(handoff_id: UUID, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): await app_service.mark_handoff_copied(identity, handoff_id); return Response(status_code=204)
@app.post("/api/platform/credential-handoffs/{handoff_id}/retry-email", tags=["platform"], response_model=HandoffDto)
async def retry_credentials_email(handoff_id: UUID, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.email_handoff(identity, handoff_id)
@app.patch("/api/platform/academies/{academy_id}", tags=["platform"], response_model=AcademyDto)
async def set_active(academy_id: UUID, input: ActiveInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.set_active(identity, academy_id, input.active)
@app.patch("/api/platform/academies/{academy_id}/subscription", tags=["platform"], response_model=AcademyDto)
async def set_subscription(academy_id: UUID, input: SubscriptionInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.set_subscription(identity, academy_id, input)
@app.get("/api/academies/{academy_id}/dashboard", tags=["academy"], response_model=DashboardDto)
async def dashboard(academy_id: UUID, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.dashboard(identity, academy_id)
@app.get("/api/academies/{academy_id}/branches", tags=["academy"], response_model=list[BranchDto])
async def branches(academy_id: UUID, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.branches(identity, academy_id)
@app.post("/api/academies/{academy_id}/branches", tags=["academy"], status_code=201, response_model=BranchDto)
async def create_branch(academy_id: UUID, input: BranchInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.create_branch(identity, academy_id, input)
@app.put("/api/academies/{academy_id}/branches/{branch_id}", tags=["academy"], response_model=BranchDto)
async def update_branch(academy_id: UUID, branch_id: UUID, input: BranchInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.update_branch(identity, academy_id, branch_id, input)
@app.delete("/api/academies/{academy_id}/branches/{branch_id}", tags=["academy"], status_code=204)
async def delete_branch(academy_id: UUID, branch_id: UUID, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): await app_service.delete_branch(identity, academy_id, branch_id); return Response(status_code=204)
@app.post("/api/academies/{academy_id}/branches/{branch_id}/tables", tags=["academy"], status_code=201, response_model=TableDto)
async def create_table(academy_id: UUID, branch_id: UUID, input: TableInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.create_table(identity, academy_id, branch_id, input.name)
@app.put("/api/academies/{academy_id}/branches/{branch_id}/tables/{table_id}", tags=["academy"], response_model=TableDto)
async def update_table(academy_id: UUID, branch_id: UUID, table_id: UUID, input: TableInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.update_table(identity, academy_id, branch_id, table_id, input.name)
@app.delete("/api/academies/{academy_id}/branches/{branch_id}/tables/{table_id}", tags=["academy"], status_code=204)
async def delete_table(academy_id: UUID, branch_id: UUID, table_id: UUID, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): await app_service.delete_table(identity, academy_id, branch_id, table_id); return Response(status_code=204)
@app.get("/api/academies/{academy_id}/members", tags=["academy"], response_model=list[MemberDto])
async def members(academy_id: UUID, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.members(identity, academy_id)
@app.patch("/api/academies/{academy_id}/members/{member_id}", tags=["academy"], response_model=MemberDto)
async def update_member(academy_id: UUID, member_id: UUID, input: MemberInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.update_member(identity, academy_id, member_id, input)
@app.get("/api/academies/{academy_id}/invitations", tags=["academy"], response_model=list[InvitationDto])
async def invitations(academy_id: UUID, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.invitations(identity, academy_id)
@app.post("/api/academies/{academy_id}/invitations", tags=["academy"], status_code=201, response_model=InvitationCreatedDto)
async def invite(academy_id: UUID, input: InvitationInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.create_invitation(identity, academy_id, input)
@app.post("/api/academies/{academy_id}/invitations/{invitation_id}/revoke", tags=["academy"], status_code=204)
async def revoke(academy_id: UUID, invitation_id: UUID, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): await app_service.revoke(identity, academy_id, invitation_id); return Response(status_code=204)
@app.get("/api/academies/{academy_id}/activity", tags=["academy"], response_model=list[AuditDto])
async def activity(academy_id: UUID, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.activity(identity, academy_id)
@app.get("/api/academies/{academy_id}/athletes", tags=["attendance"], response_model=list[AthleteDto])
async def athletes(academy_id: UUID, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.athletes(identity, academy_id)
@app.post("/api/academies/{academy_id}/athletes", tags=["attendance"], status_code=201, response_model=AthleteDto)
async def create_athlete(academy_id: UUID, input: AthleteInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.create_athlete(identity, academy_id, input)
@app.patch("/api/academies/{academy_id}/athletes/{athlete_id}", tags=["academy"], response_model=AthleteDto)
async def update_athlete(academy_id: UUID, athlete_id: UUID, input: AthleteUpdateInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.update_athlete(identity, academy_id, athlete_id, input)
@app.get("/api/academies/{academy_id}/coaches", tags=["academy"], response_model=list[CoachDto])
async def coaches(academy_id: UUID, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.coaches(identity, academy_id)
@app.post("/api/academies/{academy_id}/coaches", tags=["academy"], status_code=201, response_model=CoachDto)
async def create_coach(academy_id: UUID, input: CoachInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.create_coach(identity, academy_id, input)
@app.put("/api/academies/{academy_id}/coaches/{coach_id}", tags=["academy"], response_model=CoachDto)
async def update_coach(academy_id: UUID, coach_id: UUID, input: CoachInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.update_coach(identity, academy_id, coach_id, input)
@app.get("/api/academies/{academy_id}/batches", tags=["academy"], response_model=list[BatchDto])
async def batches(academy_id: UUID, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.batches(identity, academy_id)
@app.post("/api/academies/{academy_id}/batches", tags=["academy"], status_code=201, response_model=BatchDto)
async def create_batch(academy_id: UUID, input: BatchInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.save_batch(identity, academy_id, input)
@app.put("/api/academies/{academy_id}/batches/{batch_id}", tags=["academy"], response_model=BatchDto)
async def update_batch(academy_id: UUID, batch_id: UUID, input: BatchInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.save_batch(identity, academy_id, input, batch_id)
@app.delete("/api/academies/{academy_id}/batches/{batch_id}", tags=["academy"], status_code=204)
async def delete_batch(academy_id: UUID, batch_id: UUID, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): await app_service.delete_batch(identity, academy_id, batch_id); return Response(status_code=204)
@app.get("/api/academies/{academy_id}/daily-attendance", tags=["attendance"], response_model=list[DailyAttendanceDto])
async def daily_attendance(academy_id: UUID, localDate: date, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.daily_attendance(identity, academy_id, localDate)
@app.put("/api/academies/{academy_id}/daily-attendance", tags=["attendance"], status_code=204)
async def save_daily_attendance(academy_id: UUID, input: DailyAttendanceInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): await app_service.save_daily_attendance(identity, academy_id, input); return Response(status_code=204)
@app.get("/api/academies/{academy_id}/invoices", tags=["finance"], response_model=list[InvoiceDto])
async def invoices(academy_id: UUID, month: date | None = None, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.invoices(identity, academy_id, month.replace(day=1) if month else None)
@app.post("/api/academies/{academy_id}/invoices/generate", tags=["finance"], response_model=list[InvoiceDto])
async def generate_invoices(academy_id: UUID, input: InvoiceGenerateInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.generate_invoices(identity, academy_id, input)
@app.patch("/api/academies/{academy_id}/invoices/{invoice_id}", tags=["finance"], response_model=InvoiceDto)
async def update_invoice(academy_id: UUID, invoice_id: UUID, input: InvoiceUpdateInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.update_invoice(identity, academy_id, invoice_id, input)
@app.get("/api/academies/{academy_id}/payments", tags=["finance"], response_model=list[PaymentDto])
async def payments(academy_id: UUID, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.payments(identity, academy_id)
@app.post("/api/academies/{academy_id}/payments", tags=["finance"], status_code=201, response_model=PaymentDto)
async def create_payment(academy_id: UUID, input: PaymentInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.save_payment(identity, academy_id, input)
@app.put("/api/academies/{academy_id}/payments/{payment_id}", tags=["finance"], response_model=PaymentDto)
async def update_payment(academy_id: UUID, payment_id: UUID, input: PaymentInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.save_payment(identity, academy_id, input, payment_id)
@app.delete("/api/academies/{academy_id}/payments/{payment_id}", tags=["finance"], status_code=204)
async def delete_payment(academy_id: UUID, payment_id: UUID, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): await app_service.delete_payment(identity, academy_id, payment_id); return Response(status_code=204)
@app.get("/api/academies/{academy_id}/refunds", tags=["finance"], response_model=list[RefundDto])
async def refunds(academy_id: UUID, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.refunds(identity, academy_id)
@app.post("/api/academies/{academy_id}/payments/{payment_id}/refunds", tags=["finance"], status_code=201, response_model=RefundDto)
async def create_refund(academy_id: UUID, payment_id: UUID, input: RefundInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.create_refund(identity, academy_id, payment_id, input)
@app.get("/api/academies/{academy_id}/expenses", tags=["finance"], response_model=list[ExpenseDto])
async def expenses(academy_id: UUID, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.expenses(identity, academy_id)
@app.post("/api/academies/{academy_id}/expenses", tags=["finance"], status_code=201, response_model=ExpenseDto)
async def create_expense(academy_id: UUID, input: ExpenseInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.save_expense(identity, academy_id, input)
@app.put("/api/academies/{academy_id}/expenses/{expense_id}", tags=["finance"], response_model=ExpenseDto)
async def update_expense(academy_id: UUID, expense_id: UUID, input: ExpenseInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.save_expense(identity, academy_id, input, expense_id)
@app.delete("/api/academies/{academy_id}/expenses/{expense_id}", tags=["finance"], status_code=204)
async def delete_expense(academy_id: UUID, expense_id: UUID, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): await app_service.delete_expense(identity, academy_id, expense_id); return Response(status_code=204)
@app.get("/api/academies/{academy_id}/finance-summary", tags=["finance"], response_model=FinanceSummaryDto)
async def finance_summary(academy_id: UUID, start: date, end: date, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.finance_summary(identity, academy_id, start, end)
@app.post("/api/academies/{academy_id}/guardian-links", tags=["attendance"], status_code=204)
async def guardian_link(academy_id: UUID, input: GuardianLinkInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): await app_service.link_guardian(identity, academy_id, input); return Response(status_code=204)
@app.get("/api/academies/{academy_id}/sessions", tags=["attendance"], response_model=list[SessionDto])
async def sessions(academy_id: UUID, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.sessions(identity, academy_id)
@app.post("/api/academies/{academy_id}/sessions", tags=["attendance"], status_code=201, response_model=SessionDto)
async def create_session(academy_id: UUID, input: SessionInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.create_session(identity, academy_id, input)
@app.post("/api/academies/{academy_id}/sessions/{session_id}/roster", tags=["attendance"], status_code=204)
async def add_roster(academy_id: UUID, session_id: UUID, input: RosterInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): await app_service.add_roster(identity, academy_id, session_id, input.athleteId); return Response(status_code=204)
@app.put("/api/academies/{academy_id}/sessions/{session_id}/attendance/{athlete_id}", tags=["attendance"], response_model=AttendanceDto)
async def mark_attendance(academy_id: UUID, session_id: UUID, athlete_id: UUID, input: AttendanceInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.mark_attendance(identity, academy_id, session_id, athlete_id, input, "MANUAL")
@app.post("/api/academies/{academy_id}/attendance-qr", tags=["attendance"], response_model=QrDto)
async def create_qr(academy_id: UUID, input: QrInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.create_qr(identity, academy_id, input)
@app.post("/api/attendance-qr/redeem", tags=["attendance"], response_model=AttendanceDto)
async def redeem_qr(input: RedeemQrInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.redeem_qr(identity, input)
@app.get("/api/health", tags=["health"])
async def health(): return {"status": "ok"}
