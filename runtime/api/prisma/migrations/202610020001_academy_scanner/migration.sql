ALTER TABLE "AthleteDailyAttendance" ADD COLUMN "checkedAt" TIMESTAMPTZ;
CREATE FUNCTION app_private.active_check_in_member(user_id uuid) RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER SET search_path='' AS $$
  SELECT EXISTS (SELECT 1 FROM public."UserCredential" WHERE "userId"=$1 AND active)
$$;
REVOKE ALL ON FUNCTION app_private.active_check_in_member(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION app_private.active_check_in_member(uuid) TO ams_app;
