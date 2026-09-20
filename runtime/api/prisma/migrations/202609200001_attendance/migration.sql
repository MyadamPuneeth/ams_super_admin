CREATE TYPE "AttendanceStatus" AS ENUM ('PRESENT', 'ABSENT', 'EXCUSED');
CREATE TYPE "SessionStatus" AS ENUM ('SCHEDULED', 'OPEN', 'CLOSED', 'CANCELLED');
CREATE TYPE "QrKind" AS ENUM ('SESSION', 'STAFF');

CREATE TABLE "Athlete" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(), "academyId" UUID NOT NULL, "membershipId" UUID,
  "name" TEXT NOT NULL, "active" BOOLEAN NOT NULL DEFAULT true, "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE ("academyId", "id"), UNIQUE ("membershipId"),
  FOREIGN KEY ("academyId") REFERENCES "Academy"(id) ON DELETE RESTRICT,
  FOREIGN KEY ("academyId", "membershipId") REFERENCES "Membership"("academyId", id) ON DELETE RESTRICT
);
CREATE TABLE "GuardianAthlete" (
  "academyId" UUID NOT NULL, "guardianMembershipId" UUID NOT NULL, "athleteId" UUID NOT NULL,
  PRIMARY KEY ("guardianMembershipId", "athleteId"),
  FOREIGN KEY ("academyId", "guardianMembershipId") REFERENCES "Membership"("academyId", id) ON DELETE RESTRICT,
  FOREIGN KEY ("academyId", "athleteId") REFERENCES "Athlete"("academyId", id) ON DELETE RESTRICT
);
CREATE TABLE "TrainingSession" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(), "academyId" UUID NOT NULL, "branchId" UUID NOT NULL,
  "coachMembershipId" UUID, title TEXT NOT NULL, "startsAt" TIMESTAMPTZ NOT NULL, "endsAt" TIMESTAMPTZ NOT NULL,
  status "SessionStatus" NOT NULL DEFAULT 'SCHEDULED', "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE ("academyId", "id"), CHECK ("endsAt" > "startsAt"),
  FOREIGN KEY ("academyId", "branchId") REFERENCES "Branch"("academyId", id) ON DELETE RESTRICT,
  FOREIGN KEY ("academyId", "coachMembershipId") REFERENCES "Membership"("academyId", id) ON DELETE RESTRICT
);
CREATE TABLE "SessionRoster" (
  "academyId" UUID NOT NULL, "sessionId" UUID NOT NULL, "athleteId" UUID NOT NULL,
  PRIMARY KEY ("sessionId", "athleteId"),
  FOREIGN KEY ("academyId", "sessionId") REFERENCES "TrainingSession"("academyId", id) ON DELETE RESTRICT,
  FOREIGN KEY ("academyId", "athleteId") REFERENCES "Athlete"("academyId", id) ON DELETE RESTRICT
);
CREATE TABLE "AthleteAttendance" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(), "academyId" UUID NOT NULL, "sessionId" UUID NOT NULL, "athleteId" UUID NOT NULL,
  status "AttendanceStatus" NOT NULL, source TEXT NOT NULL, "checkedAt" TIMESTAMPTZ NOT NULL DEFAULT now(), "actorId" UUID NOT NULL,
  "correctionReason" TEXT, "updatedAt" TIMESTAMPTZ NOT NULL DEFAULT now(), UNIQUE ("sessionId", "athleteId"),
  FOREIGN KEY ("academyId", "sessionId") REFERENCES "TrainingSession"("academyId", id) ON DELETE RESTRICT,
  FOREIGN KEY ("academyId", "athleteId") REFERENCES "Athlete"("academyId", id) ON DELETE RESTRICT
);
CREATE TABLE "StaffAttendance" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(), "academyId" UUID NOT NULL, "membershipId" UUID NOT NULL, "branchId" UUID NOT NULL,
  "localDate" DATE NOT NULL, status "AttendanceStatus" NOT NULL DEFAULT 'PRESENT', source TEXT NOT NULL,
  "checkedAt" TIMESTAMPTZ NOT NULL DEFAULT now(), "actorId" UUID NOT NULL, "correctionReason" TEXT, "updatedAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE ("academyId", "membershipId", "localDate"),
  FOREIGN KEY ("academyId", "membershipId") REFERENCES "Membership"("academyId", id) ON DELETE RESTRICT,
  FOREIGN KEY ("academyId", "branchId") REFERENCES "Branch"("academyId", id) ON DELETE RESTRICT
);
CREATE TABLE "AttendanceQr" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(), "academyId" UUID NOT NULL, kind "QrKind" NOT NULL, "branchId" UUID NOT NULL,
  "sessionId" UUID, "tokenHash" TEXT NOT NULL UNIQUE, "expiresAt" TIMESTAMPTZ NOT NULL, closed BOOLEAN NOT NULL DEFAULT false,
  "createdBy" UUID NOT NULL, "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
  FOREIGN KEY ("academyId", "branchId") REFERENCES "Branch"("academyId", id) ON DELETE RESTRICT,
  FOREIGN KEY ("academyId", "sessionId") REFERENCES "TrainingSession"("academyId", id) ON DELETE RESTRICT,
  CHECK ((kind = 'SESSION' AND "sessionId" IS NOT NULL) OR (kind = 'STAFF' AND "sessionId" IS NULL))
);

CREATE INDEX "TrainingSession_academy_startsAt" ON "TrainingSession"("academyId", "startsAt");
CREATE INDEX "AthleteAttendance_session" ON "AthleteAttendance"("sessionId");
CREATE INDEX "AttendanceQr_token" ON "AttendanceQr"("tokenHash");

ALTER TABLE "Athlete" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "GuardianAthlete" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "TrainingSession" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "SessionRoster" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "AthleteAttendance" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "StaffAttendance" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "AttendanceQr" ENABLE ROW LEVEL SECURITY;
GRANT SELECT, INSERT, UPDATE ON "Athlete", "GuardianAthlete", "TrainingSession", "SessionRoster", "AthleteAttendance", "StaffAttendance", "AttendanceQr" TO ams_app;

CREATE FUNCTION app_private.own_member(m uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path = '' AS $$
  SELECT EXISTS (SELECT 1 FROM public."Membership" WHERE id=$1 AND "userId"=app_private.actor() AND active)
$$;
CREATE FUNCTION app_private.assigned_coach(a uuid, s uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path = '' AS $$
  SELECT app_private.is_admin(a) OR EXISTS (SELECT 1 FROM public."TrainingSession" t JOIN public."Membership" m ON m.id=t."coachMembershipId" WHERE t.id=s AND t."academyId"=a AND m."userId"=app_private.actor() AND m.active)
$$;
CREATE FUNCTION app_private.athlete_visible(a uuid, athlete uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path = '' AS $$
  SELECT app_private.is_admin(a) OR EXISTS (SELECT 1 FROM public."Athlete" x JOIN public."Membership" m ON m.id=x."membershipId" WHERE x.id=athlete AND m."userId"=app_private.actor()) OR EXISTS (SELECT 1 FROM public."GuardianAthlete" g JOIN public."Membership" m ON m.id=g."guardianMembershipId" WHERE g."athleteId"=athlete AND m."userId"=app_private.actor())
$$;
CREATE POLICY athlete_read ON "Athlete" FOR SELECT TO ams_app USING (app_private.athlete_visible("academyId", id) OR app_private.is_admin("academyId"));
CREATE POLICY athlete_write ON "Athlete" FOR ALL TO ams_app USING (app_private.is_admin("academyId")) WITH CHECK (app_private.is_admin("academyId"));
CREATE POLICY guardian_read ON "GuardianAthlete" FOR SELECT TO ams_app USING (app_private.athlete_visible("academyId", "athleteId"));
CREATE POLICY guardian_write ON "GuardianAthlete" FOR ALL TO ams_app USING (app_private.is_admin("academyId")) WITH CHECK (app_private.is_admin("academyId"));
CREATE POLICY session_read ON "TrainingSession" FOR SELECT TO ams_app USING (app_private.branch_allowed("academyId", "branchId"));
CREATE POLICY session_write ON "TrainingSession" FOR ALL TO ams_app USING (app_private.is_admin("academyId") OR app_private.assigned_coach("academyId", id)) WITH CHECK (app_private.is_admin("academyId"));
CREATE POLICY roster_read ON "SessionRoster" FOR SELECT TO ams_app USING (app_private.assigned_coach("academyId", "sessionId") OR app_private.athlete_visible("academyId", "athleteId"));
CREATE POLICY roster_write ON "SessionRoster" FOR ALL TO ams_app USING (app_private.assigned_coach("academyId", "sessionId")) WITH CHECK (app_private.assigned_coach("academyId", "sessionId"));
CREATE POLICY athlete_attendance_read ON "AthleteAttendance" FOR SELECT TO ams_app USING (app_private.assigned_coach("academyId", "sessionId") OR app_private.athlete_visible("academyId", "athleteId"));
CREATE POLICY athlete_attendance_write ON "AthleteAttendance" FOR ALL TO ams_app USING (app_private.assigned_coach("academyId", "sessionId") OR app_private.athlete_visible("academyId", "athleteId")) WITH CHECK (app_private.assigned_coach("academyId", "sessionId") OR app_private.athlete_visible("academyId", "athleteId"));
CREATE POLICY staff_attendance_read ON "StaffAttendance" FOR SELECT TO ams_app USING (app_private.is_admin("academyId") OR app_private.own_member("membershipId"));
CREATE POLICY staff_attendance_write ON "StaffAttendance" FOR ALL TO ams_app USING (app_private.is_admin("academyId") OR app_private.own_member("membershipId")) WITH CHECK (app_private.is_admin("academyId") OR app_private.own_member("membershipId"));
CREATE POLICY qr_read ON "AttendanceQr" FOR SELECT TO ams_app USING (app_private.is_admin("academyId") OR app_private.assigned_coach("academyId", "sessionId"));
CREATE POLICY qr_write ON "AttendanceQr" FOR ALL TO ams_app USING (app_private.is_admin("academyId") OR app_private.assigned_coach("academyId", "sessionId")) WITH CHECK (app_private.is_admin("academyId") OR app_private.assigned_coach("academyId", "sessionId"));
REVOKE ALL ON FUNCTION app_private.own_member(uuid), app_private.assigned_coach(uuid, uuid), app_private.athlete_visible(uuid, uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION app_private.own_member(uuid), app_private.assigned_coach(uuid, uuid), app_private.athlete_visible(uuid, uuid) TO ams_app;
