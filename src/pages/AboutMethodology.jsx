export function AboutMethodology({ setView }) {
  const apiRows = [
    ['Search API', 'GET /api/search', 'Risk score, confidence, matching reports'],
    ['Report API', 'POST /api/reports', 'Validated community report creation'],
    ['NLP API', 'POST /api/analyze/job', 'Fake job text score and reasons'],
    ['Stats API', 'GET /api/stats', 'Charts, state heatmap, platform metrics'],
  ];
  const outcomes = [
    ['Before trusting', 'Student searches number/message and sees prior reports.'],
    ['Before paying', 'NLP flags registration fee, UPI request and no-interview promise.'],
    ['After reporting', 'Report enters community feed, live ticker and moderation queue.'],
    ['For college', 'Placement cells can review campus reports and repeated scam patterns.']
  ];

  return (
    <main className="demo-page">
      <section className="demo-hero panel">
        <div>
          <p className="eyebrow">About Scrutnix</p>
          <h1>A scam-checking platform for students, job seekers, and colleges.</h1>
          <p>This page explains how Scrutnix works: architecture, APIs, dataset strategy, NLP, risk score methodology, moderation workflow, and student impact.</p>
          <div className="hero-actions">
            <button className="primary" onClick={() => setView('home')}>Open live product</button>
            <button className="secondary-cta" onClick={() => setView('research')}>Explain algorithm</button>
          </div>
        </div>
        <div className="demo-scoreboard">
          <div><strong>31+</strong><span>API-seeded reports</span></div>
          <div><strong>5</strong><span>Backend service layers</span></div>
          <div><strong>6</strong><span>Core API families</span></div>
          <div><strong>4</strong><span>Dataset sources</span></div>
        </div>
      </section>

      <section className="architecture panel">
        <div className="panel-kicker">System architecture</div>
        <h2>How Scrutnix works end to end</h2>
        <div className="arch-grid">
          <ArchNode title="React Frontend" items={['Search UI', 'Reports feed', 'Job analyzer', 'Charts']} />
          <ArchNode title="Flask Backend" items={['Auth', 'Reports', 'Search', 'Stats']} />
          <ArchNode title="Risk Engine" items={['Bayesian votes', 'Trust', 'Recency', 'Proof']} />
          <ArchNode title="NLP Layer" items={['Scam phrases', 'Negation', 'Similarity', 'Summary']} />
          <ArchNode title="Database" items={['Users', 'Reports', 'Votes', 'Comments']} />
        </div>
      </section>

      <section className="grid two showcase-grid">
        <div className="panel">
          <div className="panel-kicker">Backend endpoints</div>
          <h2>API Work Completed</h2>
          <div className="api-table">
            {apiRows.map(([name, route, output]) => (
              <div className="api-row" key={route}>
                <strong>{name}</strong>
                <code>{route}</code>
                <span>{output}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="panel">
          <div className="panel-kicker">Student impact</div>
          <h2>How a student avoids a scam</h2>
          <div className="outcome-list">
            {outcomes.map(([title, text], index) => (
              <div className="outcome-row" key={title}>
                <b>{index + 1}</b>
                <div><strong>{title}</strong><span>{text}</span></div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="demo-proof-grid">
        <div className="proof-tile">
          <strong>Research-backed score</strong>
          <span>Uses severity, recency decay, Bayesian vote confidence, reporter trust, proof level and NLP signals.</span>
        </div>
        <div className="proof-tile">
          <strong>Dataset strategy</strong>
          <span>Community reports, spam examples, fake-job patterns, and campus reports.</span>
        </div>
        <div className="proof-tile">
          <strong>Abuse prevention</strong>
          <span>Login-required reporting, one vote per report, phone masking, confidence thresholds and trust scoring.</span>
        </div>
        <div className="proof-tile">
          <strong>Transparent methodology</strong>
          <span>Live reports ticker, charts, heatmap, moderation queue, case studies and methodology documents.</span>
        </div>
      </section>
    </main>
  );
}

function ArchNode({ title, items }) {
  return (
    <div className="arch-node">
      <strong>{title}</strong>
      {items.map((item) => <span key={item}>{item}</span>)}
    </div>
  );
}
