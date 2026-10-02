CREATE TABLE "MobileDeviceSession" (
  "tokenHash" TEXT PRIMARY KEY, "userId" UUID NOT NULL REFERENCES "UserCredential"("userId") ON DELETE CASCADE,
  "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(), "lastUsedAt" TIMESTAMPTZ NOT NULL DEFAULT now(), "revokedAt" TIMESTAMPTZ
);
CREATE INDEX mobile_device_session_user ON "MobileDeviceSession"("userId") WHERE "revokedAt" IS NULL;
ALTER TABLE "MobileDeviceSession" ENABLE ROW LEVEL SECURITY;

CREATE FUNCTION app_private.create_mobile_session(user_id uuid, token_hash text) RETURNS void
LANGUAGE plpgsql SECURITY DEFINER SET search_path='' AS $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM public."UserCredential" u JOIN public."Membership" m ON m."userId"=u."userId" JOIN public."Academy" a ON a.id=m."academyId" WHERE u."userId"=user_id AND u.active AND m.active AND a.active) THEN RAISE EXCEPTION 'Account unavailable'; END IF;
  INSERT INTO public."MobileDeviceSession"("tokenHash","userId") VALUES(token_hash,user_id);
END $$;
CREATE FUNCTION app_private.mobile_session(token_hash text)
RETURNS TABLE("userId" uuid,name text,email text,username text,"passwordChangeRequired" boolean)
LANGUAGE plpgsql SECURITY DEFINER SET search_path='' AS $$
BEGIN
  UPDATE public."MobileDeviceSession" s SET "lastUsedAt"=now()
  FROM public."UserCredential" u WHERE s."tokenHash"=token_hash AND s."userId"=u."userId"
    AND s."revokedAt" IS NULL AND u.active;
  RETURN QUERY SELECT u."userId",u.name,u.email,u.username,u."passwordChangeRequired"
  FROM public."MobileDeviceSession" s JOIN public."UserCredential" u ON u."userId"=s."userId"
  WHERE s."tokenHash"=token_hash AND s."revokedAt" IS NULL AND u.active
    AND EXISTS (SELECT 1 FROM public."Membership" m JOIN public."Academy" a ON a.id=m."academyId"
      WHERE m."userId"=u."userId" AND m.active AND a.active);
END $$;
CREATE FUNCTION app_private.revoke_mobile_session(token_hash text) RETURNS void
LANGUAGE sql SECURITY DEFINER SET search_path='' AS $$
  UPDATE public."MobileDeviceSession" SET "revokedAt"=now() WHERE "tokenHash"=token_hash AND "revokedAt" IS NULL
$$;
CREATE FUNCTION app_private.revoke_user_mobile_sessions(user_id uuid) RETURNS void
LANGUAGE plpgsql SECURITY DEFINER SET search_path='' AS $$
BEGIN
  IF app_private.actor() IS DISTINCT FROM user_id AND NOT EXISTS (
    SELECT 1 FROM public."Membership" m WHERE m."userId"=user_id AND app_private.is_admin(m."academyId")
  ) AND NOT app_private.is_platform_owner() THEN RAISE EXCEPTION 'Not authorized'; END IF;
  UPDATE public."MobileDeviceSession" SET "revokedAt"=now() WHERE "userId"=user_id AND "revokedAt" IS NULL;
END $$;
GRANT EXECUTE ON FUNCTION app_private.create_mobile_session(uuid,text),app_private.mobile_session(text),app_private.revoke_mobile_session(text),app_private.revoke_user_mobile_sessions(uuid) TO ams_app;

CREATE FUNCTION app_private.revoke_mobile_on_password_change() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path='' AS $$
BEGIN
  IF NEW."passwordHash" IS DISTINCT FROM OLD."passwordHash" OR (OLD.active AND NOT NEW.active) THEN
    UPDATE public."MobileDeviceSession" SET "revokedAt"=now() WHERE "userId"=NEW."userId" AND "revokedAt" IS NULL;
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER user_credential_mobile_revoke AFTER UPDATE ON "UserCredential" FOR EACH ROW EXECUTE FUNCTION app_private.revoke_mobile_on_password_change();
CREATE FUNCTION app_private.revoke_mobile_on_membership_deactivation() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path='' AS $$
BEGIN
  IF OLD.active AND NOT NEW.active THEN UPDATE public."MobileDeviceSession" SET "revokedAt"=now() WHERE "userId"=NEW."userId" AND "revokedAt" IS NULL; END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER membership_mobile_revoke AFTER UPDATE ON "Membership" FOR EACH ROW EXECUTE FUNCTION app_private.revoke_mobile_on_membership_deactivation();

ALTER TABLE "Coach" ADD COLUMN "membershipId" UUID UNIQUE,
  ADD CONSTRAINT coach_membership_fk FOREIGN KEY ("academyId","membershipId") REFERENCES "Membership"("academyId",id);
ALTER TABLE "Batch" ADD COLUMN "historyFrom" DATE;
UPDATE "Batch" SET "historyFrom"="startsOn";
ALTER TABLE "Batch" ALTER COLUMN "historyFrom" SET NOT NULL;
ALTER TABLE "BatchAthlete" ADD COLUMN "assignedOn" DATE;
UPDATE "BatchAthlete" ba SET "assignedOn"=b."startsOn" FROM "Batch" b WHERE b.id=ba."batchId";
ALTER TABLE "BatchAthlete" ALTER COLUMN "assignedOn" SET NOT NULL;
CREATE TABLE "StaffWorkdayRule" (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), "academyId" UUID NOT NULL, "membershipId" UUID NOT NULL,
  "effectiveOn" DATE NOT NULL, weekdays SMALLINT[] NOT NULL, "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE ("academyId","membershipId","effectiveOn"),
  FOREIGN KEY ("academyId","membershipId") REFERENCES "Membership"("academyId",id),
  CHECK (weekdays <@ ARRAY[0,1,2,3,4,5,6]::smallint[])
);
ALTER TABLE "StaffWorkdayRule" ENABLE ROW LEVEL SECURITY;
GRANT SELECT,INSERT,UPDATE ON "StaffWorkdayRule" TO ams_app;
CREATE POLICY staff_workday_read ON "StaffWorkdayRule" FOR SELECT TO ams_app USING (app_private.own_member("membershipId") OR app_private.is_admin("academyId"));
CREATE POLICY staff_workday_write ON "StaffWorkdayRule" FOR INSERT TO ams_app WITH CHECK (app_private.is_admin("academyId"));
CREATE POLICY staff_workday_update ON "StaffWorkdayRule" FOR UPDATE TO ams_app USING (app_private.is_admin("academyId")) WITH CHECK (app_private.is_admin("academyId"));

CREATE TABLE "AthleteBatchOpportunity" (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), "academyId" UUID NOT NULL, "batchId" UUID,
  "athleteId" UUID NOT NULL, "localDate" DATE NOT NULL, "startTime" TIME NOT NULL,
  "batchName" TEXT NOT NULL, "branchId" UUID NOT NULL, status "AttendanceStatus", source TEXT,
  "updatedAt" TIMESTAMPTZ NOT NULL DEFAULT now(), UNIQUE ("batchId","athleteId","localDate"),
  FOREIGN KEY ("academyId","athleteId") REFERENCES "Athlete"("academyId",id),
  FOREIGN KEY ("academyId","branchId") REFERENCES "Branch"("academyId",id),
  FOREIGN KEY ("academyId","batchId") REFERENCES "Batch"("academyId",id) ON DELETE SET NULL ("batchId")
);
ALTER TABLE "AthleteBatchOpportunity" ENABLE ROW LEVEL SECURITY;
GRANT SELECT,INSERT,UPDATE ON "AthleteBatchOpportunity" TO ams_app;
CREATE POLICY athlete_batch_read ON "AthleteBatchOpportunity" FOR SELECT TO ams_app USING (app_private.athlete_visible("academyId","athleteId"));
CREATE POLICY athlete_batch_write ON "AthleteBatchOpportunity" FOR ALL TO ams_app USING (app_private.is_admin("academyId") OR app_private.athlete_visible("academyId","athleteId")) WITH CHECK (app_private.is_admin("academyId") OR app_private.athlete_visible("academyId","athleteId"));

ALTER TABLE "AttendanceQr" ADD COLUMN "batchId" UUID,
  ADD CONSTRAINT qr_batch_fk FOREIGN KEY ("academyId","batchId") REFERENCES "Batch"("academyId",id),
  DROP CONSTRAINT "AttendanceQr_check";
ALTER TABLE "AttendanceQr" ADD CONSTRAINT qr_kind_target CHECK (
  (kind='SESSION' AND "sessionId" IS NOT NULL AND "batchId" IS NULL) OR
  (kind='STAFF' AND "sessionId" IS NULL AND "batchId" IS NULL) OR
  (kind='BATCH' AND "sessionId" IS NULL AND "batchId" IS NOT NULL));
CREATE POLICY qr_batch_coach ON "AttendanceQr" FOR ALL TO ams_app USING (
  kind='BATCH' AND EXISTS (SELECT 1 FROM "BatchCoach" bc JOIN "Coach" c ON c.id=bc."coachId" JOIN "Membership" m ON m.id=c."membershipId" WHERE bc."batchId"="AttendanceQr"."batchId" AND m."userId"=app_private.actor() AND m.active)
) WITH CHECK (
  kind='BATCH' AND EXISTS (SELECT 1 FROM "BatchCoach" bc JOIN "Coach" c ON c.id=bc."coachId" JOIN "Membership" m ON m.id=c."membershipId" WHERE bc."batchId"="AttendanceQr"."batchId" AND m."userId"=app_private.actor() AND m.active)
);
CREATE POLICY qr_member_preview ON "AttendanceQr" FOR SELECT TO ams_app USING (app_private.is_member("academyId"));

CREATE FUNCTION app_private.provision_mobile_account(academy_id uuid, person_type text, person_id uuid,
  new_user uuid, login text, password_hash text, display_name text, contact_email text)
RETURNS uuid LANGUAGE plpgsql SECURITY DEFINER SET search_path='' AS $$
DECLARE new_member uuid;
BEGIN
  IF NOT app_private.is_admin(academy_id) OR academy_id IS DISTINCT FROM app_private.academy() THEN RAISE EXCEPTION 'Administrator access required'; END IF;
  IF person_type NOT IN ('ATHLETE','COACH','STAFF') THEN RAISE EXCEPTION 'Invalid account type'; END IF;
  IF person_type='ATHLETE' AND NOT EXISTS (SELECT 1 FROM public."Athlete" WHERE id=person_id AND "academyId"=academy_id AND active AND "membershipId" IS NULL) THEN RAISE EXCEPTION 'Athlete unavailable'; END IF;
  IF person_type='COACH' AND NOT EXISTS (SELECT 1 FROM public."Coach" WHERE id=person_id AND "academyId"=academy_id AND active AND "membershipId" IS NULL) THEN RAISE EXCEPTION 'Coach unavailable'; END IF;
  INSERT INTO public."UserCredential"("userId",username,"passwordHash",name,email) VALUES(new_user,login,password_hash,display_name,contact_email);
  INSERT INTO public."Membership"(id,"academyId","userId",email,name,roles,"allBranches")
  VALUES(gen_random_uuid(),academy_id,new_user,contact_email,display_name,
    CASE person_type WHEN 'ATHLETE' THEN ARRAY['ATHLETE']::public."Role"[] WHEN 'COACH' THEN ARRAY['COACH']::public."Role"[] ELSE ARRAY['SCORER']::public."Role"[] END,true)
  RETURNING id INTO new_member;
  IF person_type='ATHLETE' THEN UPDATE public."Athlete" SET "membershipId"=new_member WHERE id=person_id AND "academyId"=academy_id;
  ELSIF person_type='COACH' THEN UPDATE public."Coach" SET "membershipId"=new_member WHERE id=person_id AND "academyId"=academy_id; END IF;
  RETURN new_member;
END $$;
GRANT EXECUTE ON FUNCTION app_private.provision_mobile_account(uuid,text,uuid,uuid,text,text,text,text) TO ams_app;
CREATE FUNCTION app_private.reset_mobile_password(academy_id uuid, member_id uuid, password_hash text) RETURNS void
LANGUAGE plpgsql SECURITY DEFINER SET search_path='' AS $$
DECLARE target_user uuid;
BEGIN
  IF NOT app_private.is_admin(academy_id) OR academy_id IS DISTINCT FROM app_private.academy() THEN RAISE EXCEPTION 'Administrator access required'; END IF;
  SELECT "userId" INTO target_user FROM public."Membership" WHERE id=member_id AND "academyId"=academy_id AND active;
  IF target_user IS NULL THEN RAISE EXCEPTION 'Account unavailable'; END IF;
  UPDATE public."UserCredential" SET "passwordHash"=password_hash,"passwordChangeRequired"=true,
    "failedLoginCount"=0,"lockedUntil"=NULL WHERE "userId"=target_user;
  IF NOT FOUND THEN RAISE EXCEPTION 'Account unavailable'; END IF;
END $$;
GRANT EXECUTE ON FUNCTION app_private.reset_mobile_password(uuid,uuid,text) TO ams_app;
