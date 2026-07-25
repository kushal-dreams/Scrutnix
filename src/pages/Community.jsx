import { useState } from 'react';
import { LiveFeed } from '../components/DashboardComponents';
import { DEMO_REPORTS } from '../data/demoData';
import { api } from '../services/api';

export function Community({ reports, refresh, user, notify }) {
  const [category, setCategory] = useState('all');
  const items = reports.length ? reports : DEMO_REPORTS;
  const filtered = category === 'all' ? items : items.filter((r) => r.category === category);
  const vote = async (id, vote_type) => {
    if (!user) return notify('Login to vote on reports');
    await api(`/reports/${id}/vote`, { method: 'POST', body: JSON.stringify({ vote_type }) });
    await refresh();
  };
  return (
    <main className="section">
      <div className="section-head">
        <h1>Community Reports Feed</h1>
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="all">All categories</option><option value="job_fraud">Job fraud</option><option value="phishing">Phishing</option><option value="loan_scam">Loan scam</option><option value="spam">Spam</option>
        </select>
      </div>
      <div className="report-list">
        {filtered.map((report) => (
          <article className="report-card" key={report.id}>
            <div className="report-meta">
              <strong>{report.category.replace('_', ' ')}</strong>
              <span>{report.masked_target}</span>
              <span>{report.city}, {report.state}</span>
            </div>
            <p>{report.message}</p>
            <div className="report-actions">
              <button onClick={() => vote(report.id, 'up')}>Confirm {report.upvotes}</button>
              <button onClick={() => vote(report.id, 'down')}>Dispute {report.downvotes}</button>
              <span>Trust {Math.round((report.trust_score || 0.5) * 100)}%</span>
            </div>
          </article>
        ))}
      </div>
    </main>
  );
}
