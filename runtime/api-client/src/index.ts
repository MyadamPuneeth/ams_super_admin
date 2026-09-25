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
export type Handoff = Models['HandoffDto'];
export type Athlete = Models['AthleteDto'];
export type Coach = Models['CoachDto'];
export type Batch = Models['BatchDto'];
export type Invoice = Models['InvoiceDto'];
export type Payment = Models['PaymentDto'];
export type Expense = Models['ExpenseDto'];
export type FinanceSummary = Models['FinanceSummaryDto'];
export class ApiError extends Error {
  constructor(public readonly status: number, message: string, public readonly requestId?: string) { super(message); }
}
export function createApi(getToken: () => string | null, baseUrl = '') {
  async function request<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
    const token = getToken();
    const response = await fetch(`${baseUrl}/api${path}`, { method, credentials: 'same-origin', headers: { ...(body ? { 'Content-Type': 'application/json' } : {}), ...(token ? { Authorization: `Bearer ${token}` } : {}) }, body: body ? JSON.stringify(body) : undefined });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'The server could not complete this request.' }));
      throw new ApiError(response.status, Array.isArray(error.message) ? error.message.join(' ') : error.message || 'Request failed.', error.requestId);
    }
    return response.status === 204 ? undefined as T : response.json();
  }
  const academyPath = (id: string, resource: string) => `/academies/${encodeURIComponent(id)}/${resource}`;
  return {
    platformSignIn: (body: Models['PlatformSignInInput']) => request<void>('/platform/auth/sign-in', 'POST', body),
    platformSignOut: () => request<void>('/platform/auth/sign-out', 'POST'),
    passwordSignIn: (body: Models['PasswordSignInInput']) => request<void>('/auth/password/sign-in', 'POST', body),
    changeRequiredPassword: (newPassword: string) => request<void>('/auth/password/change-required', 'POST', { newPassword }),
    passwordSignOut: () => request<void>('/auth/password/sign-out', 'POST'),
    config: () => request<AuthConfig>('/auth/config'),
    demo: (userId: string) => request<Models['TokenDto']>('/auth/demo', 'POST', { userId }),
    me: () => request<Me>('/me'),
    academies: () => request<Academy[]>('/platform/academies'),
    createAcademy: (body: Models['AcademyInput']) => request<Models['AcademyCreatedDto']>('/platform/academies', 'POST', body),
    credentialHandoffs: () => request<Handoff[]>('/platform/credential-handoffs'),
    revealCredentials: (id: string) => request<Models['HandoffSecretDto']>(`/platform/credential-handoffs/${id}/reveal`, 'POST'),
    markCredentialsCopied: (id: string) => request<void>(`/platform/credential-handoffs/${id}/copied`, 'POST'),
    retryCredentialsEmail: (id: string) => request<Handoff>(`/platform/credential-handoffs/${id}/retry-email`, 'POST'),
    setAcademyActive: (id: string, active: boolean) => request<Academy>(`/platform/academies/${id}`, 'PATCH', { active }),
    setAcademySubscription: (id: string, body: Models['SubscriptionInput']) => request<Academy>(`/platform/academies/${id}/subscription`, 'PATCH', body),
    branches: (id: string) => request<Branch[]>(academyPath(id, 'branches')),
    createBranch: (id: string, body: Models['BranchInput']) => request<Branch>(academyPath(id, 'branches'), 'POST', body),
    updateBranch: (id: string, branch: string, body: Models['BranchInput']) => request<Branch>(academyPath(id, `branches/${branch}`), 'PUT', body),
    deleteBranch: (id: string, branch: string) => request<void>(academyPath(id, `branches/${branch}`), 'DELETE'),
    createTable: (id: string, branch: string, name: string) => request<Models['TableDto']>(academyPath(id, `branches/${branch}/tables`), 'POST', { name }),
    updateTable: (id: string, branch: string, table: string, name: string) => request<Models['TableDto']>(academyPath(id, `branches/${branch}/tables/${table}`), 'PUT', { name }),
    deleteTable: (id: string, branch: string, table: string) => request<void>(academyPath(id, `branches/${branch}/tables/${table}`), 'DELETE'),
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
    updateAthlete: (id: string, athlete: string, body: Models['AthleteUpdateInput']) => request<Athlete>(academyPath(id, `athletes/${athlete}`), 'PATCH', body),
    coaches: (id: string) => request<Coach[]>(academyPath(id, 'coaches')),
    createCoach: (id: string, body: Models['CoachInput']) => request<Coach>(academyPath(id, 'coaches'), 'POST', body),
    updateCoach: (id: string, coach: string, body: Models['CoachInput']) => request<Coach>(academyPath(id, `coaches/${coach}`), 'PUT', body),
    batches: (id: string) => request<Batch[]>(academyPath(id, 'batches')),
    createBatch: (id: string, body: Models['BatchInput']) => request<Batch>(academyPath(id, 'batches'), 'POST', body),
    updateBatch: (id: string, batch: string, body: Models['BatchInput']) => request<Batch>(academyPath(id, `batches/${batch}`), 'PUT', body),
    deleteBatch: (id: string, batch: string) => request<void>(academyPath(id, `batches/${batch}`), 'DELETE'),
    dailyAttendance: (id: string, date: string) => request<Models['DailyAttendanceDto'][]>(`${academyPath(id, 'daily-attendance')}?localDate=${encodeURIComponent(date)}`),
    saveDailyAttendance: (id: string, body: Models['DailyAttendanceInput']) => request<void>(academyPath(id, 'daily-attendance'), 'PUT', body),
    invoices: (id: string, month?: string) => request<Invoice[]>(`${academyPath(id, 'invoices')}${month ? `?month=${encodeURIComponent(month)}` : ''}`),
    generateInvoices: (id: string, body: Models['InvoiceGenerateInput']) => request<Invoice[]>(academyPath(id, 'invoices/generate'), 'POST', body),
    updateInvoice: (id: string, invoice: string, body: Models['InvoiceUpdateInput']) => request<Invoice>(academyPath(id, `invoices/${invoice}`), 'PATCH', body),
    payments: (id: string) => request<Payment[]>(academyPath(id, 'payments')),
    createPayment: (id: string, body: Models['PaymentInput']) => request<Payment>(academyPath(id, 'payments'), 'POST', body),
    updatePayment: (id: string, payment: string, body: Models['PaymentInput']) => request<Payment>(academyPath(id, `payments/${payment}`), 'PUT', body),
    deletePayment: (id: string, payment: string) => request<void>(academyPath(id, `payments/${payment}`), 'DELETE'),
    refunds: (id: string) => request<Models['RefundDto'][]>(academyPath(id, 'refunds')),
    createRefund: (id: string, payment: string, body: Models['RefundInput']) => request<Models['RefundDto']>(academyPath(id, `payments/${payment}/refunds`), 'POST', body),
    expenses: (id: string) => request<Expense[]>(academyPath(id, 'expenses')),
    createExpense: (id: string, body: Models['ExpenseInput']) => request<Expense>(academyPath(id, 'expenses'), 'POST', body),
    updateExpense: (id: string, expense: string, body: Models['ExpenseInput']) => request<Expense>(academyPath(id, `expenses/${expense}`), 'PUT', body),
    deleteExpense: (id: string, expense: string) => request<void>(academyPath(id, `expenses/${expense}`), 'DELETE'),
    financeSummary: (id: string, start: string, end: string) => request<FinanceSummary>(`${academyPath(id, 'finance-summary')}?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`),
    sessions: (id: string) => request<Models['SessionDto'][]>(academyPath(id, 'sessions')),
    createSession: (id: string, body: Models['SessionInput']) => request<Models['SessionDto']>(academyPath(id, 'sessions'), 'POST', body),
    addRoster: (id: string, session: string, athleteId: string) => request<void>(academyPath(id, `sessions/${session}/roster`), 'POST', { athleteId }),
    markAttendance: (id: string, session: string, athlete: string, body: Models['AttendanceInput']) => request<Models['AttendanceDto']>(academyPath(id, `sessions/${session}/attendance/${athlete}`), 'PUT', body),
    createQr: (id: string, body: Models['QrInput']) => request<Models['QrDto']>(academyPath(id, 'attendance-qr'), 'POST', body),
    redeemQr: (body: Models['RedeemQrInput']) => request<Models['AttendanceDto']>('/attendance-qr/redeem', 'POST', body),
  };
}
