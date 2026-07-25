export function RiskResult({ result }) {
  const risk = result.risk;
  return (
    <div className={`risk-card ${risk.label.toLowerCase().replaceAll(' ', '-')}`}>
      <div className="score-ring" style={{ '--score': `${risk.score * 3.6}deg` }}>
        <strong>{risk.score}</strong>
        <span>/100</span>
      </div>
      <div>
        <h3>{risk.label}</h3>
        <p>{risk.method}</p>
        <div className="chips">
          <span>{risk.report_count} reports</span>
          <span>{risk.unique_reporters} reporters</span>
          <span>{Math.round(risk.confidence * 100)}% confidence</span>
        </div>
      </div>
    </div>
  );
}

export function AnalysisResult({ analysis }) {
  return (
    <div className="analysis">
      <div className="score-row">
        <strong>{analysis.label}</strong>
        <span>{analysis.score}/100</span>
      </div>
      <p>{analysis.summary}</p>
      {analysis.layers && <LayerBreakdown analysis={analysis} />}
      <h4>Detected Signals</h4>
      <div className="chips">
        {analysis.flags.length ? analysis.flags.map((f) => <span key={f.phrase}>{f.phrase}: {f.reason}</span>) : <span>No major scam phrases found</span>}
      </div>
      <h4>Recommendations</h4>
      <ul>{analysis.recommendations.map((tip) => <li key={tip}>{tip}</li>)}</ul>
    </div>
  );
}

function LayerBreakdown({ analysis }) {
  const layers = analysis.layers;
  const cards = [
    ['Layer 1', 'ML Model', layers.layer_1_ml_model.score, layers.layer_1_ml_model.label, 'Trained on 18k template-derived text samples'],
    ['Layer 2', 'Scam Keywords', layers.layer_2_scam_keywords.score, `${layers.layer_2_scam_keywords.matched_patterns} signals`, 'Checks fee, OTP, documents, urgency and channel risk'],
    ['Layer 3', 'User Reports', layers.layer_3_user_reports.score, `${layers.layer_3_user_reports.matched_reports} matches`, 'Compares with community reports and repeat scam patterns']
  ];
  return (
    <div className="layer-breakdown">
      {cards.map(([layer, title, score, label, note]) => (
        <div className="layer-card" key={layer}>
          <span>{layer}</span>
          <strong>{title}</strong>
          <b>{score}/100</b>
          <em>{label}</em>
          <small>{note}</small>
        </div>
      ))}
      {layers.layer_1_ml_model.top_terms?.length > 0 && (
        <div className="ml-terms">
          <strong>ML explanation terms</strong>
          <div className="chips">
            {layers.layer_1_ml_model.top_terms.slice(0, 6).map((item) => (
              <span key={item.term}>{item.term} to {item.direction}</span>
            ))}
          </div>
        </div>
      )}
      {analysis.model_metadata && (
        <p className="model-note">
          {analysis.model_metadata.model} trained with {analysis.model_metadata.training_rows?.toLocaleString()} job-listing examples.
        </p>
      )}
    </div>
  );
}
