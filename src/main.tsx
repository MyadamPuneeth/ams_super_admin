import { StrictMode, useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { createApi, type Academy, type Me } from '@ams/api-client';
import './style.css';

// Keep the demo credential scoped to this browser tab rather than persisting it.
const api = createApi(() => sessionStorage.getItem('ams.super.token'));

function App() {
  const [me, setMe] = useState<Me>();
  const [items, setItems] = useState<Academy[]>([]);
  const [message, setMessage] = useState('');

  const load = async () => {
    try {
      const currentUser = await api.me();
      // Do not render platform controls until the API confirms owner access.
      if (!currentUser.platformOwner) throw new Error('Platform owner access is required.');
      setMe(currentUser);
      setItems(await api.academies());
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Could not load platform');
    }
  };

  useEffect(() => {
    void load();
  }, []);

  if (!me) {
    return <main><h1>AMS Platform</h1><p>Separate onboarding and workspace status controls.</p><button onClick={async () => {
      const token = await api.demo('44444444-4444-4444-8444-444444444444');
      sessionStorage.setItem('ams.super.token', token.accessToken);
      void load();
    }}>Open platform admin</button>{message && <p role="alert">{message}</p>}</main>;
  }

  return <main><header><b>AMS Platform</b><button onClick={() => {
    sessionStorage.removeItem('ams.super.token');
    setMe(undefined);
  }}>Sign out</button></header><h1>Academies</h1><p>Platform administration cannot access academy records.</p><section>{items.map(academy => <article key={academy.id}><div><b>{academy.name}</b><span>{academy.slug}</span></div><button onClick={async () => {
    await api.setAcademyActive(academy.id, !academy.active);
    void load();
  }}>{academy.active ? 'Suspend' : 'Activate'}</button></article>)}</section></main>;
}

createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>);
