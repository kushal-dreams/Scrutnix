import { useState } from 'react';
import {
  CASE_STUDIES,
  COLLEGE_INSIGHTS,
  DEMO_REPORTS,
  DEMO_STATS,
  INGESTION_STEPS,
  MODERATION_QUEUE,
  MONTHLY_TRENDS,
  PLAYBOOKS
} from '../data/demoData';
import { api } from '../services/api';
import { fallbackSearchResult } from '../services/fallbacks';
import { AnalysisResult, RiskResult } from '../components/RiskResults';
import {
  CategoryChart,
  DataSources,
  Feature,
  HighRiskTable,
  LiveFeed,
  Metric,
  StateGrid
} from '../components/DashboardComponents';

export function Home({ stats, reports, refresh, setView, notify }) {
  const activeStats = stats || DEMO_STATS;
  const activeReports = reports.length ? reports : DEMO_REPORTS;
  const [search, setSearch] = useState({ type: 'phone', q: '9876543210' });
  const [result, setResult] = useState(null);
  const [jobText, setJobText] = useState('WhatsApp HR says I am selected for data entry work from home. No interview. Pay registration fee of Rs 799 by UPI and send Aadhaar PAN card for employee ID.');
  const [analysis, setAnalysis] = useState(null);

  const doSearch = async (e) => {
    e.preventDefault();
    try {
      setResult(await api(`/search?type=${search.type}&q=${encodeURIComponent(search.q)}`));
    } catch (err) {
      setResult(fallbackSearchResult(search.q, search.type));
      notify('Showing result from built-in sample dataset');
    }
  };

  const analyze = async () => {
    try {
      const data = await api('/analyze/job', { method: 'POST', body: JSON.stringify({ text: jobText }) });
      setAnalysis(data.analysis);
    } catch (err) {
      setAnalysis({
        score: 84,
        label: 'Likely Fraud',
        summary: 'The message contains multiple fake-job indicators: advance fee, WhatsApp hiring, no interview, and identity document request.',
        flags: [
          { phrase: 'registration fee', reason: 'Advance payment before job verification' },
          { phrase: 'no interview', reason: 'Hiring without interview is suspicious' },
          { phrase: 'aadhaar pan card', reason: 'Sensitive identity documents requested early' }
        ],
        recommendations: [
          'Do not pay any registration or training fee.',
          'Verify the recruiter from the official company careers page.',
          'Do not share Aadhaar, PAN, bank details, or OTPs.'
        ]
      });
      notify('Showing sample NLP analysis because backend is offline');
    }
  };

  return (
    <main>
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Community scam checking platform</p>
          <h1>Check a phone number, WhatsApp job offer, or suspicious message before trusting it.</h1>
          <p>Scrutnix combines community reports, open seed datasets, NLP scam-signal detection, reporter trust, and an explainable risk score.</p>
          <div className="hero-badges">
            <button type="button" onClick={() => setView('research')}>Risk engine</button>
            <button type="button" onClick={() => setView('analyzer')}>Job analyzer</button>
            <button type="button" onClick={() => setView('student')}>Student safety hub</button>
          </div>
          <div className="hero-actions">
            <button className="primary" onClick={() => setView('report')}>Report a scam</button>
            <button className="secondary-cta" onClick={() => setView('research')}>View algorithm</button>
            <button className="demo-cta" onClick={() => setView('about')}>About platform</button>
          </div>
        </div>
        <div className="hero-stage">
          <HeroGraphic reports={activeReports} setView={setView} />
          <div className="hero-panel search-console">
            <div className="panel-kicker">Instant risk lookup</div>
            <h2>Check a number or message</h2>
            <form className="search-box" onSubmit={doSearch}>
              <div className="segmented">
                {['phone', 'email', 'message'].map((type) => (
                  <button type="button" key={type} className={search.type === type ? 'active' : ''} onClick={() => setSearch({ ...search, type })}>{type}</button>
                ))}
              </div>
              <input value={search.q} onChange={(e) => setSearch({ ...search, q: e.target.value })} placeholder="Enter phone, email, or message keyword" />
              <button className="primary">Search risk</button>
            </form>
            {result && <RiskResult result={result} />}
          </div>
        </div>
      </section>

      <section className="front-visual-grid">
        <button className="visual-card phone-demo" type="button" onClick={() => setResult(fallbackSearchResult('9876543210', 'phone'))}>
          <div className="phone-top"><span />Suspicious WhatsApp Offer</div>
          <div className="chat-bubble incoming">Selected for backend job. No interview needed.</div>
          <div className="chat-bubble incoming danger-msg">Pay Rs 799 registration fee to confirm joining.</div>
          <div className="phone-verdict"><strong>91</strong><span>Critical risk detected</span></div>
        </button>
        <button className="visual-card mini-map-card" type="button" onClick={() => setView('community')}>
          <div className="panel-kicker">India signal map</div>
          <div className="mini-map">
            <span className="pin p1" />
            <span className="pin p2" />
            <span className="pin p3" />
            <span className="pin p4" />
            <span className="pin p5" />
          </div>
          <p>Live clusters across Delhi, Maharashtra, Karnataka, Tamil Nadu and Uttar Pradesh.</p>
        </button>
        <button className="visual-card proof-card" type="button" onClick={() => setView('research')}>
          <div className="panel-kicker">Evidence quality</div>
          <h3>Why the score is trusted</h3>
          <div className="proof-bars">
            <span style={{ '--w': '92%' }}>Reporter consensus</span>
            <span style={{ '--w': '86%' }}>Proof strength</span>
            <span style={{ '--w': '78%' }}>NLP scam signals</span>
          </div>
        </button>
      </section>

      <Stats stats={activeStats} setView={setView} />

      <IntelligenceDashboard stats={activeStats} reports={activeReports} />

      <section className="grid two showcase-grid">
        <IndiaHeatmap states={activeStats.by_state || DEMO_STATS.by_state} />
        <TrendPanel />
      </section>

      <section className="grid two showcase-grid">
        <ModelPipeline />
        <ScamPlaybooks />
      </section>

      <ProjectDepth reports={activeReports} />

      <section className="grid two">
        <div className="panel">
          <div className="panel-kicker">NLP safety lab</div>
          <h2>NLP Job Offer Analyzer</h2>
          <p className="muted">Uses negation-aware Indian scam keywords plus similarity against community reports.</p>
          <textarea value={jobText} onChange={(e) => setJobText(e.target.value)} rows="8" />
          <button className="primary" onClick={analyze}>Analyze job message</button>
          {analysis && <AnalysisResult analysis={analysis} />}
        </div>
        <div className="panel">
          <div className="panel-kicker">Community stream</div>
          <h2>Live Community Reports</h2>
          <LiveFeed reports={activeReports} />
          <button onClick={() => refresh().catch(() => {})}>Refresh feed</button>
        </div>
      </section>

      <section className="section">
        <div className="section-title">
          <p className="eyebrow">Project modules</p>
          <h2>Built for College Awareness</h2>
        </div>
        <div className="feature-grid">
          <Feature title="Campus Reporting" text="Students can report suspicious recruiters and help other students identify repeated scam patterns." />
          <Feature title="Campus Heatmap" text="Reports are grouped by state/city so colleges can show local awareness trends." />
          <Feature title="Evidence-Based Reports" text="Proof level, reporter trust, source type, and community votes change the risk confidence." />
          <Feature title="Explainable Score" text="Every score shows the report, evidence, trust, recency, and text factors used in the calculation." />
        </div>
      </section>

      <CollegeModule setView={setView} />
    </main>
  );
}

function HeroGraphic({ reports, setView }) {
  const top = [...reports].sort((a, b) => (b.risk || 0) - (a.risk || 0)).slice(0, 4);
  return (
    <div className="hero-graphic" aria-label="Risk score preview">
      <button className="radar-card" type="button" onClick={() => setView('research')}>
        <div className="radar-orbit orbit-one" />
        <div className="radar-orbit orbit-two" />
        <div className="radar-center">3L</div>
      </button>
      <div className="hero-alerts">
        {top.map((item) => (
          <button className="hero-alert" type="button" key={item.id} onClick={() => setView('community')}>
            <span>{item.category.replace('_', ' ')}</span>
            <strong>{item.risk}%</strong>
            <em>{item.city}</em>
          </button>
        ))}
      </div>
    </div>
  );
}

function Stats({ stats, setView }) {
  const cards = [
    ['Reports', stats?.total_reports || 0, 'community'],
    ['Unique Numbers', stats?.unique_numbers || 0, 'community'],
    ['Users', stats?.users || 0, 'community'],
    ['Reported Loss', `Rs ${Math.round(stats?.money_lost || 0)}`, 'research']
  ];
  return (
    <section className="stats">
      {cards.map(([label, value, target]) => (
        <button className="stat-card" type="button" key={label} onClick={() => setView(target)}>
          <strong>{value}</strong><span>{label}</span>
        </button>
      ))}
    </section>
  );
}

function IntelligenceDashboard({ stats, reports }) {
  return (
    <section className="intel-grid">
      <div className="panel threat-map">
        <div className="panel-kicker">Dataset summary</div>
        <h2>Scam Activity Overview</h2>
        <p className="muted">The sample dataset contains community-style reports, spam examples, fake-job patterns, and public discussion patterns.</p>
        <CategoryChart items={stats.by_category || DEMO_STATS.by_category} />
      </div>
      <div className="panel">
        <div className="panel-kicker">High priority queue</div>
        <h2>Top Risk Entities</h2>
        <HighRiskTable reports={reports} />
      </div>
      <div className="panel">
        <div className="panel-kicker">Campus and state signals</div>
        <h2>State Hotspots</h2>
        <StateGrid states={stats.by_state || DEMO_STATS.by_state} />
      </div>
      <div className="panel">
        <div className="panel-kicker">Evidence pipeline</div>
        <h2>Dataset Sources</h2>
        <DataSources />
      </div>
    </section>
  );
}

function IndiaHeatmap({ states }) {
  const coords = {
    Delhi: [49, 28],
    Maharashtra: [34, 61],
    Karnataka: [39, 78],
    'Tamil Nadu': [48, 88],
    'Uttar Pradesh': [55, 38],
    Telangana: [45, 68],
    'West Bengal': [72, 49],
    Gujarat: [25, 52],
    'Madhya Pradesh': [45, 52],
    Rajasthan: [33, 38],
    Kerala: [39, 91],
    Odisha: [63, 61]
  };
  const max = Math.max(...states.map((item) => item.count), 1);

  return (
    <div className="panel map-panel">
      <div className="panel-kicker">Report locations</div>
      <h2>India Scam Heatmap</h2>
      <p className="muted">State-wise intensity based on report volume, confidence, and repeat-target evidence.</p>
      <div className="india-map">
        <div className="map-shape" />
        {states.map((item) => {
          const [left, top] = coords[item.state] || [50, 50];
          const size = 16 + (item.count / max) * 34;
          return (
            <div
              className="hotspot"
              key={item.state}
              style={{ left: `${left}%`, top: `${top}%`, width: size, height: size }}
              title={`${item.state}: ${item.count} reports`}
            >
              <span>{item.count}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function TrendPanel() {
  const max = Math.max(...MONTHLY_TRENDS.map((item) => item.reports));
  return (
    <div className="panel trend-panel">
      <div className="panel-kicker">Incident velocity</div>
      <h2>Monthly Scam Trend</h2>
      <p className="muted">Fake job activity is rising fastest, which supports the project focus and NLP feature.</p>
      <div className="trend-chart">
        {MONTHLY_TRENDS.map((item) => (
          <div className="trend-col" key={item.month}>
            <div className="trend-stack">
              <span className="trend-total" style={{ height: `${(item.reports / max) * 100}%` }} />
              <span className="trend-job" style={{ height: `${(item.job / max) * 100}%` }} />
            </div>
            <strong>{item.month}</strong>
          </div>
        ))}
      </div>
      <div className="legend">
        <span><i className="legend-total" />All reports</span>
        <span><i className="legend-job" />Job fraud</span>
      </div>
    </div>
  );
}

function ModelPipeline() {
  const stages = [
    ['Normalize', 'Clean phone, email, text, source and proof metadata'],
    ['Score', 'Severity, recency, Bayesian votes, trust and evidence'],
    ['NLP', 'Fee, urgency, identity, WhatsApp-only and negation signals'],
    ['Explain', 'Risk label, confidence, reasons and safety actions']
  ];
  return (
    <div className="panel pipeline-panel">
      <div className="panel-kicker">Core backend algorithm</div>
      <h2>Risk Engine Pipeline</h2>
      <div className="pipeline">
        {stages.map(([title, text], index) => (
          <div className="pipeline-step" key={title}>
            <b>{index + 1}</b>
            <strong>{title}</strong>
            <span>{text}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function ScamPlaybooks() {
  return (
    <div className="panel playbook-panel">
      <div className="panel-kicker">Awareness content</div>
      <h2>Scam Pattern Playbooks</h2>
      <div className="playbooks">
        {PLAYBOOKS.map(([title, text]) => (
          <div className="playbook" key={title}>
            <strong>{title}</strong>
            <span>{text}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function ProjectDepth({ reports }) {
  const top = [...reports].sort((a, b) => (b.risk || 0) - (a.risk || 0))[0] || DEMO_REPORTS[0];
  return (
    <section className="depth-section">
      <div className="depth-header">
        <div>
          <p className="eyebrow">Technical depth layer</p>
          <h2>Frontend, backend, scoring, NLP, and community reporting</h2>
        </div>
        <p>These modules show the backend logic, data pipeline, review workflow, case analysis and explainability expected from a serious two-student project.</p>
      </div>

      <div className="depth-grid">
        <div className="panel investigation-panel">
          <div className="panel-kicker">Investigation workspace</div>
          <h2>Case Investigator</h2>
          <div className="investigation-card">
            <div>
              <span>Target</span>
              <strong>{top.masked_target}</strong>
            </div>
            <div>
              <span>Risk</span>
              <strong>{top.risk || 91}%</strong>
            </div>
            <div>
              <span>Evidence</span>
              <strong>{top.proof_level || 'Screenshot'}</strong>
            </div>
          </div>
          <p>{top.message}</p>
          <div className="signal-cloud">
            {['Fee demand', 'Urgency', 'Identity request', 'Community confirmations', 'Recent activity'].map((item) => <span key={item}>{item}</span>)}
          </div>
        </div>

        <div className="panel ingestion-panel">
          <div className="panel-kicker">Backend data pipeline</div>
          <h2>From report to risk score</h2>
          <div className="ingestion-flow">
            {INGESTION_STEPS.map(([title, text], index) => (
              <div className="ingestion-step" key={title}>
                <b>{index + 1}</b>
                <strong>{title}</strong>
                <span>{text}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="panel">
          <div className="panel-kicker">Realistic project evidence</div>
          <h2>Case Studies</h2>
          <div className="case-grid">
            {CASE_STUDIES.map((item) => (
              <article className="case-card" key={item.title}>
                <div className="case-top">
                  <strong>{item.title}</strong>
                  <b>{item.risk}</b>
                </div>
                <span>{item.target} - loss: {item.loss}</span>
                <div className="case-signals">
                  {item.signals.map((signal) => <em key={signal}>{signal}</em>)}
                </div>
                <p>{item.outcome}</p>
              </article>
            ))}
          </div>
        </div>

        <div className="panel moderation-panel">
          <div className="panel-kicker">Admin backend workflow</div>
          <h2>Moderation Queue</h2>
          <div className="moderation-list">
            {MODERATION_QUEUE.map((item) => (
              <div className="moderation-row" key={item.id}>
                <b>{item.id}</b>
                <div>
                  <strong>{item.type}</strong>
                  <span>{item.evidence}</span>
                </div>
                <em className={`priority ${item.priority.toLowerCase()}`}>{item.priority}</em>
                <span>{item.action}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function CollegeModule({ setView }) {
  return (
    <section className="college-section">
      <div className="college-hero panel">
        <div>
          <div className="panel-kicker">College deployment module</div>
          <h2>Campus Scam Awareness Command Center</h2>
          <p>Designed for placement cells, student coordinators, college mentors, and public awareness teams. It shows how students discover scams, which channels are risky, and which colleges contribute verified reports.</p>
          <button className="primary" onClick={() => setView('report')}>Submit campus report</button>
        </div>
        <div className="college-score-card">
          <span>Campus readiness</span>
          <strong>92%</strong>
          <em>based on report coverage, verification, and alert participation</em>
        </div>
      </div>

      <div className="college-metrics">
        <Metric label="Campus reports" value={COLLEGE_INSIGHTS.campus_reports} />
        <Metric label="Colleges covered" value={COLLEGE_INSIGHTS.colleges} />
        <Metric label="Students saw scams" value={`${COLLEGE_INSIGHTS.students_seen_scam}%`} />
        <Metric label="Want alerts" value={`${COLLEGE_INSIGHTS.alert_opt_in}%`} />
      </div>

      <div className="grid two showcase-grid">
        <div className="panel">
          <div className="panel-kicker">Report analytics</div>
          <h2>Where Students Encounter Scams</h2>
          <CategoryChart items={COLLEGE_INSIGHTS.channels.map((item) => ({ category: item.label, count: item.value }))} />
        </div>
        <div className="panel">
          <div className="panel-kicker">Participation ranking</div>
          <h2>Campus Leaderboard</h2>
          <div className="leaderboard">
            {COLLEGE_INSIGHTS.leaderboard.map((item, index) => (
              <div className="leader-row" key={item.college}>
                <b>{index + 1}</b>
                <div>
                  <strong>{item.college}</strong>
                  <span>{item.reports} reports - {item.verified} verified</span>
                </div>
                <em>{item.score}</em>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="panel">
        <div className="panel-kicker">How students will know it is a scam</div>
        <h2>Campus Awareness Workflow</h2>
        <div className="campus-flow">
          <div><strong>1. Receive</strong><span>Student gets WhatsApp/call/email job offer.</span></div>
          <div><strong>2. Check</strong><span>Paste phone number or message into Scrutnix.</span></div>
          <div><strong>3. Explain</strong><span>Risk score shows reports, NLP flags, proof, and source.</span></div>
          <div><strong>4. Alert</strong><span>Verified scam pattern appears in live feed and campus report.</span></div>
        </div>
      </div>

      <div className="workshop-grid">
        {COLLEGE_INSIGHTS.workshops.map(([title, text]) => (
          <div className="workshop-card" key={title}>
            <strong>{title}</strong>
            <span>{text}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
