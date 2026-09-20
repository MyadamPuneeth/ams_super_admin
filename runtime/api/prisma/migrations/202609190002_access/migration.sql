CREATE SCHEMA app_private;
REVOKE ALL ON SCHEMA app_private FROM PUBLIC;
GRANT USAGE ON SCHEMA public, app_private TO ams_app;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

CREATE FUNCTION app_private.actor() RETURNS uuid LANGUAGE sql STABLE AS $$
  SELECT nullif(current_setting('app.actor', true), '')::uuid
$$;
CREATE FUNCTION app_private.academy() RETURNS uuid LANGUAGE sql STABLE AS $$
  SELECT nullif(current_setting('app.academy', true), '')::uuid
$$;
CREATE FUNCTION app_private.is_platform_owner() RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = '' AS $$
  SELECT EXISTS (SELECT 1 FROM public."PlatformOwner" WHERE "userId" = app_private.actor())
$$;
CREATE FUNCTION app_private.is_member(a uuid) RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = '' AS $$
  SELECT EXISTS (SELECT 1 FROM public."Membership" m JOIN public."Academy" a ON a.id = m."academyId"
    WHERE m."academyId" = $1 AND m."userId" = app_private.actor() AND m.active AND a.active)
$$;
CREATE FUNCTION app_private.is_admin(a uuid) RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = '' AS $$
  SELECT EXISTS (SELECT 1 FROM public."Membership" m JOIN public."Academy" a ON a.id = m."academyId"
    WHERE m."academyId" = $1 AND m."userId" = app_private.actor() AND m.active AND a.active AND 'ADMIN' = ANY(m.roles))
$$;
CREATE FUNCTION app_private.own_membership(m uuid) RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = '' AS $$
  SELECT EXISTS (SELECT 1 FROM public."Membership" WHERE id = $1 AND "userId" = app_private.actor())
$$;
CREATE FUNCTION app_private.branch_allowed(a uuid, b uuid) RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = '' AS $$
  SELECT EXISTS (SELECT 1 FROM public."Membership" m JOIN public."Academy" a ON a.id = m."academyId"
    WHERE m."academyId" = $1 AND m."userId" = app_private.actor() AND m.active AND a.active
    AND (m."allBranches" OR EXISTS (SELECT 1 FROM public."MemberBranch" s WHERE s."membershipId" = m.id AND s."branchId" = $2 AND s."academyId" = $1)))
$$;

ALTER TABLE "Membership" ALTER COLUMN roles SET NOT NULL;
ALTER TABLE "Membership" ADD CONSTRAINT membership_roles_present CHECK (cardinality(roles) > 0);
ALTER TABLE "Membership" ADD CONSTRAINT admin_all_branches CHECK (NOT ('ADMIN' = ANY(roles)) OR "allBranches");
ALTER TABLE "Invitation" ALTER COLUMN roles SET NOT NULL;
ALTER TABLE "Invitation" ALTER COLUMN "branchIds" SET NOT NULL;
ALTER TABLE "Invitation" ADD CONSTRAINT invitation_roles_present CHECK (cardinality(roles) > 0);
ALTER TABLE "Invitation" ADD CONSTRAINT invitation_scope CHECK (("allBranches" AND cardinality("branchIds") = 0) OR (NOT "allBranches" AND cardinality("branchIds") > 0));
ALTER TABLE "Invitation" ADD CONSTRAINT invite_admin_all_branches CHECK (NOT ('ADMIN' = ANY(roles)) OR "allBranches");
CREATE INDEX membership_actor ON "Membership"("userId");
CREATE INDEX invitation_academy ON "Invitation"("academyId");
CREATE INDEX table_academy ON "TableResource"("academyId");

ALTER TABLE "Academy" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Branch" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "TableResource" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Membership" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "MemberBranch" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Invitation" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Audit" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "PlatformOwner" ENABLE ROW LEVEL SECURITY;

GRANT SELECT, INSERT, UPDATE ON "Academy" TO ams_app;
GRANT SELECT, INSERT ON "Branch", "TableResource" TO ams_app;
GRANT SELECT, UPDATE ON "Membership" TO ams_app;
GRANT SELECT, INSERT, DELETE ON "MemberBranch" TO ams_app;
GRANT SELECT, INSERT, UPDATE ON "Invitation" TO ams_app;
GRANT SELECT, INSERT ON "Audit" TO ams_app;

CREATE POLICY academy_read ON "Academy" FOR SELECT TO ams_app USING (app_private.is_platform_owner() OR app_private.is_member(id));
CREATE POLICY academy_create ON "Academy" FOR INSERT TO ams_app WITH CHECK (app_private.is_platform_owner());
-- Administrators need a row lock for serialized membership administration; API limits updates to platform owners.
CREATE POLICY academy_update ON "Academy" FOR UPDATE TO ams_app USING (app_private.is_platform_owner() OR (id = app_private.academy() AND app_private.is_admin(id))) WITH CHECK (app_private.is_platform_owner() OR (id = app_private.academy() AND app_private.is_admin(id)));
CREATE POLICY branch_read ON "Branch" FOR SELECT TO ams_app USING ("academyId" = app_private.academy() AND app_private.branch_allowed("academyId", id));
CREATE POLICY branch_create ON "Branch" FOR INSERT TO ams_app WITH CHECK ("academyId" = app_private.academy() AND app_private.is_admin("academyId"));
CREATE POLICY table_read ON "TableResource" FOR SELECT TO ams_app USING ("academyId" = app_private.academy() AND app_private.branch_allowed("academyId", "branchId"));
CREATE POLICY table_create ON "TableResource" FOR INSERT TO ams_app WITH CHECK ("academyId" = app_private.academy() AND app_private.is_admin("academyId"));
CREATE POLICY membership_read ON "Membership" FOR SELECT TO ams_app USING ("userId" = app_private.actor() OR ("academyId" = app_private.academy() AND app_private.is_admin("academyId")));
CREATE POLICY membership_update ON "Membership" FOR UPDATE TO ams_app USING ("academyId" = app_private.academy() AND app_private.is_admin("academyId")) WITH CHECK ("academyId" = app_private.academy());
CREATE POLICY scope_read ON "MemberBranch" FOR SELECT TO ams_app USING (app_private.own_membership("membershipId") OR ("academyId" = app_private.academy() AND app_private.is_admin("academyId")));
CREATE POLICY scope_insert ON "MemberBranch" FOR INSERT TO ams_app WITH CHECK ("academyId" = app_private.academy() AND app_private.is_admin("academyId"));
CREATE POLICY scope_delete ON "MemberBranch" FOR DELETE TO ams_app USING ("academyId" = app_private.academy() AND app_private.is_admin("academyId"));
CREATE POLICY invite_read ON "Invitation" FOR SELECT TO ams_app USING ("academyId" = app_private.academy() AND (app_private.is_admin("academyId") OR app_private.is_platform_owner()));
CREATE POLICY invite_create ON "Invitation" FOR INSERT TO ams_app WITH CHECK ("academyId" = app_private.academy() AND (app_private.is_admin("academyId") OR (app_private.is_platform_owner() AND roles = ARRAY['ADMIN']::public."Role"[])));
CREATE POLICY invite_update ON "Invitation" FOR UPDATE TO ams_app USING ("academyId" = app_private.academy() AND (app_private.is_admin("academyId") OR app_private.is_platform_owner())) WITH CHECK ("academyId" = app_private.academy());
CREATE POLICY audit_read ON "Audit" FOR SELECT TO ams_app USING ("academyId" = app_private.academy() AND app_private.is_admin("academyId"));
CREATE POLICY audit_append ON "Audit" FOR INSERT TO ams_app WITH CHECK ("academyId" = app_private.academy() AND "actorId" = app_private.actor() AND (app_private.is_admin("academyId") OR app_private.is_platform_owner()));

CREATE FUNCTION app_private.accept_invitation(token_hash text, display_name text) RETURNS uuid
LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
DECLARE invite public."Invitation"; member_id uuid; target_academy uuid;
BEGIN
  IF app_private.actor() IS NULL THEN RAISE EXCEPTION 'Authentication required'; END IF;
  SELECT "academyId" INTO target_academy FROM public."Invitation" WHERE "tokenHash" = token_hash;
  IF target_academy IS NULL THEN RAISE EXCEPTION 'Invitation unavailable'; END IF;
  PERFORM id FROM public."Academy" WHERE id = target_academy AND active FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'Academy unavailable'; END IF;
  SELECT * INTO invite FROM public."Invitation" WHERE "tokenHash" = token_hash FOR UPDATE;
  IF invite."acceptedAt" IS NOT NULL OR invite."expiresAt" <= now() OR invite.email <> lower(current_setting('app.email', true)) THEN
    RAISE EXCEPTION 'Invitation unavailable for this account';
  END IF;
  IF EXISTS (SELECT 1 FROM public."Membership" WHERE "academyId" = invite."academyId" AND "userId" = app_private.actor() AND active) THEN
    RAISE EXCEPTION 'Already a member';
  END IF;
  IF (SELECT count(*) FROM public."Branch" WHERE "academyId" = invite."academyId" AND id = ANY(invite."branchIds")) <> cardinality(invite."branchIds") THEN
    RAISE EXCEPTION 'Invitation branches unavailable';
  END IF;
  INSERT INTO public."Membership"(id, "academyId", "userId", email, name, roles, "allBranches")
    VALUES(gen_random_uuid(), invite."academyId", app_private.actor(), invite.email, left(display_name, 100), invite.roles, invite."allBranches")
    ON CONFLICT ("academyId", "userId") DO UPDATE SET roles = EXCLUDED.roles, "allBranches" = EXCLUDED."allBranches", active = true, name = EXCLUDED.name, email = EXCLUDED.email
    RETURNING id INTO member_id;
  DELETE FROM public."MemberBranch" WHERE "membershipId" = member_id;
  INSERT INTO public."MemberBranch"("academyId", "membershipId", "branchId") SELECT invite."academyId", member_id, unnest(invite."branchIds");
  UPDATE public."Invitation" SET "acceptedAt" = now() WHERE id = invite.id;
  INSERT INTO public."Audit"(id, "academyId", "actorId", action, detail) VALUES(gen_random_uuid(), invite."academyId", app_private.actor(), 'invitation.accepted', 'Joined academy via invitation');
  RETURN invite."academyId";
END
$$;

REVOKE ALL ON ALL FUNCTIONS IN SCHEMA app_private FROM PUBLIC;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA app_private TO ams_app;
