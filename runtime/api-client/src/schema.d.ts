export interface paths {
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
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Invitationurl */
            invitationUrl: string;
            academy: components["schemas"]["AcademyDto"];
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
        };
        /** AcademyInput */
        AcademyInput: {
            /** Name */
            name: string;
            /** Slug */
            slug: string;
            /** Adminemail */
            adminEmail: string;
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
            /** Active */
            active: boolean;
        };
        /** AthleteInput */
        AthleteInput: {
            /** Name */
            name: string;
            /** Membershipid */
            membershipId?: string | null;
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
