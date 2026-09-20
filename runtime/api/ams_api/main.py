import os
from contextlib import asynccontextmanager
from uuid import UUID, uuid4
from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException
from .auth import AuthService, DEMO_PROFILES, Identity, actor
from .database import Database
from .errors import ApiError, api_error, body, http_error, unexpected_error, validation_error
from .schemas import *
from .service import AcademyService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Refuse traffic before verifying that the request role cannot bypass tenant RLS.
    app.state.db = Database(); await app.state.db.verify_runtime_role()
    app.state.auth = AuthService(); app.state.service = AcademyService(app.state.db)
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
    try:
        response = await call_next(request)
    except IntegrityError:
        # Constraint failures are safe conflicts; database details stay private.
        response = body(409, "This change is not allowed in the current state.", request)
    response.headers.update({"X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY", "Referrer-Policy": "no-referrer"})
    return response

def service(request: Request) -> AcademyService: return request.app.state.service

@app.get("/api/auth/config", tags=["authentication"], response_model=AuthConfigDto)
async def auth_config(request: Request): return {"demo": request.app.state.auth.demo, "profiles": DEMO_PROFILES if request.app.state.auth.demo else []}
@app.post("/api/auth/demo", tags=["authentication"], response_model=TokenDto)
async def demo(input: DemoInput, request: Request): return {"accessToken": request.app.state.auth.issue_demo(input.userId)}
@app.get("/api/me", tags=["workspaces"], response_model=MeDto)
async def me(identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.me(identity)
@app.post("/api/invitations/accept", tags=["workspaces"], response_model=AcceptDto)
async def accept(input: AcceptInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.accept(identity, input.token)
@app.get("/api/platform/academies", tags=["platform"], response_model=list[AcademyDto])
async def academies(identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.academies(identity)
@app.post("/api/platform/academies", tags=["platform"], status_code=201, response_model=AcademyCreatedDto)
async def create_academy(input: AcademyInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.create_academy(identity, input)
@app.patch("/api/platform/academies/{academy_id}", tags=["platform"], response_model=AcademyDto)
async def set_active(academy_id: UUID, input: ActiveInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.set_active(identity, academy_id, input.active)
@app.get("/api/academies/{academy_id}/dashboard", tags=["academy"], response_model=DashboardDto)
async def dashboard(academy_id: UUID, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.dashboard(identity, academy_id)
@app.get("/api/academies/{academy_id}/branches", tags=["academy"], response_model=list[BranchDto])
async def branches(academy_id: UUID, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.branches(identity, academy_id)
@app.post("/api/academies/{academy_id}/branches", tags=["academy"], status_code=201, response_model=BranchDto)
async def create_branch(academy_id: UUID, input: BranchInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.create_branch(identity, academy_id, input)
@app.post("/api/academies/{academy_id}/branches/{branch_id}/tables", tags=["academy"], status_code=201, response_model=TableDto)
async def create_table(academy_id: UUID, branch_id: UUID, input: TableInput, identity: Identity = Depends(actor), app_service: AcademyService = Depends(service)): return await app_service.create_table(identity, academy_id, branch_id, input.name)
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
