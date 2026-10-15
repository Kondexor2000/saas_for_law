import React, { useEffect, useState } from 'react';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const roleNames = { client: 'Panel klienta', lawyer: 'Panel prawnika', administrator: 'Panel administratora' };

export default function App() {
  const [user, setUser] = useState(null);
  const [cases, setCases] = useState([]);
  const [lawyers, setLawyers] = useState([]);
  const [form, setForm] = useState({ title: '', category: '', description: '', client_phone: '', client_email: '' });
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(true);

  async function csrf() { await fetch(`${API}/csrf/`, { credentials: 'include' }); }
  async function loadCases(currentUser = user) {
    if (!currentUser) return;
    try {
      const response = await fetch(`${API}/cases/`, { credentials: 'include' });
      if (!response.ok) throw new Error('Nie udało się pobrać spraw.');
      setCases(await response.json());
      if (currentUser.role === 'administrator') {
        const lawyerResponse = await fetch(`${API}/lawyers/`, { credentials: 'include' });
        if (lawyerResponse.ok) setLawyers(await lawyerResponse.json());
      } else setLawyers([]);
    } catch { setNotice('Brak połączenia z API lub błąd odczytu danych.'); }
  }

  async function refreshSession() {
    try {
      const response = await fetch(`${API}/auth/me/`, { credentials: 'include' });
      if (!response.ok) { setUser(null); setCases([]); return; }
      const currentUser = await response.json(); setUser(currentUser); await loadCases(currentUser);
    } catch { setNotice('Nie można połączyć się z API PostgreSQL.'); }
    finally { setBusy(false); }
  }
  useEffect(() => { refreshSession(); }, []);

  async function signIn(event) {
    event.preventDefault(); setNotice('');
    try {
      await csrf();
      const response = await fetch(`${API}/auth/login/`, { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') }, body: JSON.stringify(loginForm) });
      const result = await readResponse(response);
      if (!response.ok) throw new Error(result.detail || 'Logowanie nie powiodło się.');
      setUser(result); setLoginForm({ username: '', password: '' }); setNotice(`Zalogowano: ${roleNames[result.role]}.`); await loadCases(result);
    } catch (error) { setNotice(error.message); }
  }

  async function signOut() {
    await csrf();
    await fetch(`${API}/auth/logout/`, { method: 'POST', credentials: 'include', headers: { 'X-CSRFToken': getCookie('csrftoken') } });
    setUser(null); setCases([]); setLawyers([]); setNotice('Wylogowano.');
  }

  async function submitCase(event) {
    event.preventDefault(); setNotice(''); await csrf();
    try {
      const response = await fetch(`${API}/cases/`, { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') }, body: JSON.stringify(form) });
      const result = await readResponse(response);
      if (!response.ok) throw new Error(result.detail || 'Nie udało się wysłać formularza.');
      setForm({ title: '', category: '', description: '', client_phone: '', client_email: '' }); setNotice('Formularz sprawy został wysłany.'); await loadCases();
    } catch (error) { setNotice(error.message); }
  }

  async function assignLawyer(caseId, lawyerId) {
    await csrf();
    try {
      const response = await fetch(`${API}/cases/${caseId}/`, { method: 'PATCH', credentials: 'include', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') }, body: JSON.stringify({ lawyer: lawyerId || null }) });
      const result = await readResponse(response);
      if (!response.ok) throw new Error(result.lawyer?.[0] || result.detail || 'Nie udało się przypisać prawnika.');
      setNotice('Przypisanie prawnika zostało zapisane.'); await loadCases();
    } catch (error) { setNotice(error.message); }
  }

  if (busy) return <main className="shell"><p className="empty">Łączenie z systemem…</p></main>;

  return <main className="shell">
    <header><div className="mark">L</div><div><p className="eyebrow">OBSŁUGA PRAWNA</p><h1>{user ? roleNames[user.role] : 'Portal spraw prawnych'}</h1></div>
      {user ? <div className="account"><span>{user.name || user.username}</span><button className="refresh" onClick={signOut}>Wyloguj</button></div> : <span className="secure">● Bezpieczny panel</span>}</header>
    {notice && <div className="notice" role="status">{notice}</div>}

    {!user ? <>
      <section className="intro"><p className="eyebrow">CENTRUM KLIENTA</p><h2>Opisz swoją sprawę</h2><p>Przekaż najważniejsze informacje. Administrator przydzieli zgłoszenie odpowiedniemu prawnikowi.</p></section>
      <section className="card"><div className="card-title"><span className="number">01</span><div><h3>Formularz sprawy</h3><p>Pola oznaczone * są wymagane.</p></div></div>
        <form onSubmit={submitCase}><label>Adres e-mail *<input required type="email" autoComplete="email" maxLength="254" value={form.client_email} onChange={e=>setForm({...form,client_email:e.target.value})} placeholder="np. jan@example.com"/></label>
          <label>Numer telefonu *<input required type="tel" autoComplete="tel" maxLength="32" value={form.client_phone} onChange={e=>setForm({...form,client_phone:e.target.value})} placeholder="np. +48 123 456 789"/></label>
          <label>Tytuł sprawy *<input required maxLength="200" value={form.title} onChange={e=>setForm({...form,title:e.target.value})} placeholder="Np. analiza umowy najmu"/></label>
          <label>Obszar prawny<input value={form.category} onChange={e=>setForm({...form,category:e.target.value})} placeholder="Np. prawo cywilne"/></label>
          <label>Opis sprawy *<textarea required rows="6" value={form.description} onChange={e=>setForm({...form,description:e.target.value})} placeholder="Opisz sytuację, ważne daty i czego potrzebujesz…"/></label>
          <button type="submit">Wyślij formularz <span>→</span></button></form>
      </section>
      <section className="card login-card"><div className="card-title"><span className="number">02</span><div><h3>Panel kancelarii</h3><p>Logowanie dla administratora i prawników. Konta tworzy administrator.</p></div></div>
        <form onSubmit={signIn}><label>Login<input required autoComplete="username" value={loginForm.username} onChange={e=>setLoginForm({...loginForm,username:e.target.value})} /></label>
          <label>Hasło<input required type="password" autoComplete="current-password" value={loginForm.password} onChange={e=>setLoginForm({...loginForm,password:e.target.value})} /></label>
          <button type="submit">Zaloguj się <span>→</span></button></form>
      </section>
    </> : <>
      <section className="intro"><p className="eyebrow">{user.role === 'lawyer' ? 'PRZYDZIELONE DO CIEBIE' : user.role === 'administrator' ? 'ZARZĄDZANIE SPRAWAMI' : 'CENTRUM KLIENTA'}</p>
        <h2>{user.role === 'lawyer' ? 'Sprawy klientów' : user.role === 'administrator' ? 'Wszystkie zgłoszenia' : 'Opisz swoją sprawę'}</h2>
        <p>{user.role === 'lawyer' ? 'Poniżej znajdziesz sprawy przydzielone do Twojego konta.' : user.role === 'administrator' ? 'Przydziel zgłoszenia do prawników. Konta i role użytkowników zarządzane są w panelu administracyjnym.' : 'Przekaż nam najważniejsze informacje. Administrator przydzieli sprawę odpowiedniemu prawnikowi.'}</p>
      </section>

      {user.role === 'client' && <section className="card"><div className="card-title"><span className="number">01</span><div><h3>Formularz sprawy</h3><p>Pola oznaczone * są wymagane.</p></div></div>
        <form onSubmit={submitCase}><label>Adres e-mail *<input required type="email" autoComplete="email" maxLength="254" value={form.client_email} onChange={e=>setForm({...form,client_email:e.target.value})} placeholder="np. jan@example.com"/></label>
          <label>Numer telefonu *<input required type="tel" autoComplete="tel" maxLength="32" value={form.client_phone} onChange={e=>setForm({...form,client_phone:e.target.value})} placeholder="np. +48 123 456 789"/></label>
          <label>Tytuł sprawy *<input required maxLength="200" value={form.title} onChange={e=>setForm({...form,title:e.target.value})} placeholder="Np. analiza umowy najmu"/></label>
          <label>Obszar prawny<input value={form.category} onChange={e=>setForm({...form,category:e.target.value})} placeholder="Np. prawo cywilne"/></label>
          <label>Opis sprawy *<textarea required rows="6" value={form.description} onChange={e=>setForm({...form,description:e.target.value})} placeholder="Opisz sytuację, ważne daty i czego potrzebujesz…"/></label>
          <button type="submit">Wyślij formularz <span>→</span></button></form>
      </section>}

      <section className="list"><div className="list-head"><h3>{user.role === 'client' ? 'Wysłane sprawy' : 'Lista spraw'}</h3><button className="refresh" onClick={()=>loadCases()}>Odśwież</button></div>
        {cases.length === 0 ? <p className="empty">{user.role === 'lawyer' ? 'Nie masz jeszcze przydzielonych spraw.' : 'Brak spraw do wyświetlenia.'}</p> : cases.map(c=><article className="case" key={c.id}><div className="case-copy"><b>{c.title}</b><p>{c.category || 'Bez kategorii'} · {new Date(c.created_at).toLocaleDateString('pl-PL')}{user.role !== 'client' && c.client_name ? ` · Klient: ${c.client_name}` : ''}</p>
          {user.role !== 'client' && <><p className="description">{c.description}</p><p>Kontakt do klienta: <a href={`mailto:${c.client_email}`}>{c.client_email}</a> · <a href={`tel:${c.client_phone}`}>{c.client_phone}</a></p></>}
          {user.role === 'administrator' && <label className="assign">Przypisz prawnika<select value={c.lawyer || ''} onChange={e=>assignLawyer(c.id,e.target.value)}><option value="">Nieprzypisane</option>{lawyers.map(l=><option key={l.id} value={l.id}>{l.name || l.username}</option>)}</select></label>}
          {user.role === 'lawyer' && c.lawyer_name && <p>Prawnik: {c.lawyer_name}</p>}</div><span className="status">{c.status}</span></article>)}
      </section>
      {user.role === 'administrator' && <p className="admin-link">Tworzenie kont: panel administratora Django pod adresem <a href="http://127.0.0.1:8000/admin/">/admin/</a>.</p>}
    </>}
    <footer>Twoje informacje są dostępne wyłącznie dla Ciebie, administratora i przypisanego prawnika.</footer>
  </main>;
}

function getCookie(name) { return document.cookie.split('; ').find(row => row.startsWith(`${name}=`))?.split('=')[1] || ''; }

async function readResponse(response) {
  const body = await response.text();
  if (!body) return {};
  try { return JSON.parse(body); }
  catch {
    if (!response.ok) throw new Error(`Serwer API zwrócił błąd (${response.status}). Spróbuj ponownie lub skontaktuj się z administratorem.`);
    throw new Error('Serwer API zwrócił nieoczekiwaną odpowiedź.');
  }
}
