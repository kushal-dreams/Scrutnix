import { useState } from 'react';
import { DEMO_REPORTS } from '../data/demoData';
import { api } from '../services/api';

export function TopLiveTicker({ reports }) {
  const items = (reports.length ? reports : DEMO_REPORTS).slice(0, 10);
  const loop = [...items, ...items];

  return (
    <div className="ticker-shell">
      <div className="ticker-label">
        <span className="pulse-dot" />
        Live reports
      </div>
      <div className="ticker-track">
        <div className="ticker-line">
          {loop.map((report, index) => (
            <span className="ticker-item" key={`${report.id}-${index}`}>
              <strong>{String(report.category).replace('_', ' ')}</strong>
              <span>{report.city || 'India'}, {report.state || 'Community'}</span>
              <em>{report.masked_target}</em>
              <b>{report.upvotes || 0} confirmed</b>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

export function Header({ view, setView, user, setUser, notify }) {
  const navItems = [
    ['home', 'Home'],
    ['student', 'Student Hub'],
    ['analyzer', 'Job Analyzer'],
    ['community', 'Community'],
    ['report', 'Report Scam'],
    ['research', 'Research'],
    ['about', 'About']
  ];

  return (
    <header className="topbar">
      <button className="brand" onClick={() => setView('home')}>
        <span className="logo">S</span>
        <span>Scrutnix</span>
      </button>
      <nav>
        {navItems.map(([item, label]) => (
          <button key={item} className={view === item ? 'active' : ''} onClick={() => setView(item)}>
            {label}
          </button>
        ))}
      </nav>
      <AuthBox user={user} setUser={setUser} notify={notify} />
    </header>
  );
}

function AuthBox({ user, setUser, notify }) {
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ identifier: '', password: '', username: '', nickname: '', phone: '', otp: '' });
  const [mode, setMode] = useState('login');
  const [otpSent, setOtpSent] = useState(false);

  if (user) {
    return (
      <div className="auth-user">
        <span>{user.nickname || user.username || user.name}</span>
        <button onClick={() => { localStorage.removeItem('scrutinix_token'); setUser(null); }}>Logout</button>
      </div>
    );
  }

  const submit = async (e) => {
    e.preventDefault();
    try {
      if (mode === 'signup' && !otpSent) {
        await api('/auth/send-otp', { method: 'POST', body: JSON.stringify({ phone: form.phone }) });
        setOtpSent(true);
        notify('OTP created. Check the backend terminal for the code.');
        return;
      }

      let data;
      if (mode === 'signup') {
        await api('/auth/verify-otp', {
          method: 'POST',
          body: JSON.stringify({ phone: form.phone, otp: form.otp })
        });
        data = await api('/auth/signup', {
          method: 'POST',
          body: JSON.stringify({
            username: form.username,
            nickname: form.nickname,
            phone: form.phone,
            password: form.password
          })
        });
      } else {
        data = await api('/auth/login', { method: 'POST', body: JSON.stringify(form) });
      }
      localStorage.setItem('scrutinix_token', data.token);
      setUser(data.user);
      setOpen(false);
      notify(mode === 'signup' ? 'Account created successfully' : 'Logged in successfully');
    } catch (err) {
      notify(err.message);
    }
  };

  return (
    <div className="auth">
      <button className="primary small" onClick={() => setOpen(!open)}>Login</button>
      {open && (
        <form className="auth-panel" onSubmit={submit}>
          <div className="segmented">
            <button type="button" className={mode === 'login' ? 'active' : ''} onClick={() => { setMode('login'); setOtpSent(false); }}>Login</button>
            <button type="button" className={mode === 'signup' ? 'active' : ''} onClick={() => { setMode('signup'); setOtpSent(false); }}>Signup</button>
          </div>
          {mode === 'signup' && (
            <>
              <input placeholder="Username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
              <input placeholder="Display name" value={form.nickname} onChange={(e) => setForm({ ...form, nickname: e.target.value })} />
              <input placeholder="10-digit phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
              {otpSent && <input placeholder="OTP from backend terminal" value={form.otp} onChange={(e) => setForm({ ...form, otp: e.target.value })} />}
            </>
          )}
          {mode === 'login' && <input placeholder="Username or phone" value={form.identifier} onChange={(e) => setForm({ ...form, identifier: e.target.value })} />}
          <input placeholder="Password" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          <button className="primary">{mode === 'signup' && !otpSent ? 'Send OTP' : 'Continue'}</button>
        </form>
      )}
    </div>
  );
}

function getGuideAnswer(question) {
  const q = question.toLowerCase();
  if (q.includes('know') || q.includes('scam') || q.includes('fake') || q.includes('identify')) {
    return {
      text: 'A student can suspect a scam if the offer asks for registration/training/security fee, promises joining without interview, uses WhatsApp/Telegram only, asks for Aadhaar/PAN/bank/OTP, creates urgency, or uses a free email instead of an official company domain.',
      action: 'Check the number/message now',
      view: 'home'
    };
  }
  if (q.includes('next') || q.includes('do') || q.includes('received') || q.includes('pay')) {
    return {
      text: 'Next steps: do not pay, do not share documents or OTP, screenshot the message, search the number/message on Scrutnix, verify through the official company website, and ask your placement cell or trusted campus coordinator if unsure.',
      action: 'Open student checklist',
      view: 'student'
    };
  }
  if (q.includes('protect') || q.includes('other') || q.includes('class') || q.includes('friend')) {
    return {
      text: 'Protect others by submitting a report with the number/message, proof level, city/state, and scam category. The report appears in the community feed and helps the risk score warn future students.',
      action: 'Report this scam',
      view: 'report'
    };
  }
  if (q.includes('faculty') || q.includes('guide') || q.includes('project')) {
    return {
      text: 'Open the About section. It explains architecture, APIs, risk algorithm, NLP layer, dataset sources, moderation workflow, and student impact in a public-friendly way.',
      action: 'Open about platform',
      view: 'about'
    };
  }
  return {
    text: 'I can help with scam red flags, next steps, reporting, campus alerts, and project explanation. Try asking: "How will I know this is a scam?", "What should I do next?", or "How can I protect other students?"',
    action: 'Open student hub',
    view: 'student'
  };
}

export function GuideBot({ setView }) {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState('How will a student know this is a scam?');
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Hi, I am Scrutnix Guide. Ask me how to identify a fake job offer, what to do next, or how to protect other students.', action: 'Open student hub', view: 'student' }
  ]);

  const ask = (question = input) => {
    const trimmed = question.trim();
    if (!trimmed) return;
    const answer = getGuideAnswer(trimmed);
    setMessages((items) => [...items, { role: 'user', text: trimmed }, { role: 'bot', ...answer }]);
    setInput('');
    setOpen(true);
  };

  const quick = [
    'How will a student know this is a scam?',
    'What should they do next?',
    'How can they protect other students?'
  ];

  return (
    <div className={`guidebot ${open ? 'open' : ''}`}>
      {open && (
        <div className="guidebot-panel">
          <div className="guidebot-head">
            <div><strong>Scrutnix Guide</strong><span>Student scam assistant</span></div>
            <button type="button" onClick={() => setOpen(false)}>Close</button>
          </div>
          <div className="guidebot-messages">
            {messages.map((msg, index) => (
              <div className={`guide-msg ${msg.role}`} key={`${msg.role}-${index}`}>
                <p>{msg.text}</p>
                {msg.role === 'bot' && msg.action && (
                  <button type="button" onClick={() => setView(msg.view)}>{msg.action}</button>
                )}
              </div>
            ))}
          </div>
          <div className="guidebot-quick">
            {quick.map((item) => <button type="button" key={item} onClick={() => ask(item)}>{item}</button>)}
          </div>
          <form className="guidebot-input" onSubmit={(e) => { e.preventDefault(); ask(); }}>
            <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask about a suspicious job offer..." />
            <button className="primary">Ask</button>
          </form>
        </div>
      )}
      <button className="guidebot-toggle" type="button" onClick={() => setOpen(!open)}>
        {open ? 'Guide open' : 'Ask Scrutnix Guide'}
      </button>
    </div>
  );
}

export function Footer() {
  return <footer>Scrutnix - Community scam checking with React, Flask, and SQLite</footer>;
}
