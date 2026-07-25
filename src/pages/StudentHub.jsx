import { DEMO_REPORTS } from '../data/demoData';

export function StudentHub({ setView }) {
  const checklist = [
    ['No payment before interview', 'Reject registration, kit, training, software or security fees.'],
    ['Verify company source', 'Check official careers page and company domain email.'],
    ['Protect documents', 'Do not send Aadhaar, PAN, bank passbook or OTP before verification.'],
    ['Ask campus cell', 'Share suspicious offers with a placement cell or trusted campus coordinator.']
  ];
  const alerts = DEMO_REPORTS.filter((item) => ['job_fraud', 'phishing', 'identity_theft'].includes(item.category)).slice(0, 5);

  return (
    <main className="student-page">
      <section className="student-hero panel">
        <div>
          <p className="eyebrow">Student safety hub</p>
          <h1>Know if a job offer is fake before you pay, share documents, or trust the caller.</h1>
          <p>This section is made for students of any college: check an offer, learn red flags, see live campus alerts, and report suspicious recruiters.</p>
          <div className="hero-actions">
            <button className="primary" onClick={() => setView('home')}>Check number or message</button>
            <button className="secondary-cta" onClick={() => setView('report')}>Report suspicious offer</button>
          </div>
        </div>
        <div className="student-phone">
          <div className="student-phone-head">Fake offer scanner</div>
          <div className="scanner-line"><span>Registration fee</span><b>High risk</b></div>
          <div className="scanner-line"><span>No interview</span><b>High risk</b></div>
          <div className="scanner-line"><span>Aadhaar/PAN request</span><b>Critical</b></div>
          <div className="student-verdict">Do not pay. Verify first.</div>
        </div>
      </section>

      <section className="student-grid">
        <div className="panel">
          <div className="panel-kicker">Student checklist</div>
          <h2>Before accepting any offer</h2>
          <div className="student-checklist">
            {checklist.map(([title, text]) => (
              <button type="button" className="check-card" key={title} onClick={() => setView('research')}>
                <strong>{title}</strong>
                <span>{text}</span>
              </button>
            ))}
          </div>
        </div>
        <div className="panel">
          <div className="panel-kicker">Campus alerts</div>
          <h2>Recent risks students should know</h2>
          <div className="student-alert-list">
            {alerts.map((item) => (
              <button type="button" key={item.id} className="student-alert-row" onClick={() => setView('community')}>
                <strong>{item.category.replace('_', ' ')}</strong>
                <span>{item.city}, {item.state}</span>
                <b>{item.risk}%</b>
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="student-actions">
        <button type="button" onClick={() => setView('home')}>
          <strong>1. Search</strong>
          <span>Paste number, email, or message.</span>
        </button>
        <button type="button" onClick={() => setView('community')}>
          <strong>2. Compare</strong>
          <span>See matching community reports.</span>
        </button>
        <button type="button" onClick={() => setView('community')}>
          <strong>3. Learn</strong>
          <span>View scam reports submitted by the community.</span>
        </button>
        <button type="button" onClick={() => setView('report')}>
          <strong>4. Report</strong>
          <span>Help other students avoid the same scam.</span>
        </button>
      </section>
      <section className="panel student-bot-panel">
        <div className="panel-kicker">Ask Scrutnix Guide</div>
        <h2>Questions students can ask</h2>
        <p className="muted">Use the chatbot button at the bottom-right for instant guidance like: "Is this a scam?", "What should I do next?", or "How do I protect my classmates?"</p>
        <div className="bot-question-grid">
          <button type="button" onClick={() => setView('home')}>Check this number or message</button>
          <button type="button" onClick={() => setView('report')}>I want to report a scam</button>
          <button type="button" onClick={() => setView('community')}>Show community reports</button>
          <button type="button" onClick={() => setView('report')}>Submit a campus scam report</button>
        </div>
      </section>
    </main>
  );
}
