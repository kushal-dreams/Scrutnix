import { DEMO_REPORTS } from '../data/demoData';

export function Metric({ label, value }) {
  return (
    <div className="metric-card">
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}

export function CategoryChart({ items }) {
  const max = Math.max(...items.map((item) => item.count), 1);
  return (
    <div className="bar-list">
      {items.map((item) => (
        <div className="bar-row" key={item.category}>
          <div className="bar-label">
            <span>{item.category.replace('_', ' ')}</span>
            <strong>{item.count}</strong>
          </div>
          <div className="bar-track">
            <div className="bar-fill" style={{ width: `${(item.count / max) * 100}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

export function HighRiskTable({ reports }) {
  return (
    <div className="risk-table">
      {[...reports].sort((a, b) => (b.risk || b.upvotes || 0) - (a.risk || a.upvotes || 0)).slice(0, 6).map((report) => (
        <div className="risk-row" key={report.id}>
          <div>
            <strong>{report.masked_target}</strong>
            <span>{report.category.replace('_', ' ')} - {report.city || 'India'}</span>
          </div>
          <b>{report.risk || Math.min(96, 45 + report.upvotes)}%</b>
        </div>
      ))}
    </div>
  );
}

export function StateGrid({ states }) {
  return (
    <div className="state-grid">
      {states.slice(0, 8).map((item) => (
        <div className="state-pill" key={item.state}>
          <span>{item.state}</span>
          <strong>{item.count}</strong>
        </div>
      ))}
    </div>
  );
}

export function DataSources() {
  const sources = [
    ['Community reports', 'Live user-submitted phone, email, and message complaints'],
    ['TRAI DND seed', 'Spam and unwanted-call style examples for baseline data'],
    ['Kaggle patterns', 'Fake job posting phrases adapted for NLP testing'],
    ['Campus reports', 'Reports submitted by students and verified community members']
  ];
  return (
    <div className="source-list">
      {sources.map(([title, text]) => (
        <div className="source-card" key={title}>
          <strong>{title}</strong>
          <span>{text}</span>
        </div>
      ))}
    </div>
  );
}

export function LiveFeed({ reports }) {
  const items = reports.length ? reports : DEMO_REPORTS;
  return (
    <div className="feed">
      {items.slice(0, 8).map((report) => (
        <article key={report.id} className="feed-item">
          <div>
            <strong>{report.category.replace('_', ' ')}</strong>
            <span>{report.city || 'Unknown city'}, {report.state || 'India'}</span>
          </div>
          <p>{report.message}</p>
          <small>{report.masked_target} - {report.upvotes} confirmations</small>
        </article>
      ))}
    </div>
  );
}

export function Feature({ title, text }) {
  return <div className="feature"><h3>{title}</h3><p>{text}</p></div>;
}
