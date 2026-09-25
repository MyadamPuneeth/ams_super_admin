CREATE TYPE "SubscriptionPlan" AS ENUM ('STARTER', 'PRO', 'ENTERPRISE');
CREATE TYPE "SubscriptionStatus" AS ENUM ('TRIAL', 'ACTIVE', 'PAST_DUE', 'CANCELLED', 'EXPIRED');

ALTER TABLE "Academy"
  ADD COLUMN "subscriptionPlan" "SubscriptionPlan" NOT NULL DEFAULT 'STARTER',
  ADD COLUMN "subscriptionStatus" "SubscriptionStatus" NOT NULL DEFAULT 'ACTIVE',
  ADD COLUMN "subscriptionStartsOn" DATE DEFAULT CURRENT_DATE,
  ADD COLUMN "subscriptionEndsOn" DATE,
  ADD CONSTRAINT academy_subscription_dates CHECK ("subscriptionEndsOn" IS NULL OR "subscriptionEndsOn" >= "subscriptionStartsOn");
UPDATE "Academy" SET "subscriptionStartsOn" = "createdAt"::date;
ALTER TABLE "Academy" ALTER COLUMN "subscriptionStartsOn" SET NOT NULL;

ALTER TABLE "PlatformOwner"
  ADD COLUMN username TEXT,
  ADD COLUMN "passwordHash" TEXT,
  ADD COLUMN name TEXT,
  ADD COLUMN active BOOLEAN NOT NULL DEFAULT true,
  ADD COLUMN "failedLoginCount" INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN "lockedUntil" TIMESTAMPTZ,
  ADD CONSTRAINT platform_owner_username CHECK (username IS NULL OR username ~ '^[a-z0-9._-]{3,50}$'),
  ADD CONSTRAINT platform_owner_failed_login_count CHECK ("failedLoginCount" >= 0);
CREATE UNIQUE INDEX platform_owner_username_key ON "PlatformOwner" (username) WHERE username IS NOT NULL;

CREATE FUNCTION app_private.platform_owner_credential(login text)
RETURNS TABLE("userId" uuid, "passwordHash" text, name text, active boolean, "lockedUntil" timestamptz)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = '' AS $$
  SELECT p."userId", p."passwordHash", p.name, p.active, p."lockedUntil"
  FROM public."PlatformOwner" p
  WHERE p.username = lower(login) AND p.username IS NOT NULL
$$;

CREATE FUNCTION app_private.record_platform_login(owner_id uuid, succeeded boolean)
RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
DECLARE failures integer;
BEGIN
  IF succeeded THEN
    UPDATE public."PlatformOwner" SET "failedLoginCount" = 0, "lockedUntil" = NULL WHERE "userId" = owner_id;
    RETURN;
  END IF;
  UPDATE public."PlatformOwner"
  SET "failedLoginCount" = CASE WHEN "lockedUntil" IS NULL OR "lockedUntil" <= now() THEN "failedLoginCount" + 1 ELSE "failedLoginCount" END
  WHERE "userId" = owner_id
  RETURNING "failedLoginCount" INTO failures;
  IF failures >= 5 THEN
    UPDATE public."PlatformOwner" SET "failedLoginCount" = 0, "lockedUntil" = now() + interval '15 minutes' WHERE "userId" = owner_id;
  END IF;
END
$$;

CREATE OR REPLACE FUNCTION app_private.is_platform_owner() RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = '' AS $$
  SELECT EXISTS (SELECT 1 FROM public."PlatformOwner" WHERE "userId" = app_private.actor() AND active)
$$;

GRANT EXECUTE ON FUNCTION app_private.platform_owner_credential(text) TO ams_app;
GRANT EXECUTE ON FUNCTION app_private.record_platform_login(uuid, boolean) TO ams_app;
