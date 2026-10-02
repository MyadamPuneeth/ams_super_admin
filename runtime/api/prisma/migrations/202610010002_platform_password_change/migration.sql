CREATE FUNCTION app_private.change_platform_password(owner_id uuid, password_hash text)
RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
BEGIN
  IF app_private.actor() IS DISTINCT FROM owner_id THEN RAISE EXCEPTION 'Authentication required'; END IF;
  UPDATE public."PlatformOwner" SET "passwordHash"=password_hash, "failedLoginCount"=0, "lockedUntil"=NULL
  WHERE "userId"=owner_id AND active AND username IS NOT NULL;
  IF NOT FOUND THEN RAISE EXCEPTION 'Account unavailable'; END IF;
END
$$;
GRANT EXECUTE ON FUNCTION app_private.change_platform_password(uuid, text) TO ams_app;

CREATE FUNCTION app_private.coach_athlete_visible(a uuid, athlete uuid) RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = '' AS $$
  SELECT EXISTS (
    SELECT 1 FROM public."Membership" m
    JOIN public."Coach" c ON c."membershipId"=m.id AND c."academyId"=a AND c.active
    JOIN public."BatchCoach" bc ON bc."coachId"=c.id
    JOIN public."BatchAthlete" ba ON ba."batchId"=bc."batchId"
    WHERE m."userId"=app_private.actor() AND m."academyId"=a AND m.active
      AND 'COACH'=ANY(m.roles) AND ba."athleteId"=athlete
  )
$$;
CREATE OR REPLACE FUNCTION app_private.athlete_visible(a uuid, athlete uuid) RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = '' AS $$
  SELECT app_private.is_admin(a) OR app_private.coach_athlete_visible(a, athlete)
    OR EXISTS (SELECT 1 FROM public."Athlete" x JOIN public."Membership" m ON m.id=x."membershipId" WHERE x.id=athlete AND m."userId"=app_private.actor())
    OR EXISTS (SELECT 1 FROM public."GuardianAthlete" g JOIN public."Membership" m ON m.id=g."guardianMembershipId" WHERE g."athleteId"=athlete AND m."userId"=app_private.actor())
$$;
GRANT EXECUTE ON FUNCTION app_private.coach_athlete_visible(uuid,uuid) TO ams_app;
