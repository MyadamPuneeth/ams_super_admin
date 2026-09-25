import { StrictMode, useEffect, useMemo, useRef, useState, type FormEvent, type ReactNode } from 'react';
import { createRoot } from 'react-dom/client';
import { ApiError, createApi, type Academy, type Handoff, type Me } from '@ams/api-client';
import './style.css';
import './handoff.css';

const api = createApi(() => null);
const plans = ['STARTER', 'PRO', 'ENTERPRISE'] as const;
const statuses = ['TRIAL', 'ACTIVE', 'PAST_DUE', 'CANCELLED', 'EXPIRED'] as const;
const today = () => new Date().toISOString().slice(0, 10);
const inThirtyDays = () => new Date(Date.now() + 30 * 86_400_000).toISOString().slice(0, 10);
const label = (value: string) => value.replace('_', ' ').toLowerCase().replace(/^./, character => character.toUpperCase());

function Mark() {
  return <span className="mark" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M7 4h10v4H7zM4 10h16v4H4zM8 16h8v4H8z" /></svg></span>;
}

function Modal({ title, children, onClose }: { title: string; children: ReactNode; onClose: () => void }) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => { const dialog = ref.current; if (dialog && !dialog.open) dialog.showModal(); return () => dialog?.close(); }, []);
  return <dialog ref={ref} onCancel={event => { event.preventDefault(); onClose(); }} onClick={event => { if (event.target === ref.current) onClose(); }}>
    <div className="dialog-card">
      <div className="dialog-title"><h2>{title}</h2><button className="icon-button" type="button" aria-label="Close dialog" onClick={onClose}>×</button></div>
      {children}
    </div>
  </dialog>;
}

function SignIn({ onSuccess }: { onSuccess: () => Promise<void> }) {
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setBusy(true); setMessage('');
    const data = new FormData(event.currentTarget);
    try {
      await api.platformSignIn({ username: String(data.get('username')), password: String(data.get('password')) });
      await onSuccess();
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Could not sign in.'); }
    finally { setBusy(false); }
  };
  return <main className="sign-in-page">
    <section className="welcome-panel" aria-label="AMS platform introduction">
      <div className="brand light"><Mark /><span>AMS Platform</span></div>
      <div className="welcome-copy"><span className="eyebrow">Academy operations, simplified</span><h1>Lead every academy from one place.</h1><p>Onboard organizations, manage access and keep subscriptions moving—all from a secure command center.</p></div>
      <div className="orbit orbit-one" aria-hidden="true" /><div className="orbit orbit-two" aria-hidden="true" />
    </section>
    <section className="sign-in-panel">
      <form className="sign-in-card" onSubmit={submit}>
        <div><span className="eyebrow purple">Platform owners</span><h2>Welcome back</h2><p>Sign in to manage your academy network.</p></div>
        <label>Username<input name="username" autoComplete="username" minLength={3} maxLength={50} pattern="[A-Za-z0-9._-]+" required autoFocus /></label>
        <label>Password<input name="password" type="password" autoComplete="current-password" minLength={12} maxLength={128} required /></label>
        {message && <p className="form-error" role="alert">{message}</p>}
        <button className="primary full" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</button>
        <p className="secure-note"><span aria-hidden="true">●</span> Secure platform-owner access</p>
      </form>
    </section>
  </main>;
}

function CredentialDialog({ handoff: initial, initialPassword = '', onClose, onSaved }: { handoff: Handoff; initialPassword?: string; onClose: () => void; onSaved: () => Promise<void> }) {
  const [handoff, setHandoff] = useState(initial); const [password, setPassword] = useState(initialPassword); const [message, setMessage] = useState(''); const [busy, setBusy] = useState(false);
  useEffect(() => { if (!password) void api.revealCredentials(handoff.id).then(value => setPassword(value.temporaryPassword)).catch(error => setMessage(error instanceof Error ? error.message : 'Could not reveal credentials.')); }, [handoff.id, password]);
  const copy = async () => {
    setBusy(true); setMessage('');
    try { await navigator.clipboard.writeText(password); await api.markCredentialsCopied(handoff.id); setHandoff({ ...handoff, copied: true }); await onSaved(); }
    catch (error) { setMessage(error instanceof Error ? error.message : 'Could not copy the password.'); }
    finally { setBusy(false); }
  };
  const retry = async () => {
    setBusy(true); setMessage('');
    try { const updated = await api.retryCredentialsEmail(handoff.id); setHandoff(updated); await onSaved(); }
    catch (error) { setMessage(error instanceof Error ? error.message : 'Could not send the email.'); }
    finally { setBusy(false); }
  };
  const close = () => { if (handoff.copied) onClose(); else setMessage('Copy the temporary password before closing this window.'); };
  return <Modal title={`${handoff.academyName} credentials`} onClose={close}><div className="dialog-form">
    <p className="dialog-lead">These credentials remain recoverable until the password is copied and the onboarding email is sent.</p>
    <div className="form-grid"><label>Username<input value={handoff.username} readOnly /></label><label>Temporary password<input aria-label="Temporary password" value={password} readOnly onFocus={event => event.currentTarget.select()} /></label></div>
    <p className={handoff.emailSent ? 'success-note' : 'form-error'}>{handoff.emailSent ? `Credentials emailed to ${handoff.email}.` : `Email not sent: ${handoff.emailError || 'SMTP is unavailable.'}`}</p>
    {message && <p className="form-error" role="alert">{message}</p>}
    <div className="dialog-actions">{!handoff.emailSent && <button className="secondary" type="button" disabled={busy} onClick={() => void retry()}>Retry email</button>}<button className="secondary" type="button" disabled={busy || !password} onClick={() => void copy()}>{handoff.copied ? 'Copy again' : 'Copy password'}</button><button className="primary" type="button" disabled={!handoff.copied} onClick={onClose}>Done</button></div>
  </div></Modal>;
}

function AcademyDialog({ onClose, onSaved }: { onClose: () => void; onSaved: () => Promise<void> }) {
  const [message, setMessage] = useState(''); const [busy, setBusy] = useState(false); const [credentials, setCredentials] = useState<{ handoff: Handoff; password: string }>();
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setBusy(true); setMessage(''); const data = new FormData(event.currentTarget);
    try {
      const password = String(data.get('password'));
      if (password !== String(data.get('confirmPassword'))) throw new Error('The passwords do not match.');
      const created = await api.createAcademy({ name: String(data.get('name')), slug: String(data.get('slug')), adminName: String(data.get('adminName')), adminEmail: String(data.get('email')), adminUsername: String(data.get('username')), temporaryPassword: password, subscriptionPlan: String(data.get('plan')) as typeof plans[number], subscriptionStatus: 'TRIAL', subscriptionStartsOn: String(data.get('starts')), subscriptionEndsOn: String(data.get('ends')) || null });
      await onSaved(); setCredentials({ handoff: created.handoff, password });
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Could not add the academy.'); }
    finally { setBusy(false); }
  };
  if (credentials) return <CredentialDialog handoff={credentials.handoff} initialPassword={credentials.password} onClose={onClose} onSaved={onSaved} />;
  return <Modal title="Add a new academy" onClose={onClose}><form className="dialog-form" onSubmit={submit}>
    <div className="form-grid"><label>Academy name<input name="name" minLength={2} maxLength={100} required autoFocus /></label><label>Workspace slug<input name="slug" minLength={3} maxLength={50} pattern="[a-z0-9]+(?:-[a-z0-9]+)*" placeholder="city-champions" required /></label></div>
    <div className="form-grid"><label>Administrator name<input name="adminName" minLength={2} maxLength={100} autoComplete="name" required /></label><label>Administrator email<input name="email" type="email" autoComplete="email" required /></label></div>
    <div className="form-grid"><label>Administrator username<input name="username" minLength={3} maxLength={50} pattern="[A-Za-z0-9._-]+" autoComplete="off" required /></label><span /></div>
    <div className="form-grid"><label>Temporary password<input name="password" type="password" minLength={12} maxLength={128} autoComplete="new-password" required /></label><label>Confirm password<input name="confirmPassword" type="password" minLength={12} maxLength={128} autoComplete="new-password" required /></label></div>
    <div className="form-grid"><label>Starting plan<select name="plan" defaultValue="STARTER">{plans.map(plan => <option key={plan}>{plan}</option>)}</select></label><label>Subscription status<input value="Trial" disabled /></label></div>
    <div className="form-grid"><label>Starts on<input name="starts" type="date" defaultValue={today()} required /></label><label>Trial ends on<input name="ends" type="date" defaultValue={inThirtyDays()} /></label></div>
    {message && <p className="form-error" role="alert">{message}</p>}
    <div className="dialog-actions"><button type="button" className="secondary" onClick={onClose}>Cancel</button><button className="primary" disabled={busy}>{busy ? 'Creating…' : 'Create academy'}</button></div>
  </form></Modal>;
}

function SubscriptionDialog({ academy, onClose, onSaved }: { academy: Academy; onClose: () => void; onSaved: () => Promise<void> }) {
  const [message, setMessage] = useState(''); const [busy, setBusy] = useState(false);
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setBusy(true); setMessage(''); const data = new FormData(event.currentTarget);
    try {
      await api.setAcademySubscription(academy.id, { plan: String(data.get('plan')) as typeof plans[number], status: String(data.get('status')) as typeof statuses[number], startsOn: String(data.get('starts')), endsOn: String(data.get('ends')) || null });
      await onSaved(); onClose();
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Could not update the subscription.'); }
    finally { setBusy(false); }
  };
  return <Modal title={`Manage ${academy.name}`} onClose={onClose}><form className="dialog-form" onSubmit={submit}>
    <p className="dialog-lead">Update the academy’s current subscription. Billing remains managed outside AMS.</p>
    <div className="form-grid"><label>Plan<select name="plan" defaultValue={academy.subscriptionPlan}>{plans.map(plan => <option key={plan}>{plan}</option>)}</select></label><label>Status<select name="status" defaultValue={academy.subscriptionStatus}>{statuses.map(status => <option key={status} value={status}>{label(status)}</option>)}</select></label></div>
    <div className="form-grid"><label>Starts on<input name="starts" type="date" defaultValue={academy.subscriptionStartsOn} required /></label><label>Renews or ends on<input name="ends" type="date" defaultValue={academy.subscriptionEndsOn ?? ''} /></label></div>
    {message && <p className="form-error" role="alert">{message}</p>}
    <div className="dialog-actions"><button type="button" className="secondary" onClick={onClose}>Cancel</button><button className="primary" disabled={busy}>{busy ? 'Saving…' : 'Save subscription'}</button></div>
  </form></Modal>;
}

function Dashboard({ me, academies, handoffs, reload, signOut }: { me: Me; academies: Academy[]; handoffs: Handoff[]; reload: () => Promise<void>; signOut: () => Promise<void> }) {
  const [query, setQuery] = useState(''); const [adding, setAdding] = useState(false); const [editing, setEditing] = useState<Academy>(); const [handoff, setHandoff] = useState<Handoff>(); const [message, setMessage] = useState('');
  const filtered = useMemo(() => { const value = query.trim().toLowerCase(); return academies.filter(item => !value || item.name.toLowerCase().includes(value) || item.slug.toLowerCase().includes(value)); }, [academies, query]);
  const toggle = async (academy: Academy) => {
    const action = academy.active ? 'suspend' : 'activate';
    if (!window.confirm(`${action === 'suspend' ? 'Suspend' : 'Activate'} ${academy.name}?`)) return;
    setMessage(''); try { await api.setAcademyActive(academy.id, !academy.active); await reload(); } catch (error) { setMessage(error instanceof Error ? error.message : `Could not ${action} the academy.`); }
  };
  return <div className="app-shell">
    <aside><div className="brand"><Mark /><span>AMS Platform</span></div><nav aria-label="Main navigation"><a className="active" href="#academies"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 4h6v6H4zm10 0h6v6h-6zM4 14h6v6H4zm10 0h6v6h-6z" /></svg>Academies</a></nav><div className="aside-user"><span>{me.name.slice(0, 1).toUpperCase()}</span><div><b>{me.name}</b><small>Platform owner</small></div></div></aside>
    <main className="dashboard" id="academies">
      <header><div className="mobile-brand"><Mark /><b>AMS</b></div><div className="header-user"><span>{me.name}</span><button className="text-button" onClick={() => void signOut()}>Sign out</button></div></header>
      <div className="content">
        <section className="hero"><div><span className="eyebrow purple">Academy network</span><h1>Good to see you, {me.name.split(' ')[0]}.</h1><p>Manage every academy, subscription and access status from one place.</p></div><button className="primary" onClick={() => setAdding(true)}>+ Add academy</button></section>
        <section className="metrics" aria-label="Academy summary"><article><span className="metric-icon violet" aria-hidden="true">A</span><div><b>{academies.length}</b><small>Total academies</small></div></article><article><span className="metric-icon green" aria-hidden="true">✓</span><div><b>{academies.filter(item => item.active).length}</b><small>Active academies</small></div></article><article><span className="metric-icon orange" aria-hidden="true">S</span><div><b>{academies.filter(item => item.subscriptionStatus === 'TRIAL').length}</b><small>Active trials</small></div></article></section>
        {!!handoffs.length && <section className="handoff-panel" aria-labelledby="handoff-title"><div><span className="eyebrow purple">Action required</span><h2 id="handoff-title">Finish credential handoff</h2><p>Temporary credentials remain recoverable until copied and successfully emailed.</p></div><div className="handoff-list">{handoffs.map(item => <button className="secondary" key={item.id} onClick={() => setHandoff(item)}>{item.academyName}<small>{item.emailSent ? 'Copy pending' : 'Email and copy pending'}</small></button>)}</div></section>}
        <section className="academy-panel"><div className="panel-header"><div><h2>Registered academies</h2><p>{filtered.length} of {academies.length} academies</p></div><label className="search"><span className="sr-only">Search academies</span><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m21 21-4.4-4.4m2.4-5.1a7.5 7.5 0 1 1-15 0 7.5 7.5 0 0 1 15 0Z" /></svg><input type="search" placeholder="Search name or slug" value={query} onChange={event => setQuery(event.target.value)} /></label></div>
          {message && <p className="form-error table-error" role="alert">{message}</p>}
          <div className="table-wrap"><table><thead><tr><th>Academy</th><th>Subscription</th><th>Renewal</th><th>Access</th><th><span className="sr-only">Actions</span></th></tr></thead><tbody>{filtered.map(academy => <tr key={academy.id}><td data-label="Academy"><div className="academy-name"><span>{academy.name.slice(0, 1).toUpperCase()}</span><div><b>{academy.name}</b><small>/{academy.slug}</small></div></div></td><td data-label="Subscription"><b>{label(academy.subscriptionPlan)}</b><span className={`badge ${academy.subscriptionStatus.toLowerCase()}`}>{label(academy.subscriptionStatus)}</span></td><td data-label="Renewal">{academy.subscriptionEndsOn ? new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeZone: 'UTC' }).format(new Date(`${academy.subscriptionEndsOn}T00:00:00Z`)) : 'Not set'}</td><td data-label="Access"><span className={`status ${academy.active ? 'on' : 'off'}`}><i />{academy.active ? 'Active' : 'Suspended'}</span></td><td data-label="Actions"><div className="row-actions"><button className="secondary compact" onClick={() => setEditing(academy)}>Manage plan</button><button className={`text-button ${academy.active ? 'danger' : ''}`} onClick={() => void toggle(academy)}>{academy.active ? 'Suspend' : 'Activate'}</button></div></td></tr>)}</tbody></table></div>
          {!filtered.length && <div className="empty"><h3>No academies found</h3><p>Try a different name or workspace slug.</p></div>}
        </section>
      </div>
    </main>
    {adding && <AcademyDialog onClose={() => setAdding(false)} onSaved={reload} />}{editing && <SubscriptionDialog academy={editing} onClose={() => setEditing(undefined)} onSaved={reload} />}{handoff && <CredentialDialog handoff={handoff} onClose={() => setHandoff(undefined)} onSaved={reload} />}
  </div>;
}

function App() {
  const [me, setMe] = useState<Me>(); const [academies, setAcademies] = useState<Academy[]>([]); const [handoffs, setHandoffs] = useState<Handoff[]>([]); const [checking, setChecking] = useState(true); const [message, setMessage] = useState('');
  const load = async () => {
    try { const current = await api.me(); if (!current.platformOwner) throw new Error('Platform owner access is required.'); const [academyList, pending] = await Promise.all([api.academies(), api.credentialHandoffs()]); setMe(current); setAcademies(academyList); setHandoffs(pending); setMessage(''); }
    catch (error) { setMe(undefined); setAcademies([]); setHandoffs([]); if (!(error instanceof ApiError && error.status === 401)) setMessage(error instanceof Error ? error.message : 'Could not load the platform.'); }
    finally { setChecking(false); }
  };
  useEffect(() => { void load(); }, []);
  if (checking) return <main className="loading"><Mark /><p>Loading AMS Platform…</p></main>;
  if (!me) return <><SignIn onSuccess={load} />{message && <div className="global-error" role="alert">{message}</div>}</>;
  return <Dashboard me={me} academies={academies} handoffs={handoffs} reload={load} signOut={async () => { await api.platformSignOut(); setMe(undefined); setAcademies([]); setHandoffs([]); }} />;
}

createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>);
