CREATE TYPE "BatchRecurrence" AS ENUM ('ONCE', 'WEEKLY');
CREATE TYPE "InvoiceStatus" AS ENUM ('DUE', 'PARTIAL', 'PAID', 'OVERDUE', 'VOID');
CREATE TYPE "PaymentKind" AS ENUM ('FEE', 'AD_HOC');
CREATE TYPE "PaymentMethod" AS ENUM ('CASH', 'UPI', 'CARD', 'BANK_TRANSFER', 'OTHER');

ALTER TABLE "Athlete" ADD COLUMN "homeBranchId" UUID, ADD COLUMN "monthlyFee" NUMERIC(12,2) NOT NULL DEFAULT 0,
  ADD CONSTRAINT athlete_monthly_fee_nonnegative CHECK ("monthlyFee" >= 0),
  ADD CONSTRAINT athlete_home_branch_fk FOREIGN KEY ("academyId", "homeBranchId") REFERENCES "Branch"("academyId", id) ON DELETE RESTRICT;
CREATE UNIQUE INDEX table_resource_academy_branch_id ON "TableResource"("academyId", "branchId", id);

CREATE TABLE "Coach" (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), "academyId" UUID NOT NULL REFERENCES "Academy"(id) ON DELETE RESTRICT,
  name TEXT NOT NULL, phone TEXT NOT NULL, email TEXT, notes TEXT, active BOOLEAN NOT NULL DEFAULT true,
  "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(), UNIQUE ("academyId", id)
);
CREATE TABLE "Batch" (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), "academyId" UUID NOT NULL, "branchId" UUID NOT NULL, "tableId" UUID NOT NULL,
  name TEXT NOT NULL, recurrence "BatchRecurrence" NOT NULL, "oneOffDate" DATE, weekdays SMALLINT[] NOT NULL DEFAULT '{}',
  "startsOn" DATE NOT NULL, "endsOn" DATE, "startTime" TIME NOT NULL, "endTime" TIME NOT NULL, active BOOLEAN NOT NULL DEFAULT true,
  "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(), UNIQUE ("academyId", id),
  FOREIGN KEY ("academyId", "branchId") REFERENCES "Branch"("academyId", id) ON DELETE RESTRICT,
  FOREIGN KEY ("academyId", "branchId", "tableId") REFERENCES "TableResource"("academyId", "branchId", id) ON DELETE RESTRICT,
  CHECK ("endTime" > "startTime"), CHECK ("endsOn" IS NULL OR "endsOn" >= "startsOn"),
  CHECK ((recurrence='ONCE' AND "oneOffDate" IS NOT NULL AND cardinality(weekdays)=0) OR (recurrence='WEEKLY' AND "oneOffDate" IS NULL AND cardinality(weekdays)>0)),
  CHECK (weekdays <@ ARRAY[0,1,2,3,4,5,6]::smallint[])
);
CREATE TABLE "BatchCoach" (
  "academyId" UUID NOT NULL, "batchId" UUID NOT NULL, "coachId" UUID NOT NULL, PRIMARY KEY ("batchId", "coachId"),
  FOREIGN KEY ("academyId", "batchId") REFERENCES "Batch"("academyId", id) ON DELETE CASCADE,
  FOREIGN KEY ("academyId", "coachId") REFERENCES "Coach"("academyId", id) ON DELETE RESTRICT
);
CREATE TABLE "BatchAthlete" (
  "academyId" UUID NOT NULL, "batchId" UUID NOT NULL, "athleteId" UUID NOT NULL, PRIMARY KEY ("batchId", "athleteId"),
  FOREIGN KEY ("academyId", "batchId") REFERENCES "Batch"("academyId", id) ON DELETE CASCADE,
  FOREIGN KEY ("academyId", "athleteId") REFERENCES "Athlete"("academyId", id) ON DELETE RESTRICT
);
CREATE TABLE "AthleteDailyAttendance" (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), "academyId" UUID NOT NULL, "athleteId" UUID NOT NULL, "localDate" DATE NOT NULL,
  status "AttendanceStatus" NOT NULL, "actorId" UUID NOT NULL, "updatedAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE ("academyId", "athleteId", "localDate"), FOREIGN KEY ("academyId", "athleteId") REFERENCES "Athlete"("academyId", id) ON DELETE RESTRICT
);
CREATE TABLE "CoachAttendance" (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), "academyId" UUID NOT NULL, "coachId" UUID NOT NULL, "localDate" DATE NOT NULL,
  status "AttendanceStatus" NOT NULL, "actorId" UUID NOT NULL, "updatedAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE ("academyId", "coachId", "localDate"), FOREIGN KEY ("academyId", "coachId") REFERENCES "Coach"("academyId", id) ON DELETE RESTRICT
);
CREATE TABLE "Invoice" (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), "academyId" UUID NOT NULL, "athleteId" UUID NOT NULL, "branchId" UUID,
  "billingMonth" DATE NOT NULL, amount NUMERIC(12,2) NOT NULL, discount NUMERIC(12,2) NOT NULL DEFAULT 0, "dueDate" DATE NOT NULL,
  status "InvoiceStatus" NOT NULL DEFAULT 'DUE', note TEXT, "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE ("academyId", "athleteId", "billingMonth"), UNIQUE ("academyId", id),
  FOREIGN KEY ("academyId", "athleteId") REFERENCES "Athlete"("academyId", id) ON DELETE RESTRICT,
  FOREIGN KEY ("academyId", "branchId") REFERENCES "Branch"("academyId", id) ON DELETE RESTRICT,
  CHECK (amount > 0 AND discount >= 0 AND discount <= amount), CHECK (date_trunc('month', "billingMonth")::date = "billingMonth")
);
CREATE TABLE "Payment" (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), "academyId" UUID NOT NULL, "invoiceId" UUID, "athleteId" UUID, "branchId" UUID,
  kind "PaymentKind" NOT NULL, amount NUMERIC(12,2) NOT NULL, "paidOn" DATE NOT NULL, method "PaymentMethod" NOT NULL,
  reference TEXT, note TEXT, "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(), UNIQUE ("academyId", id),
  FOREIGN KEY ("academyId", "invoiceId") REFERENCES "Invoice"("academyId", id) ON DELETE RESTRICT,
  FOREIGN KEY ("academyId", "athleteId") REFERENCES "Athlete"("academyId", id) ON DELETE RESTRICT,
  FOREIGN KEY ("academyId", "branchId") REFERENCES "Branch"("academyId", id) ON DELETE RESTRICT,
  CHECK (amount > 0), CHECK ((kind='FEE' AND "invoiceId" IS NOT NULL AND "athleteId" IS NOT NULL) OR (kind='AD_HOC' AND "invoiceId" IS NULL))
);
CREATE TABLE "Refund" (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), "academyId" UUID NOT NULL, "paymentId" UUID NOT NULL, amount NUMERIC(12,2) NOT NULL,
  "refundedOn" DATE NOT NULL, reason TEXT NOT NULL, "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
  FOREIGN KEY ("academyId", "paymentId") REFERENCES "Payment"("academyId", id) ON DELETE CASCADE, CHECK (amount > 0)
);
CREATE TABLE "Expense" (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), "academyId" UUID NOT NULL REFERENCES "Academy"(id) ON DELETE RESTRICT,
  "branchId" UUID, amount NUMERIC(12,2) NOT NULL, "incurredOn" DATE NOT NULL, category TEXT NOT NULL, vendor TEXT, note TEXT,
  "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(), FOREIGN KEY ("academyId", "branchId") REFERENCES "Branch"("academyId", id) ON DELETE RESTRICT,
  CHECK (amount > 0)
);

CREATE INDEX batch_schedule ON "Batch"("academyId", "startsOn", "endsOn");
CREATE INDEX invoice_month ON "Invoice"("academyId", "billingMonth");
CREATE INDEX payment_date ON "Payment"("academyId", "paidOn");
CREATE INDEX expense_date ON "Expense"("academyId", "incurredOn");

ALTER TABLE "Coach" ENABLE ROW LEVEL SECURITY; ALTER TABLE "Batch" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "BatchCoach" ENABLE ROW LEVEL SECURITY; ALTER TABLE "BatchAthlete" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "AthleteDailyAttendance" ENABLE ROW LEVEL SECURITY; ALTER TABLE "CoachAttendance" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Invoice" ENABLE ROW LEVEL SECURITY; ALTER TABLE "Payment" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Refund" ENABLE ROW LEVEL SECURITY; ALTER TABLE "Expense" ENABLE ROW LEVEL SECURITY;

GRANT SELECT, INSERT, UPDATE, DELETE ON "Coach", "Batch", "BatchCoach", "BatchAthlete", "AthleteDailyAttendance", "CoachAttendance", "Invoice", "Payment", "Refund", "Expense" TO ams_app;
GRANT UPDATE ON "Athlete" TO ams_app;
GRANT UPDATE, DELETE ON "Branch", "TableResource" TO ams_app;

CREATE FUNCTION app_private.is_finance(a uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path='' AS $$
  SELECT EXISTS (SELECT 1 FROM public."Membership" m JOIN public."Academy" x ON x.id=m."academyId" WHERE m."academyId"=$1 AND m."userId"=app_private.actor() AND m.active AND x.active AND ('ADMIN'=ANY(m.roles) OR 'FINANCE'=ANY(m.roles)))
$$;
REVOKE ALL ON FUNCTION app_private.is_finance(uuid) FROM PUBLIC; GRANT EXECUTE ON FUNCTION app_private.is_finance(uuid) TO ams_app;
CREATE POLICY audit_finance_append ON "Audit" FOR INSERT TO ams_app WITH CHECK ("academyId"=app_private.academy() AND "actorId"=app_private.actor() AND app_private.is_finance("academyId"));

CREATE POLICY coach_read ON "Coach" FOR SELECT TO ams_app USING (app_private.is_member("academyId"));
CREATE POLICY coach_write ON "Coach" FOR ALL TO ams_app USING (app_private.is_admin("academyId")) WITH CHECK (app_private.is_admin("academyId"));
CREATE POLICY batch_read ON "Batch" FOR SELECT TO ams_app USING (app_private.is_member("academyId"));
CREATE POLICY batch_write ON "Batch" FOR ALL TO ams_app USING (app_private.is_admin("academyId")) WITH CHECK (app_private.is_admin("academyId"));
CREATE POLICY batch_coach_read ON "BatchCoach" FOR SELECT TO ams_app USING (app_private.is_member("academyId"));
CREATE POLICY batch_coach_write ON "BatchCoach" FOR ALL TO ams_app USING (app_private.is_admin("academyId")) WITH CHECK (app_private.is_admin("academyId"));
CREATE POLICY batch_athlete_read ON "BatchAthlete" FOR SELECT TO ams_app USING (app_private.is_member("academyId"));
CREATE POLICY batch_athlete_write ON "BatchAthlete" FOR ALL TO ams_app USING (app_private.is_admin("academyId")) WITH CHECK (app_private.is_admin("academyId"));
CREATE POLICY daily_athlete_read ON "AthleteDailyAttendance" FOR SELECT TO ams_app USING (app_private.is_member("academyId"));
CREATE POLICY daily_athlete_write ON "AthleteDailyAttendance" FOR ALL TO ams_app USING (app_private.is_admin("academyId")) WITH CHECK (app_private.is_admin("academyId"));
CREATE POLICY coach_attendance_read ON "CoachAttendance" FOR SELECT TO ams_app USING (app_private.is_member("academyId"));
CREATE POLICY coach_attendance_write ON "CoachAttendance" FOR ALL TO ams_app USING (app_private.is_admin("academyId")) WITH CHECK (app_private.is_admin("academyId"));
CREATE POLICY invoice_finance ON "Invoice" FOR ALL TO ams_app USING (app_private.is_finance("academyId")) WITH CHECK (app_private.is_finance("academyId"));
CREATE POLICY payment_finance ON "Payment" FOR ALL TO ams_app USING (app_private.is_finance("academyId")) WITH CHECK (app_private.is_finance("academyId"));
CREATE POLICY refund_finance ON "Refund" FOR ALL TO ams_app USING (app_private.is_finance("academyId")) WITH CHECK (app_private.is_finance("academyId"));
CREATE POLICY expense_finance ON "Expense" FOR ALL TO ams_app USING (app_private.is_finance("academyId")) WITH CHECK (app_private.is_finance("academyId"));
CREATE POLICY branch_admin_update ON "Branch" FOR UPDATE TO ams_app USING (app_private.is_admin("academyId")) WITH CHECK (app_private.is_admin("academyId"));
CREATE POLICY branch_admin_delete ON "Branch" FOR DELETE TO ams_app USING (app_private.is_admin("academyId"));
CREATE POLICY table_admin_update ON "TableResource" FOR UPDATE TO ams_app USING (app_private.is_admin("academyId")) WITH CHECK (app_private.is_admin("academyId"));
CREATE POLICY table_admin_delete ON "TableResource" FOR DELETE TO ams_app USING (app_private.is_admin("academyId"));
