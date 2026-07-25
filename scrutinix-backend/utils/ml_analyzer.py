"""
ml_analyzer.py — Drop-in replacement for risk_score_jobs.py.

Place this file at: scrutinix-backend/utils/ml_analyzer.py

    Requires that you have already run train_model.py to generate:
    scrutinix-backend/models/job_fraud_model.pkl
"""

import os
import re
import csv
import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# ── Paths ─────────────────────────────────────────────────────────────────────
_BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODEL_PATH   = os.path.join(_BASE_DIR, 'models', 'job_fraud_model.pkl')
_KEYWORDS_CSV = os.path.join(
    _BASE_DIR, 'datasets', 'indian_nlp', 'india_scam_keywords_dictionary.csv'
)

# ── Module-level singletons (loaded once at startup, reused for every request) ─
_pipeline = None   # The trained TF-IDF + LogReg model
_keywords = None   # Dict of Indian scam keywords with weights


# ── Load model ────────────────────────────────────────────────────────────────
def _get_pipeline():
    """
    Load the trained model from disk once.
    After the first call, it's kept in memory — no disk I/O on subsequent calls.
    """
    global _pipeline
    if _pipeline is None:
        if not os.path.exists(_MODEL_PATH):
            raise FileNotFoundError(
                f"[ml_analyzer] Model not found at: {_MODEL_PATH}\n"
                "Run 'python train_model.py' from the backend folder first."
            )
        print("[ml_analyzer] Loading model from disk...")
        _pipeline = joblib.load(_MODEL_PATH)
        print("[ml_analyzer] Model loaded. Ready.")
    return _pipeline


# ── Load Indian scam keywords ─────────────────────────────────────────────────
def _get_keywords() -> dict:
    """
    Load the Indian scam keyword CSV once.
    Expected CSV columns: keyword, weight, category
    (Falls back gracefully if the file is missing or columns differ.)
    """
    global _keywords
    if _keywords is not None:
        return _keywords

    _keywords = {}

    if not os.path.exists(_KEYWORDS_CSV):
        print("[ml_analyzer] Warning: Indian keywords CSV not found. Skipping keyword layer.")
        return _keywords

    try:
        with open(_KEYWORDS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Normalise column names (strip spaces, lowercase)
            reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]

            for row in reader:
                # Try multiple possible column name spellings
                kw = (row.get('keyword') or row.get('phrase') or row.get('term') or '').lower().strip()
                if not kw:
                    continue

                try:
                    weight = int(row.get('weight') or row.get('score') or 1)
                except (ValueError, TypeError):
                    weight = 1

                category = row.get('category') or row.get('type') or 'general'
                severity = 'high' if weight >= 3 else ('medium' if weight == 2 else 'low')

                _keywords[kw] = {
                    'weight':   weight,
                    'category': category.strip(),
                    'severity': severity
                }

        print(f"[ml_analyzer] Loaded {len(_keywords)} Indian scam keywords.")

    except Exception as e:
        print(f"[ml_analyzer] Could not load keywords CSV: {e}")

    return _keywords


# ── Text preprocessing (must match what train_model.py used) ─────────────────
def _preprocess(text: str) -> str:
    if not isinstance(text, str):
        return ''
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s₹]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ── Negation detector ─────────────────────────────────────────────────────────
def _is_negated(text: str, phrase: str, window: int = 6) -> bool:
    """
    Check if a negation word appears within `window` words BEFORE the phrase.

    Examples:
      "No registration fee required"  → True  (negated → skip this flag)
      "Send registration fee now"     → False (not negated → keep this flag)
    """
    negation_words = {'no', 'not', 'never', 'none', 'without', 'free', 'zero', 'nil', 'dont', "don't"}
    words       = text.lower().split()
    phrase_toks = phrase.lower().split()
    phrase_len  = len(phrase_toks)

    for i in range(len(words) - phrase_len + 1):
        if words[i: i + phrase_len] == phrase_toks:
            context = set(words[max(0, i - window): i])
            if context & negation_words:
                return True
    return False


# ── Explainability: which words drove the model's fraud score? ────────────────
def _top_fraud_signals(pipeline, raw_text: str, top_n: int = 8) -> list[tuple[str, float]]:
    """
    For a given text, find the words/bigrams that most contributed to
    the fraud prediction.

    How it works:
      - TF-IDF weight of a word in THIS document  (how prominent it is here)
      × The model's learned coefficient for that word  (how fraud-y that word is)
      = Contribution score

    Returns a list of (word, score) tuples, highest first.
    """
    vectorizer    = pipeline.named_steps['tfidf']
    clf           = pipeline.named_steps['clf']
    feature_names = vectorizer.get_feature_names_out()
    fraud_coefs   = clf.coef_[0]   # positive = fraud signal, negative = real-job signal

    processed = _preprocess(raw_text)
    X         = vectorizer.transform([processed])

    present_indices = X.nonzero()[1]  # only features that appear in this text
    if len(present_indices) == 0:
        return []

    scored = [
        (feature_names[i], float(X[0, i] * fraud_coefs[i]))
        for i in present_indices
        if fraud_coefs[i] > 0   # only positive fraud contributors
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_n]


# ── Community report similarity ───────────────────────────────────────────────
def _community_similarity(query: str, db_reports: list[dict]) -> tuple[list, float]:
    """
    Build a tiny TF-IDF on the fly from community-reported fraud posts,
    then find which ones are most similar to the current query.

    db_reports: list of dicts with keys: report_id, phone, job_description
    Returns: (matches_list, max_similarity_score)
    """
    if not db_reports:
        return [], 0.0

    corpus = [_preprocess(r.get('job_description', '')) for r in db_reports]
    corpus = [c for c in corpus if len(c) > 5]

    if not corpus:
        return [], 0.0

    try:
        vec   = TfidfVectorizer(max_features=5_000, ngram_range=(1, 2))
        all_d = corpus + [_preprocess(query)]
        vec.fit(all_d)

        corpus_mat  = vec.transform(corpus)
        query_vec   = vec.transform([_preprocess(query)])
        sims        = cosine_similarity(query_vec, corpus_mat)[0]

        matches = []
        for idx, sim in enumerate(sims):
            if sim > 0.10:   # ignore very weak matches
                report = db_reports[idx]
                matches.append({
                    'report_id':  report.get('report_id'),
                    'phone':      report.get('phone', 'N/A'),
                    'category':   'Job Fraud',
                    'similarity': round(float(sim), 2)
                })

        matches.sort(key=lambda x: x['similarity'], reverse=True)
        max_sim = float(np.max(sims)) if len(sims) > 0 else 0.0
        return matches[:3], max_sim

    except Exception as e:
        print(f"[ml_analyzer] Community similarity error: {e}")
        return [], 0.0


# ── Main public function ──────────────────────────────────────────────────────
def analyze_job_description(description: str, db_reports: list[dict] = None) -> dict:
    """
    Full hybrid analysis of a job description.

    Layer 1 — ML Model        : trained on 17,880 EMSCAD examples → primary fraud score
    Layer 2 — Indian Keywords  : 65+ hand-crafted Indian scam signals → score boost + flags
    Layer 3 — Community TF-IDF : similarity to user-reported frauds → bonus context

    Returns a dict matching the frontend API contract exactly.

    Args:
        description : raw job description text from the user
        db_reports  : list of {'report_id', 'phone', 'job_description'} from DB
                      (pass None or [] if DB is empty — it degrades gracefully)
    """
    # ── Guard: empty input ────────────────────────────────────────────────────
    if not description or not description.strip():
        return {
            'score':              0,
            'label':              'Low Risk',
            'flagged_keywords':   [],
            'flags':              [],
            'corpus_similarity':  0.0,
            'reasoning':          'No text provided.',
            'similarity_matches': []
        }

    pipeline = _get_pipeline()
    keywords = _get_keywords()

    # ═════════════════════════════════════════════════════════════════════════
    # LAYER 1 — ML Model
    # Input: raw text → preprocessed text → TF-IDF vector → LR score
    # Output: fraud_probability (0.0 – 1.0)  →  ml_score (0–100)
    # ═════════════════════════════════════════════════════════════════════════
    processed        = _preprocess(description)
    probabilities    = pipeline.predict_proba([processed])[0]
    fraud_probability = float(probabilities[1])   # probability of class 1 (fraud)
    ml_score         = int(fraud_probability * 100)

    # ═════════════════════════════════════════════════════════════════════════
    # LAYER 2 — Indian Keyword Detection (with negation handling)
    # ═════════════════════════════════════════════════════════════════════════
    flags          = []
    keyword_bonus  = 0
    text_lower     = description.lower()

    for phrase, info in keywords.items():
        if phrase in text_lower:
            if _is_negated(description, phrase):
                continue   # "No registration fee" → don't flag it
            flags.append({
                'flag':     phrase,
                'severity': info['severity']
            })
            keyword_bonus += info['weight'] * 2

    keyword_bonus = min(20, keyword_bonus)   # cap at +20 points

    # ═════════════════════════════════════════════════════════════════════════
    # COMBINED SCORE
    # ML model = 80% weight (general patterns, learned from data)
    # Indian keywords = up to 20% bonus (local patterns the model may miss)
    # ═════════════════════════════════════════════════════════════════════════
    final_score = min(100, int(ml_score * 0.8 + keyword_bonus))

    # Safety net: if Indian keywords are screaming (₹ registration, Aadhaar requests),
    # but the EMSCAD-trained model is uncertain, still raise the minimum floor.
    high_flags_count = sum(1 for f in flags if f['severity'] == 'high')
    if high_flags_count >= 2 and final_score < 50:
        final_score = 55   # force at least "High Risk" for multiple critical flags

    # ═════════════════════════════════════════════════════════════════════════
    # RISK LABEL
    # ═════════════════════════════════════════════════════════════════════════
    if final_score <= 25:
        label = 'Low Risk'
    elif final_score <= 50:
        label = 'Moderate Risk'
    elif final_score <= 75:
        label = 'High Risk'
    else:
        label = 'Likely Fraud'

    # ═════════════════════════════════════════════════════════════════════════
    # EXPLAINABILITY — "Why did the model say this?"
    # ═════════════════════════════════════════════════════════════════════════
    top_ml_signals = _top_fraud_signals(pipeline, description)
    ml_words       = [word for word, _ in top_ml_signals[:5]]

    reasoning_parts = []

    # Report severe Indian keyword hits first (most interpretable for users)
    high_flags = [f['flag'] for f in flags if f['severity'] == 'high']
    med_flags  = [f['flag'] for f in flags if f['severity'] == 'medium']
    if high_flags:
        reasoning_parts.append(f"Critical Indian scam signals: {', '.join(high_flags[:3])}")
    if med_flags:
        reasoning_parts.append(f"Warning signals: {', '.join(med_flags[:3])}")

    # Add ML-learned patterns
    if ml_words:
        reasoning_parts.append(f"ML-detected suspicious patterns: {', '.join(ml_words)}")

    if not reasoning_parts:
        reasoning_parts.append("No strong fraud indicators detected in this posting.")

    reasoning = '. '.join(reasoning_parts)

    # ═════════════════════════════════════════════════════════════════════════
    # LAYER 3 — Community Similarity
    # ═════════════════════════════════════════════════════════════════════════
    similarity_matches, max_similarity = _community_similarity(description, db_reports or [])

    return {
        'score':              final_score,
        'label':              label,
        'flagged_keywords':   [f['flag'] for f in flags],
        'flags':              flags,
        'corpus_similarity':  round(max_similarity, 2),
        'reasoning':          reasoning,
        'similarity_matches': similarity_matches
    }
