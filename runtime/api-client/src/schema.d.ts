export interface paths {
    "/api/platform/auth/sign-in": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Platform Sign In */
        post: operations["platform_sign_in_api_platform_auth_sign_in_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/platform/auth/sign-out": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Platform Sign Out */
        post: operations["platform_sign_out_api_platform_auth_sign_out_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/auth/config": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Auth Config */
        get: operations["auth_config_api_auth_config_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/auth/demo": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Demo */
        post: operations["demo_api_auth_demo_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/auth/password/sign-in": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Password Sign In */
        post: operations["password_sign_in_api_auth_password_sign_in_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/auth/password/change-required": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Password Change */
        post: operations["password_change_api_auth_password_change_required_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/auth/password/sign-out": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Password Sign Out */
        post: operations["password_sign_out_api_auth_password_sign_out_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/me": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Me */
        get: operations["me_api_me_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/invitations/accept": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Accept */
        post: operations["accept_api_invitations_accept_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/platform/academies": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Academies */
        get: operations["academies_api_platform_academies_get"];
        put?: never;
        /** Create Academy */
        post: operations["create_academy_api_platform_academies_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/platform/credential-handoffs": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Credential Handoffs */
        get: operations["credential_handoffs_api_platform_credential_handoffs_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/platform/credential-handoffs/{handoff_id}/reveal": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Reveal Credentials */
        post: operations["reveal_credentials_api_platform_credential_handoffs__handoff_id__reveal_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/platform/credential-handoffs/{handoff_id}/copied": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Copied Credentials */
        post: operations["copied_credentials_api_platform_credential_handoffs__handoff_id__copied_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/platform/credential-handoffs/{handoff_id}/retry-email": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Retry Credentials Email */
        post: operations["retry_credentials_email_api_platform_credential_handoffs__handoff_id__retry_email_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/platform/academies/{academy_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        /** Set Active */
        patch: operations["set_active_api_platform_academies__academy_id__patch"];
        trace?: never;
    };
    "/api/platform/academies/{academy_id}/subscription": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        /** Set Subscription */
        patch: operations["set_subscription_api_platform_academies__academy_id__subscription_patch"];
        trace?: never;
    };
    "/api/academies/{academy_id}/dashboard": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Dashboard */
        get: operations["dashboard_api_academies__academy_id__dashboard_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/branches": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Branches */
        get: operations["branches_api_academies__academy_id__branches_get"];
        put?: never;
        /** Create Branch */
        post: operations["create_branch_api_academies__academy_id__branches_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/branches/{branch_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        /** Update Branch */
        put: operations["update_branch_api_academies__academy_id__branches__branch_id__put"];
        post?: never;
        /** Delete Branch */
        delete: operations["delete_branch_api_academies__academy_id__branches__branch_id__delete"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/branches/{branch_id}/tables": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Create Table */
        post: operations["create_table_api_academies__academy_id__branches__branch_id__tables_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/branches/{branch_id}/tables/{table_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        /** Update Table */
        put: operations["update_table_api_academies__academy_id__branches__branch_id__tables__table_id__put"];
        post?: never;
        /** Delete Table */
        delete: operations["delete_table_api_academies__academy_id__branches__branch_id__tables__table_id__delete"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/members": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Members */
        get: operations["members_api_academies__academy_id__members_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/members/{member_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        /** Update Member */
        patch: operations["update_member_api_academies__academy_id__members__member_id__patch"];
        trace?: never;
    };
    "/api/academies/{academy_id}/invitations": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Invitations */
        get: operations["invitations_api_academies__academy_id__invitations_get"];
        put?: never;
        /** Invite */
        post: operations["invite_api_academies__academy_id__invitations_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/invitations/{invitation_id}/revoke": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Revoke */
        post: operations["revoke_api_academies__academy_id__invitations__invitation_id__revoke_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/activity": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Activity */
        get: operations["activity_api_academies__academy_id__activity_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/athletes": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Athletes */
        get: operations["athletes_api_academies__academy_id__athletes_get"];
        put?: never;
        /** Create Athlete */
        post: operations["create_athlete_api_academies__academy_id__athletes_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/athletes/{athlete_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        /** Update Athlete */
        patch: operations["update_athlete_api_academies__academy_id__athletes__athlete_id__patch"];
        trace?: never;
    };
    "/api/academies/{academy_id}/coaches": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Coaches */
        get: operations["coaches_api_academies__academy_id__coaches_get"];
        put?: never;
        /** Create Coach */
        post: operations["create_coach_api_academies__academy_id__coaches_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/coaches/{coach_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        /** Update Coach */
        put: operations["update_coach_api_academies__academy_id__coaches__coach_id__put"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/batches": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Batches */
        get: operations["batches_api_academies__academy_id__batches_get"];
        put?: never;
        /** Create Batch */
        post: operations["create_batch_api_academies__academy_id__batches_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/batches/{batch_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        /** Update Batch */
        put: operations["update_batch_api_academies__academy_id__batches__batch_id__put"];
        post?: never;
        /** Delete Batch */
        delete: operations["delete_batch_api_academies__academy_id__batches__batch_id__delete"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/daily-attendance": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Daily Attendance */
        get: operations["daily_attendance_api_academies__academy_id__daily_attendance_get"];
        /** Save Daily Attendance */
        put: operations["save_daily_attendance_api_academies__academy_id__daily_attendance_put"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/invoices": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Invoices */
        get: operations["invoices_api_academies__academy_id__invoices_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/invoices/generate": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Generate Invoices */
        post: operations["generate_invoices_api_academies__academy_id__invoices_generate_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/invoices/{invoice_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        /** Update Invoice */
        patch: operations["update_invoice_api_academies__academy_id__invoices__invoice_id__patch"];
        trace?: never;
    };
    "/api/academies/{academy_id}/payments": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Payments */
        get: operations["payments_api_academies__academy_id__payments_get"];
        put?: never;
        /** Create Payment */
        post: operations["create_payment_api_academies__academy_id__payments_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/payments/{payment_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        /** Update Payment */
        put: operations["update_payment_api_academies__academy_id__payments__payment_id__put"];
        post?: never;
        /** Delete Payment */
        delete: operations["delete_payment_api_academies__academy_id__payments__payment_id__delete"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/refunds": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Refunds */
        get: operations["refunds_api_academies__academy_id__refunds_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/payments/{payment_id}/refunds": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Create Refund */
        post: operations["create_refund_api_academies__academy_id__payments__payment_id__refunds_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/expenses": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Expenses */
        get: operations["expenses_api_academies__academy_id__expenses_get"];
        put?: never;
        /** Create Expense */
        post: operations["create_expense_api_academies__academy_id__expenses_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/expenses/{expense_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        /** Update Expense */
        put: operations["update_expense_api_academies__academy_id__expenses__expense_id__put"];
        post?: never;
        /** Delete Expense */
        delete: operations["delete_expense_api_academies__academy_id__expenses__expense_id__delete"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/finance-summary": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Finance Summary */
        get: operations["finance_summary_api_academies__academy_id__finance_summary_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/guardian-links": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Guardian Link */
        post: operations["guardian_link_api_academies__academy_id__guardian_links_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/sessions": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Sessions */
        get: operations["sessions_api_academies__academy_id__sessions_get"];
        put?: never;
        /** Create Session */
        post: operations["create_session_api_academies__academy_id__sessions_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/sessions/{session_id}/roster": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Add Roster */
        post: operations["add_roster_api_academies__academy_id__sessions__session_id__roster_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/sessions/{session_id}/attendance/{athlete_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        /** Mark Attendance */
        put: operations["mark_attendance_api_academies__academy_id__sessions__session_id__attendance__athlete_id__put"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/academies/{academy_id}/attendance-qr": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Create Qr */
        post: operations["create_qr_api_academies__academy_id__attendance_qr_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/attendance-qr/redeem": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Redeem Qr */
        post: operations["redeem_qr_api_attendance_qr_redeem_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/health": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Health */
        get: operations["health_api_health_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {
        /** AcademyCreatedDto */
        AcademyCreatedDto: {
            academy: components["schemas"]["AcademyDto"];
            handoff: components["schemas"]["HandoffDto"];
        };
        /** AcademyDto */
        AcademyDto: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Name */
            name: string;
            /** Slug */
            slug: string;
            /** Active */
            active: boolean;
            /** Timezone */
            timezone: string;
            /**
             * Createdat
             * Format: date-time
             */
            createdAt: string;
            subscriptionPlan: components["schemas"]["SubscriptionPlan"];
            subscriptionStatus: components["schemas"]["SubscriptionStatus"];
            /**
             * Subscriptionstartson
             * Format: date
             */
            subscriptionStartsOn: string;
            /** Subscriptionendson */
            subscriptionEndsOn: string | null;
        };
        /** AcademyInput */
        AcademyInput: {
            /** Name */
            name: string;
            /** Slug */
            slug: string;
            /** Adminemail */
            adminEmail: string;
            /** Adminname */
            adminName: string;
            /** Adminusername */
            adminUsername: string;
            /** Temporarypassword */
            temporaryPassword: string;
            /** @default STARTER */
            subscriptionPlan: components["schemas"]["SubscriptionPlan"];
            /** @default TRIAL */
            subscriptionStatus: components["schemas"]["SubscriptionStatus"];
            /**
             * Subscriptionstartson
             * Format: date
             */
            subscriptionStartsOn?: string;
            /** Subscriptionendson */
            subscriptionEndsOn?: string | null;
        };
        /** AcceptDto */
        AcceptDto: {
            /**
             * Academyid
             * Format: uuid
             */
            academyId: string;
        };
        /** AcceptInput */
        AcceptInput: {
            /** Token */
            token: string;
        };
        /** ActiveInput */
        ActiveInput: {
            /** Active */
            active: boolean;
        };
        /** AthleteDto */
        AthleteDto: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Name */
            name: string;
            /** Membershipid */
            membershipId: string | null;
            /** Homebranchid */
            homeBranchId: string | null;
            /** Monthlyfee */
            monthlyFee: string;
            /** Active */
            active: boolean;
        };
        /** AthleteInput */
        AthleteInput: {
            /** Name */
            name: string;
            /** Membershipid */
            membershipId?: string | null;
            /** Homebranchid */
            homeBranchId?: string | null;
            /**
             * Monthlyfee
             * @default 0
             */
            monthlyFee: number | string;
        };
        /** AthleteUpdateInput */
        AthleteUpdateInput: {
            /** Homebranchid */
            homeBranchId?: string | null;
            /** Monthlyfee */
            monthlyFee: number | string;
        };
        /** AttendanceDto */
        AttendanceDto: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Sessionid */
            sessionId?: string | null;
            /** Athleteid */
            athleteId?: string | null;
            /** Membershipid */
            membershipId?: string | null;
            /** Branchid */
            branchId?: string | null;
            /** Localdate */
            localDate?: string | null;
            /** Status */
            status: string;
            /** Source */
            source: string;
            /**
             * Checkedat
             * Format: date-time
             */
            checkedAt: string;
        };
        /** AttendanceInput */
        AttendanceInput: {
            /** Status */
            status: string;
            /** Correctionreason */
            correctionReason?: string | null;
        };
        /** AuditDto */
        AuditDto: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Action */
            action: string;
            /** Detail */
            detail: string;
            /**
             * Createdat
             * Format: date-time
             */
            createdAt: string;
        };
        /** AuthConfigDto */
        AuthConfigDto: {
            /** Demo */
            demo: boolean;
            /** Profiles */
            profiles: components["schemas"]["DemoProfileDto"][];
        };
        /** BatchDto */
        BatchDto: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Academyid
             * Format: uuid
             */
            academyId: string;
            /** Name */
            name: string;
            /**
             * Branchid
             * Format: uuid
             */
            branchId: string;
            /**
             * Tableid
             * Format: uuid
             */
            tableId: string;
            /** Recurrence */
            recurrence: string;
            /** Oneoffdate */
            oneOffDate: string | null;
            /** Weekdays */
            weekdays: number[];
            /**
             * Startson
             * Format: date
             */
            startsOn: string;
            /** Endson */
            endsOn: string | null;
            /**
             * Starttime
             * Format: time
             */
            startTime: string;
            /**
             * Endtime
             * Format: time
             */
            endTime: string;
            /** Coachids */
            coachIds: string[];
            /** Athleteids */
            athleteIds: string[];
            /** Active */
            active: boolean;
        };
        /** BatchInput */
        BatchInput: {
            /** Name */
            name: string;
            /**
             * Branchid
             * Format: uuid
             */
            branchId: string;
            /**
             * Tableid
             * Format: uuid
             */
            tableId: string;
            /** Recurrence */
            recurrence: string;
            /** Oneoffdate */
            oneOffDate?: string | null;
            /**
             * Weekdays
             * @default []
             */
            weekdays: number[];
            /**
             * Startson
             * Format: date
             */
            startsOn: string;
            /** Endson */
            endsOn?: string | null;
            /**
             * Starttime
             * Format: time
             */
            startTime: string;
            /**
             * Endtime
             * Format: time
             */
            endTime: string;
            /**
             * Coachids
             * @default []
             */
            coachIds: string[];
            /**
             * Athleteids
             * @default []
             */
            athleteIds: string[];
            /**
             * Active
             * @default true
             */
            active: boolean;
        };
        /** BranchDto */
        BranchDto: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Name */
            name: string;
            /** City */
            city: string;
            /** Address */
            address: string;
            /** Tables */
            tables: components["schemas"]["TableDto"][];
        };
        /** BranchInput */
        BranchInput: {
            /** Name */
            name: string;
            /** City */
            city: string;
            /** Address */
            address: string;
        };
        /** BranchRevenueDto */
        BranchRevenueDto: {
            /** Branchid */
            branchId: string | null;
            /** Branchname */
            branchName: string;
            /** Revenue */
            revenue: string;
        };
        /** CoachDto */
        CoachDto: {
            /** Name */
            name: string;
            /** Phone */
            phone: string;
            /** Email */
            email?: string | null;
            /** Notes */
            notes?: string | null;
            /**
             * Active
             * @default true
             */
            active: boolean;
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Createdat
             * Format: date-time
             */
            createdAt: string;
        };
        /** CoachInput */
        CoachInput: {
            /** Name */
            name: string;
            /** Phone */
            phone: string;
            /** Email */
            email?: string | null;
            /** Notes */
            notes?: string | null;
            /**
             * Active
             * @default true
             */
            active: boolean;
        };
        /** DailyAttendanceDto */
        DailyAttendanceDto: {
            /** Persontype */
            personType: string;
            /**
             * Personid
             * Format: uuid
             */
            personId: string;
            /** Name */
            name: string;
            /** Status */
            status: string | null;
        };
        /** DailyAttendanceEntry */
        DailyAttendanceEntry: {
            /** Persontype */
            personType: string;
            /**
             * Personid
             * Format: uuid
             */
            personId: string;
            /** Status */
            status: string;
        };
        /** DailyAttendanceInput */
        DailyAttendanceInput: {
            /**
             * Localdate
             * Format: date
             */
            localDate: string;
            /** Entries */
            entries: components["schemas"]["DailyAttendanceEntry"][];
        };
        /** DashboardDto */
        DashboardDto: {
            /** Branches */
            branches: number;
            /** Tables */
            tables: number;
            /** Members */
            members: number | null;
            /** Invitations */
            invitations: number | null;
            /** Currentmonthrevenue */
            currentMonthRevenue: string;
        };
        /** DemoInput */
        DemoInput: {
            /**
             * Userid
             * Format: uuid
             */
            userId: string;
        };
        /** DemoProfileDto */
        DemoProfileDto: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Name */
            name: string;
            /** Email */
            email: string;
            /** Label */
            label: string;
        };
        /** ExpenseDto */
        ExpenseDto: {
            /** Branchid */
            branchId?: string | null;
            /** Amount */
            amount: string;
            /**
             * Incurredon
             * Format: date
             */
            incurredOn: string;
            /** Category */
            category: string;
            /** Vendor */
            vendor?: string | null;
            /** Note */
            note?: string | null;
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Createdat
             * Format: date-time
             */
            createdAt: string;
        };
        /** ExpenseInput */
        ExpenseInput: {
            /** Branchid */
            branchId?: string | null;
            /** Amount */
            amount: number | string;
            /**
             * Incurredon
             * Format: date
             */
            incurredOn: string;
            /** Category */
            category: string;
            /** Vendor */
            vendor?: string | null;
            /** Note */
            note?: string | null;
        };
        /** FinanceSummaryDto */
        FinanceSummaryDto: {
            /** Collections */
            collections: string;
            /** Refunds */
            refunds: string;
            /** Expenses */
            expenses: string;
            /** Outstanding */
            outstanding: string;
            /** Net */
            net: string;
            /** Monthlytrend */
            monthlyTrend: components["schemas"]["TrendDto"][];
            /** Branchdistribution */
            branchDistribution: components["schemas"]["BranchRevenueDto"][];
        };
        /** GuardianLinkInput */
        GuardianLinkInput: {
            /**
             * Guardianmembershipid
             * Format: uuid
             */
            guardianMembershipId: string;
            /**
             * Athleteid
             * Format: uuid
             */
            athleteId: string;
        };
        /** HTTPValidationError */
        HTTPValidationError: {
            /** Detail */
            detail?: components["schemas"]["ValidationError"][];
        };
        /** HandoffDto */
        HandoffDto: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Academyid
             * Format: uuid
             */
            academyId: string;
            /** Academyname */
            academyName: string;
            /** Username */
            username: string;
            /** Email */
            email: string;
            /** Copied */
            copied: boolean;
            /** Emailsent */
            emailSent: boolean;
            /** Emailerror */
            emailError: string | null;
            /**
             * Createdat
             * Format: date-time
             */
            createdAt: string;
        };
        /** HandoffSecretDto */
        HandoffSecretDto: {
            /** Temporarypassword */
            temporaryPassword: string;
        };
        /** InvitationCreatedDto */
        InvitationCreatedDto: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Invitationurl */
            invitationUrl: string;
        };
        /** InvitationDto */
        InvitationDto: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Email */
            email: string;
            /** Roles */
            roles: components["schemas"]["Role"][];
            /** Allbranches */
            allBranches: boolean;
            /** Branchids */
            branchIds: string[];
            /**
             * Expiresat
             * Format: date-time
             */
            expiresAt: string;
            /** Acceptedat */
            acceptedAt: string | null;
            /**
             * Createdat
             * Format: date-time
             */
            createdAt: string;
        };
        /** InvitationInput */
        InvitationInput: {
            /** Roles */
            roles: components["schemas"]["Role"][];
            /** Allbranches */
            allBranches: boolean;
            /** Branchids */
            branchIds: string[];
            /** Email */
            email: string;
        };
        /** InvoiceDto */
        InvoiceDto: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Athleteid
             * Format: uuid
             */
            athleteId: string;
            /** Athletename */
            athleteName: string;
            /** Branchid */
            branchId: string | null;
            /**
             * Billingmonth
             * Format: date
             */
            billingMonth: string;
            /** Amount */
            amount: string;
            /** Discount */
            discount: string;
            /**
             * Duedate
             * Format: date
             */
            dueDate: string;
            /** Status */
            status: string;
            /** Paid */
            paid: string;
            /** Balance */
            balance: string;
            /** Note */
            note: string | null;
        };
        /** InvoiceGenerateInput */
        InvoiceGenerateInput: {
            /**
             * Billingmonth
             * Format: date
             */
            billingMonth: string;
            /**
             * Duedate
             * Format: date
             */
            dueDate: string;
        };
        /** InvoiceUpdateInput */
        InvoiceUpdateInput: {
            /** Discount */
            discount: number | string;
            /**
             * Duedate
             * Format: date
             */
            dueDate: string;
            /** Note */
            note?: string | null;
            /** Status */
            status?: string | null;
        };
        /** MeDto */
        MeDto: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Email */
            email: string;
            /** Name */
            name: string;
            /** Platformowner */
            platformOwner: boolean;
            /**
             * Passwordchangerequired
             * @default false
             */
            passwordChangeRequired: boolean;
            /** Workspaces */
            workspaces: components["schemas"]["WorkspaceDto"][];
        };
        /** MemberDto */
        MemberDto: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Userid
             * Format: uuid
             */
            userId: string;
            /** Name */
            name: string;
            /** Email */
            email: string;
            /** Roles */
            roles: components["schemas"]["Role"][];
            /** Allbranches */
            allBranches: boolean;
            /** Active */
            active: boolean;
            /** Branchids */
            branchIds: string[];
        };
        /** MemberInput */
        MemberInput: {
            /** Roles */
            roles: components["schemas"]["Role"][];
            /** Allbranches */
            allBranches: boolean;
            /** Branchids */
            branchIds: string[];
            /** Active */
            active: boolean;
        };
        /** PasswordChangeInput */
        PasswordChangeInput: {
            /** Newpassword */
            newPassword: string;
        };
        /** PasswordSignInInput */
        PasswordSignInInput: {
            /** Username */
            username: string;
            /** Password */
            password: string;
        };
        /** PaymentDto */
        PaymentDto: {
            /** Invoiceid */
            invoiceId?: string | null;
            /** Athleteid */
            athleteId?: string | null;
            /** Branchid */
            branchId?: string | null;
            /** Kind */
            kind: string;
            /** Amount */
            amount: string;
            /**
             * Paidon
             * Format: date
             */
            paidOn: string;
            /** Method */
            method: string;
            /** Reference */
            reference?: string | null;
            /** Note */
            note?: string | null;
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Athletename */
            athleteName: string | null;
            /** Refunded */
            refunded: string;
            /**
             * Createdat
             * Format: date-time
             */
            createdAt: string;
        };
        /** PaymentInput */
        PaymentInput: {
            /** Invoiceid */
            invoiceId?: string | null;
            /** Athleteid */
            athleteId?: string | null;
            /** Branchid */
            branchId?: string | null;
            /** Kind */
            kind: string;
            /** Amount */
            amount: number | string;
            /**
             * Paidon
             * Format: date
             */
            paidOn: string;
            /** Method */
            method: string;
            /** Reference */
            reference?: string | null;
            /** Note */
            note?: string | null;
        };
        /** PlatformSignInInput */
        PlatformSignInInput: {
            /** Username */
            username: string;
            /** Password */
            password: string;
        };
        /** QrDto */
        QrDto: {
            /** Token */
            token: string;
            /** Url */
            url: string;
            /**
             * Expiresat
             * Format: date-time
             */
            expiresAt: string;
        };
        /** QrInput */
        QrInput: {
            /** Kind */
            kind: string;
            /**
             * Branchid
             * Format: uuid
             */
            branchId: string;
            /** Sessionid */
            sessionId?: string | null;
        };
        /** RedeemQrInput */
        RedeemQrInput: {
            /** Token */
            token: string;
            /** Athleteid */
            athleteId?: string | null;
        };
        /** RefundDto */
        RefundDto: {
            /** Amount */
            amount: string;
            /**
             * Refundedon
             * Format: date
             */
            refundedOn: string;
            /** Reason */
            reason: string;
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Paymentid
             * Format: uuid
             */
            paymentId: string;
            /**
             * Createdat
             * Format: date-time
             */
            createdAt: string;
        };
        /** RefundInput */
        RefundInput: {
            /** Amount */
            amount: number | string;
            /**
             * Refundedon
             * Format: date
             */
            refundedOn: string;
            /** Reason */
            reason: string;
        };
        /**
         * Role
         * @enum {string}
         */
        Role: "ADMIN" | "COACH" | "FINANCE" | "SCORER" | "ATHLETE" | "GUARDIAN";
        /** RosterInput */
        RosterInput: {
            /**
             * Athleteid
             * Format: uuid
             */
            athleteId: string;
        };
        /** SessionDto */
        SessionDto: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Branchid
             * Format: uuid
             */
            branchId: string;
            /** Coachmembershipid */
            coachMembershipId: string | null;
            /** Title */
            title: string;
            /**
             * Startsat
             * Format: date-time
             */
            startsAt: string;
            /**
             * Endsat
             * Format: date-time
             */
            endsAt: string;
            /** Status */
            status: string;
        };
        /** SessionInput */
        SessionInput: {
            /**
             * Branchid
             * Format: uuid
             */
            branchId: string;
            /** Coachmembershipid */
            coachMembershipId?: string | null;
            /** Title */
            title: string;
            /**
             * Startsat
             * Format: date-time
             */
            startsAt: string;
            /**
             * Endsat
             * Format: date-time
             */
            endsAt: string;
        };
        /** SubscriptionInput */
        SubscriptionInput: {
            plan: components["schemas"]["SubscriptionPlan"];
            status: components["schemas"]["SubscriptionStatus"];
            /**
             * Startson
             * Format: date
             */
            startsOn: string;
            /** Endson */
            endsOn?: string | null;
        };
        /**
         * SubscriptionPlan
         * @enum {string}
         */
        SubscriptionPlan: "STARTER" | "PRO" | "ENTERPRISE";
        /**
         * SubscriptionStatus
         * @enum {string}
         */
        SubscriptionStatus: "TRIAL" | "ACTIVE" | "PAST_DUE" | "CANCELLED" | "EXPIRED";
        /** TableDto */
        TableDto: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Name */
            name: string;
        };
        /** TableInput */
        TableInput: {
            /** Name */
            name: string;
        };
        /** TokenDto */
        TokenDto: {
            /** Accesstoken */
            accessToken: string;
        };
        /** TrendDto */
        TrendDto: {
            /**
             * Month
             * Format: date
             */
            month: string;
            /** Revenue */
            revenue: string;
            /** Expenses */
            expenses: string;
        };
        /** ValidationError */
        ValidationError: {
            /** Location */
            loc: (string | number)[];
            /** Message */
            msg: string;
            /** Error Type */
            type: string;
        };
        /** WorkspaceDto */
        WorkspaceDto: {
            academy: components["schemas"]["AcademyDto"];
            membership: components["schemas"]["MemberDto"];
        };
    };
    responses: never;
    parameters: never;
    requestBodies: never;
    headers: never;
    pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
    platform_sign_in_api_platform_auth_sign_in_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["PlatformSignInInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    platform_sign_out_api_platform_auth_sign_out_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    auth_config_api_auth_config_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AuthConfigDto"];
                };
            };
        };
    };
    demo_api_auth_demo_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["DemoInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TokenDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    password_sign_in_api_auth_password_sign_in_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["PasswordSignInInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    password_change_api_auth_password_change_required_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["PasswordChangeInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    password_sign_out_api_auth_password_sign_out_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    me_api_me_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["MeDto"];
                };
            };
        };
    };
    accept_api_invitations_accept_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["AcceptInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AcceptDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    academies_api_platform_academies_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AcademyDto"][];
                };
            };
        };
    };
    create_academy_api_platform_academies_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["AcademyInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AcademyCreatedDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    credential_handoffs_api_platform_credential_handoffs_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HandoffDto"][];
                };
            };
        };
    };
    reveal_credentials_api_platform_credential_handoffs__handoff_id__reveal_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                handoff_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HandoffSecretDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    copied_credentials_api_platform_credential_handoffs__handoff_id__copied_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                handoff_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    retry_credentials_email_api_platform_credential_handoffs__handoff_id__retry_email_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                handoff_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HandoffDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    set_active_api_platform_academies__academy_id__patch: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ActiveInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AcademyDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    set_subscription_api_platform_academies__academy_id__subscription_patch: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SubscriptionInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AcademyDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    dashboard_api_academies__academy_id__dashboard_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DashboardDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    branches_api_academies__academy_id__branches_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BranchDto"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_branch_api_academies__academy_id__branches_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["BranchInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BranchDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_branch_api_academies__academy_id__branches__branch_id__put: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
                branch_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["BranchInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BranchDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    delete_branch_api_academies__academy_id__branches__branch_id__delete: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
                branch_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_table_api_academies__academy_id__branches__branch_id__tables_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
                branch_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["TableInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TableDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_table_api_academies__academy_id__branches__branch_id__tables__table_id__put: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
                branch_id: string;
                table_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["TableInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TableDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    delete_table_api_academies__academy_id__branches__branch_id__tables__table_id__delete: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
                branch_id: string;
                table_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    members_api_academies__academy_id__members_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["MemberDto"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_member_api_academies__academy_id__members__member_id__patch: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
                member_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["MemberInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["MemberDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    invitations_api_academies__academy_id__invitations_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["InvitationDto"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    invite_api_academies__academy_id__invitations_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["InvitationInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["InvitationCreatedDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    revoke_api_academies__academy_id__invitations__invitation_id__revoke_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
                invitation_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    activity_api_academies__academy_id__activity_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AuditDto"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    athletes_api_academies__academy_id__athletes_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AthleteDto"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_athlete_api_academies__academy_id__athletes_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["AthleteInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AthleteDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_athlete_api_academies__academy_id__athletes__athlete_id__patch: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
                athlete_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["AthleteUpdateInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AthleteDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    coaches_api_academies__academy_id__coaches_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CoachDto"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_coach_api_academies__academy_id__coaches_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CoachInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CoachDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_coach_api_academies__academy_id__coaches__coach_id__put: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
                coach_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CoachInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CoachDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    batches_api_academies__academy_id__batches_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BatchDto"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_batch_api_academies__academy_id__batches_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["BatchInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BatchDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_batch_api_academies__academy_id__batches__batch_id__put: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
                batch_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["BatchInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BatchDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    delete_batch_api_academies__academy_id__batches__batch_id__delete: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
                batch_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    daily_attendance_api_academies__academy_id__daily_attendance_get: {
        parameters: {
            query: {
                localDate: string;
            };
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DailyAttendanceDto"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    save_daily_attendance_api_academies__academy_id__daily_attendance_put: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["DailyAttendanceInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    invoices_api_academies__academy_id__invoices_get: {
        parameters: {
            query?: {
                month?: string | null;
            };
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["InvoiceDto"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    generate_invoices_api_academies__academy_id__invoices_generate_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["InvoiceGenerateInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["InvoiceDto"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_invoice_api_academies__academy_id__invoices__invoice_id__patch: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
                invoice_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["InvoiceUpdateInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["InvoiceDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    payments_api_academies__academy_id__payments_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PaymentDto"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_payment_api_academies__academy_id__payments_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["PaymentInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PaymentDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_payment_api_academies__academy_id__payments__payment_id__put: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
                payment_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["PaymentInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PaymentDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    delete_payment_api_academies__academy_id__payments__payment_id__delete: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
                payment_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    refunds_api_academies__academy_id__refunds_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RefundDto"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_refund_api_academies__academy_id__payments__payment_id__refunds_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
                payment_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RefundInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RefundDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    expenses_api_academies__academy_id__expenses_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExpenseDto"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_expense_api_academies__academy_id__expenses_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ExpenseInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExpenseDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_expense_api_academies__academy_id__expenses__expense_id__put: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
                expense_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ExpenseInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExpenseDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    delete_expense_api_academies__academy_id__expenses__expense_id__delete: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
                expense_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    finance_summary_api_academies__academy_id__finance_summary_get: {
        parameters: {
            query: {
                start: string;
                end: string;
            };
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["FinanceSummaryDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    guardian_link_api_academies__academy_id__guardian_links_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GuardianLinkInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    sessions_api_academies__academy_id__sessions_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SessionDto"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_session_api_academies__academy_id__sessions_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SessionInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SessionDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    add_roster_api_academies__academy_id__sessions__session_id__roster_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
                session_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RosterInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    mark_attendance_api_academies__academy_id__sessions__session_id__attendance__athlete_id__put: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
                session_id: string;
                athlete_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["AttendanceInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AttendanceDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_qr_api_academies__academy_id__attendance_qr_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                academy_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["QrInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["QrDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    redeem_qr_api_attendance_qr_redeem_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RedeemQrInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AttendanceDto"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    health_api_health_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
}
