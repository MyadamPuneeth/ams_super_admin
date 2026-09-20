import type { components } from './schema';
type Models = components['schemas'];
export type Me = Models['MeDto'];
export type Workspace = Models['WorkspaceDto'];
export type Branch = Models['BranchDto'];
export type Member = Models['MemberDto'];
export type Invitation = Models['InvitationDto'];
export type Academy = Models['AcademyDto'];
export type Dashboard = Models['DashboardDto'];
export type Audit = Models['AuditDto'];
export type Role = Models['InvitationInput']['roles'][number];
export type AuthConfig = Models['AuthConfigDto'];
export class ApiError extends Error {
  constructor(public readonly status: number, message: string) { super(message); }
}
export function createApi(getToken: () => string | null, baseUrl = '') {
  async function request<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
    const token = getToken();
    const response = await fetch(`${baseUrl}/api${path}`, { method, headers: { ...(body ? { 'Content-Type': 'application/json' } : {}), ...(token ? { Authorization: `Bearer ${token}` } : {}) }, body: body ? JSON.stringify(body) : undefined });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'The server could not complete this request.' }));
      throw new ApiError(response.status, Array.isArray(error.message) ? error.message.join(' ') : error.message || 'Request failed.');
    }
    return response.status === 204 ? undefined as T : response.json();
  }
  const academyPath = (id: string, resource: string) => `/academies/${encodeURIComponent(id)}/${resource}`;
  return {
    config: () => request<AuthConfig>('/auth/config'),
    demo: (userId: string) => request<Models['TokenDto']>('/auth/demo', 'POST', { userId }),
    me: () => request<Me>('/me'),
    academies: () => request<Academy[]>('/platform/academies'),
    createAcademy: (body: Models['AcademyInput']) => request<Models['AcademyCreatedDto']>('/platform/academies', 'POST', body),
    setAcademyActive: (id: string, active: boolean) => request<Academy>(`/platform/academies/${id}`, 'PATCH', { active }),
    branches: (id: string) => request<Branch[]>(academyPath(id, 'branches')),
    createBranch: (id: string, body: Models['BranchInput']) => request<Branch>(academyPath(id, 'branches'), 'POST', body),
    createTable: (id: string, branch: string, name: string) => request<Models['TableDto']>(academyPath(id, `branches/${branch}/tables`), 'POST', { name }),
    members: (id: string) => request<Member[]>(academyPath(id, 'members')),
    updateMember: (id: string, member: string, body: Models['MemberInput']) => request<Member>(academyPath(id, `members/${member}`), 'PATCH', body),
    invitations: (id: string) => request<Invitation[]>(academyPath(id, 'invitations')),
    invite: (id: string, body: Models['InvitationInput']) => request<Models['InvitationCreatedDto']>(academyPath(id, 'invitations'), 'POST', body),
    revokeInvite: (id: string, invitation: string) => request<void>(academyPath(id, `invitations/${invitation}/revoke`), 'POST'),
    accept: (token: string) => request<{ academyId: string }>('/invitations/accept', 'POST', { token }),
    dashboard: (id: string) => request<Dashboard>(academyPath(id, 'dashboard')),
    activity: (id: string) => request<Audit[]>(academyPath(id, 'activity')),
    athletes: (id: string) => request<Models['AthleteDto'][]>(academyPath(id, 'athletes')),
    createAthlete: (id: string, body: Models['AthleteInput']) => request<Models['AthleteDto']>(academyPath(id, 'athletes'), 'POST', body),
    sessions: (id: string) => request<Models['SessionDto'][]>(academyPath(id, 'sessions')),
    createSession: (id: string, body: Models['SessionInput']) => request<Models['SessionDto']>(academyPath(id, 'sessions'), 'POST', body),
    addRoster: (id: string, session: string, athleteId: string) => request<void>(academyPath(id, `sessions/${session}/roster`), 'POST', { athleteId }),
    markAttendance: (id: string, session: string, athlete: string, body: Models['AttendanceInput']) => request<Models['AttendanceDto']>(academyPath(id, `sessions/${session}/attendance/${athlete}`), 'PUT', body),
    createQr: (id: string, body: Models['QrInput']) => request<Models['QrDto']>(academyPath(id, 'attendance-qr'), 'POST', body),
    redeemQr: (body: Models['RedeemQrInput']) => request<Models['AttendanceDto']>('/attendance-qr/redeem', 'POST', body),
  };
}
