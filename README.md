# Scrutnix

**Community-powered scam intelligence platform for India.**  
Search phone numbers, report scams, and analyze job descriptions with NLP — built to protect students and job seekers.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/kushal-dreams/Scrutnix)

---

## Features

- **Phone / Email Risk Lookup** — instant community risk score for any Indian mobile number or email
- **Scam Reporting** — multi-step report form with proof uploads, category tagging, and location
- **NLP Job Analyzer** — detects fake-job red flags like advance fees, no-interview promises, and identity harvesting
- **Community Feed** — upvote/downvote reports, trust scoring, and live ticker
- **India Heatmap** — state-wise scam intensity visualization
- **Student Safety Hub** — checklist, campus alerts, and awareness content
- **Explainable Risk Score** — shows severity, recency, Bayesian votes, reporter trust, proof quality, and NLP signals
- **GuideBot** — rule-based chatbot for instant scam guidance

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Vanilla CSS |
| Backend | Flask, SQLAlchemy, SQLite |
| NLP | scikit-learn (TF-IDF + Logistic Regression), custom keyword matching |
| Auth | JWT + Phone OTP |
| Deployment | Vercel (frontend) |

## Quick Start

### Frontend

```bash
npm install
npm run dev
```

Opens at **http://localhost:5173** — works fully with built-in demo data, no backend needed.

### Backend (optional)

```bash
cd scrutinix-backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Runs at **http://localhost:5000** — OTP codes print to the terminal.

## Project Structure

```
├── src/
│   ├── components/         # Layout, DashboardComponents, RiskResults
│   ├── pages/              # Home, ReportPage, JobAnalyzer, StudentHub, etc.
│   ├── services/           # API client, offline fallbacks
│   ├── data/               # Demo dataset (28 realistic reports)
│   └── styles/             # app.css, report.css
│
├── scrutinix-backend/
│   ├── app.py              # Flask entry point
│   ├── routes/             # auth, search, report, analyzer, profile, live_feed
│   ├── models/             # SQLAlchemy models + ML model
│   ├── utils/              # NLP, risk scoring, trust engine
│   └── datasets/           # Training data (CSV)
│
├── vercel.json             # Vercel deployment config
├── vite.config.js          # Vite build config
└── package.json
```

## Deployment

### Vercel (Frontend)

```bash
npx vercel
```

Or connect this repo on [vercel.com](https://vercel.com) for automatic deploys on every push.

### Backend (Optional — Render)

If you need a live backend, deploy `scrutinix-backend/` to [Render](https://render.com) as a Python web service and set the `VITE_API_URL` environment variable in Vercel to your Render URL.

## How the Risk Score Works

The risk score is an explainable ensemble:

```
score = mean(report_evidence) × 0.72
      + consensus_confidence × 0.18
      + report_volume_confidence × 0.10
```

Each report contributes evidence through: **severity** · **exponential recency decay** · **Bayesian vote confidence** · **reporter trust** · **proof quality** · **NLP scam signals**.

## Authors

Built by **Kushal**.

## License

This project is for educational and awareness purposes.
