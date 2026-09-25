CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE "UserCredential" (
  "userId" UUID PRIMARY KEY,
  username TEXT NOT NULL,
  "passwordHash" TEXT NOT NULL,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  active BOOLEAN NOT NULL DEFAULT true,
  "passwordChangeRequired" BOOLEAN NOT NULL DEFAULT true,
  "failedLoginCount" INTEGER NOT NULL DEFAULT 0,
  "lockedUntil" TIMESTAMPTZ,
  "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT user_credential_username CHECK (username ~ '^[a-z0-9._-]{3,50}$'),
  CONSTRAINT user_credential_failed_count CHECK ("failedLoginCount" >= 0)
);
CREATE UNIQUE INDEX user_credential_username_key ON "UserCredential" (username);

CREATE TABLE "CredentialHandoff" (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "academyId" UUID NOT NULL REFERENCES "Academy"(id) ON DELETE RESTRICT,
  "userId" UUID NOT NULL REFERENCES "UserCredential"("userId") ON DELETE RESTRICT,
  username TEXT NOT NULL,
  email TEXT NOT NULL,
  "passwordCipher" BYTEA,
  "copiedAt" TIMESTAMPTZ,
  "emailSentAt" TIMESTAMPTZ,
  "emailError" TEXT,
  "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX credential_handoff_pending ON "CredentialHandoff" ("createdAt") WHERE "passwordCipher" IS NOT NULL;

ALTER TABLE "UserCredential" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "CredentialHandoff" ENABLE ROW LEVEL SECURITY;
GRANT INSERT ON "UserCredential" TO ams_app;
GRANT SELECT, INSERT, UPDATE ON "CredentialHandoff" TO ams_app;
GRANT INSERT ON "Membership" TO ams_app;

CREATE POLICY user_credential_create ON "UserCredential" FOR INSERT TO ams_app WITH CHECK (app_private.is_platform_owner());
CREATE POLICY handoff_platform_read ON "CredentialHandoff" FOR SELECT TO ams_app USING (app_private.is_platform_owner());
CREATE POLICY handoff_platform_create ON "CredentialHandoff" FOR INSERT TO ams_app WITH CHECK (app_private.is_platform_owner());
CREATE POLICY handoff_platform_update ON "CredentialHandoff" FOR UPDATE TO ams_app USING (app_private.is_platform_owner()) WITH CHECK (app_private.is_platform_owner());
CREATE POLICY membership_platform_create ON "Membership" FOR INSERT TO ams_app WITH CHECK ("academyId" = app_private.academy() AND app_private.is_platform_owner());

CREATE FUNCTION app_private.user_credential(login text)
RETURNS TABLE("userId" uuid, "passwordHash" text, name text, email text, active boolean, "passwordChangeRequired" boolean, "lockedUntil" timestamptz)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = '' AS $$
  SELECT u."userId", u."passwordHash", u.name, u.email, u.active, u."passwordChangeRequired", u."lockedUntil"
  FROM public."UserCredential" u WHERE u.username = lower(login)
$$;

CREATE FUNCTION app_private.record_user_login(user_id uuid, succeeded boolean)
RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
DECLARE failures integer;
BEGIN
  IF succeeded THEN
    UPDATE public."UserCredential" SET "failedLoginCount"=0, "lockedUntil"=NULL WHERE "userId"=user_id;
    RETURN;
  END IF;
  UPDATE public."UserCredential"
  SET "failedLoginCount"=CASE WHEN "lockedUntil" IS NULL OR "lockedUntil" <= now() THEN "failedLoginCount"+1 ELSE "failedLoginCount" END
  WHERE "userId"=user_id RETURNING "failedLoginCount" INTO failures;
  IF failures >= 5 THEN
    UPDATE public."UserCredential" SET "failedLoginCount"=0, "lockedUntil"=now()+interval '15 minutes' WHERE "userId"=user_id;
  END IF;
END
$$;

CREATE FUNCTION app_private.change_user_password(user_id uuid, password_hash text)
RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
BEGIN
  IF app_private.actor() IS DISTINCT FROM user_id THEN RAISE EXCEPTION 'Authentication required'; END IF;
  UPDATE public."UserCredential" SET "passwordHash"=password_hash, "passwordChangeRequired"=false, "failedLoginCount"=0, "lockedUntil"=NULL WHERE "userId"=user_id AND active;
  IF NOT FOUND THEN RAISE EXCEPTION 'Account unavailable'; END IF;
END
$$;

GRANT EXECUTE ON FUNCTION app_private.user_credential(text) TO ams_app;
GRANT EXECUTE ON FUNCTION app_private.record_user_login(uuid, boolean) TO ams_app;
GRANT EXECUTE ON FUNCTION app_private.change_user_password(uuid, text) TO ams_app;
