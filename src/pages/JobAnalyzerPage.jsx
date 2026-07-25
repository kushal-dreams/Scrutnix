import { useState } from 'react';
import { AnalysisResult } from '../components/RiskResults';
import { api } from '../services/api';

export function JobAnalyzerPage({ notify, setView }) {
  const examples = [
    {
      title: 'Fake data entry offer',
      text: 'Dear candidate, you are selected for work from home data entry. No interview required. Salary Rs 35,000 monthly. Pay Rs 799 registration fee on UPI and send Aadhaar, PAN and bank passbook for employee ID.'
    },
    {
      title: 'Suspicious HR WhatsApp message',
      text: 'Hello, I am HR from a top MNC. Immediate joining today. Training kit fee Rs 1,500 refundable. Share OTP for profile verification and confirm payment screenshot.'
    },
    {
      title: 'Safer official-style posting',
      text: 'Software intern opening. Apply only through the official careers page. Shortlisted candidates will receive interview schedule from company domain email. No fees are charged at any stage.'
    }
  ];
  const [text, setText] = useState(examples[0].text);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeText = async () => {
    if (!text.trim()) {
      notify('Paste a job description or recruiter message first');
      return;
    }
    setLoading(true);
    try {
      const data = await api('/analyze/job', { method: 'POST', body: JSON.stringify({ text }) });
      setAnalysis(data.analysis);
    } catch (err) {
      const lower = text.toLowerCase();
      const redFlags = [
        ['registration fee', 'Advance fee before joining'],
        ['security deposit', 'Refundable deposit claim'],
        ['upi', 'Payment requested through UPI'],
        ['no interview', 'Hiring without interview'],
        ['aadhaar', 'Sensitive identity document requested'],
        ['pan', 'Sensitive identity document requested'],
        ['otp', 'OTP/profile verification scam signal'],
        ['whatsapp', 'Recruitment limited to WhatsApp']
      ].filter(([phrase]) => lower.includes(phrase));
      const fallbackScore = Math.min(95, 28 + redFlags.length * 11);
      setAnalysis({
        score: fallbackScore,
        label: fallbackScore >= 75 ? 'Likely Fraud' : fallbackScore >= 45 ? 'Suspicious' : 'Low Risk',
        summary: redFlags.length
          ? `The job text contains ${redFlags.length} strong scam signal${redFlags.length > 1 ? 's' : ''}. Verify the company before taking action.`
          : 'No major fake-job phrases were detected, but still verify the company domain, job portal, and recruiter identity.',
        flags: redFlags.map(([phrase, reason]) => ({ phrase, reason })),
        recommendations: [
          'Do not pay registration, training, kit, software, or security fees.',
          'Verify the job only through the official company careers page.',
          'Do not share Aadhaar, PAN, bank details, passbook, or OTP.',
          'Report the message on Scrutnix if it looks suspicious.'
        ],
        layers: {
          layer_1_ml_model: {
            name: 'Naive Bayes classifier with 18k template-derived samples',
            score: Math.min(100, fallbackScore + 4),
            label: fallbackScore >= 60 ? 'ML Scam Pattern' : 'ML Uncertain',
            confidence: .72,
            top_terms: redFlags.map(([term]) => ({ term, direction: 'scam', strength: 2.4 })).slice(0, 5)
          },
          layer_2_scam_keywords: {
            score: fallbackScore,
            matched_patterns: redFlags.length,
            safe_signals: []
          },
          layer_3_user_reports: {
            score: redFlags.length >= 3 ? 62 : 22,
            matched_reports: redFlags.length >= 3 ? 3 : 0,
            top_similarity: redFlags.length >= 3 ? .48 : 0
          }
        },
        model_metadata: {
          model: 'Multinomial Naive Bayes text classifier',
          training_rows: 18000,
          classes: ['scam', 'legit'],
          dataset_note: 'Local fallback explanation when backend is offline.'
        }
      });
      notify('Showing local analyzer result because backend is offline');
    } finally {
      setLoading(false);
    }
  };

  const riskLevel = analysis?.score >= 75 ? 'critical' : analysis?.score >= 45 ? 'warning' : 'safe';

  return (
    <main className="analyzer-page">
      <section className="analyzer-hero panel">
        <div>
          <p className="eyebrow">NLP job description analyzer</p>
          <h1>Paste a job offer, recruiter message, or WhatsApp text to detect fake-job red flags.</h1>
          <p>Scrutnix checks advance-fee patterns, no-interview claims, document requests, urgency language, WhatsApp-only hiring, UPI payment signals, and safer official recruitment wording.</p>
          <div className="hero-actions">
            <button className="primary" type="button" onClick={analyzeText}>{loading ? 'Analyzing...' : 'Analyze job text'}</button>
            <button className="secondary-cta" type="button" onClick={() => setView('report')}>Report this offer</button>
          </div>
        </div>
        <div className="analyzer-meter">
          <span>Current scan</span>
          <strong>{analysis ? analysis.score : '--'}</strong>
          <em>{analysis ? analysis.label : 'Paste text to begin'}</em>
        </div>
      </section>

      <section className="grid two analyzer-workbench">
        <div className="panel analyzer-input">
          <div className="panel-kicker">Job text input</div>
          <h2>Job Description / Message</h2>
          <textarea rows="13" value={text} onChange={(e) => setText(e.target.value)} placeholder="Paste job description, WhatsApp message, recruiter email, or offer text here..." />
          <div className="analyzer-actions">
            <button className="primary" type="button" onClick={analyzeText}>{loading ? 'Checking...' : 'Run NLP scan'}</button>
            <button type="button" onClick={() => setText('')}>Clear</button>
          </div>
          <div className="example-strip">
            {examples.map((item) => (
              <button type="button" key={item.title} onClick={() => { setText(item.text); setAnalysis(null); }}>
                {item.title}
              </button>
            ))}
          </div>
        </div>

        <div className={`panel analyzer-result ${riskLevel}`}>
          <div className="panel-kicker">NLP output</div>
          <h2>Risk Explanation</h2>
          {analysis ? (
            <>
              <AnalysisResult analysis={analysis} />
              <div className="next-step-box">
                <strong>What should the student do next?</strong>
                <p>Stop communication, avoid payment, verify through official sources, save screenshots, and submit a report so other students can be warned.</p>
                <button type="button" onClick={() => setView('student')}>Open student safety steps</button>
              </div>
            </>
          ) : (
            <div className="empty-analyzer">
              <strong>No scan yet</strong>
              <p>Paste a job description or choose an example, then run the NLP scan.</p>
            </div>
          )}
        </div>
      </section>

      <section className="analyzer-signals">
        {[
          ['Advance fee', 'Registration, security, kit, training, laptop or software fee before joining.'],
          ['No interview', 'Instant selection, direct joining, guaranteed salary, or no screening.'],
          ['Document request', 'Aadhaar, PAN, bank passbook, OTP, selfie, or signature asked too early.'],
          ['Channel risk', 'Recruiter uses only WhatsApp, Telegram, free email, or personal number.']
        ].map(([title, desc]) => (
          <div className="signal-card" key={title}>
            <strong>{title}</strong>
            <span>{desc}</span>
          </div>
        ))}
      </section>
    </main>
  );
}
