export function Research() {
  return (
    <main className="section research">
      <h1>Research, Algorithm, and Methodology</h1>
      <div className="grid two">
        <div className="panel">
          <h2>Risk Score Algorithm</h2>
          <p>The phone/email score is an explainable ensemble. Each matching report contributes evidence using severity, exponential recency decay, Bayesian vote confidence, reporter trust, proof level, dataset source confidence, and NLP scam-signal score.</p>
          <pre>{`score = mean(report_evidence) * 0.72
      + consensus_confidence * 0.18
      + report_volume_confidence * 0.10`}</pre>
          <p>Consensus prevents one person from falsely damaging a number. Bayesian votes prevent one upvote from creating fake certainty.</p>
        </div>
        <div className="panel">
          <h2>NLP Layer</h2>
          <p>The analyzer detects Indian fake-job phrases such as registration fee, security deposit, WhatsApp only, Aadhaar/PAN request, instant joining, daily income, and no interview.</p>
          <p>It also handles negation, so "no registration fee" is not treated the same as "pay registration fee".</p>
        </div>
        <div className="panel">
          <h2>Dataset Strategy</h2>
          <p>Initial seed data combines community-style reports, TRAI DND-like spam examples, Kaggle-inspired fake-job examples, and online-community patterns. Real deployment would replace seeds with verified user reports and imported open datasets.</p>
        </div>
        <div className="panel">
          <h2>Backend Depth</h2>
          <ul>
            <li>JWT authentication and password hashing</li>
            <li>Validated report creation and normalized phone numbers</li>
            <li>Voting, comments, report statistics, and live feed</li>
            <li>Separate risk, trust, NLP, and normalization services</li>
          </ul>
        </div>
      </div>
    </main>
  );
}
