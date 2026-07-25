import os
import re
import csv
import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

_BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODEL_PATH   = os.path.join(_BASE_DIR, 'models', 'job_fraud_model.pkl')
_KEYWORDS_CSV = os.path.join(
    _BASE_DIR, 'datasets', 'indian_nlp', 'india_scam_keywords_dictionary.csv'
)

_pipeline = None
_keywords = None


def _get_pipeline():
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


def _get_keywords() -> dict:
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
            reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]

            for row in reader:
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


def _preprocess(text: str) -> str:
    if not isinstance(text, str):
        return ''
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s₹]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _is_negated(text: str, phrase: str, window: int = 6) -> bool:
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


def _top_fraud_signals(pipeline, raw_text: str, top_n: int = 8) -> list[tuple[str, float]]:
    vectorizer    = pipeline.named_steps['tfidf']
    clf           = pipeline.named_steps['clf']
    feature_names = vectorizer.get_feature_names_out()
    fraud_coefs   = clf.coef_[0]

    processed = _preprocess(raw_text)
    X         = vectorizer.transform([processed])

    present_indices = X.nonzero()[1]
    if len(present_indices) == 0:
        return []

    scored = [
        (feature_names[i], float(X[0, i] * fraud_coefs[i]))
        for i in present_indices
        if fraud_coefs[i] > 0
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_n]


def _community_similarity(query: str, db_reports: list[dict]) -> tuple[list, float]:
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
            if sim > 0.10:
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


def analyze_job_description(description: str, db_reports: list[dict] = None) -> dict:
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

    processed        = _preprocess(description)
    probabilities    = pipeline.predict_proba([processed])[0]
    fraud_probability = float(probabilities[1])
    ml_score         = int(fraud_probability * 100)

    flags          = []
    keyword_bonus  = 0
    text_lower     = description.lower()

    for phrase, info in keywords.items():
        if phrase in text_lower:
            if _is_negated(description, phrase):
                continue
            flags.append({
                'flag':     phrase,
                'severity': info['severity']
            })
            keyword_bonus += info['weight'] * 2

    keyword_bonus = min(20, keyword_bonus)

    final_score = min(100, int(ml_score * 0.8 + keyword_bonus))

    high_flags_count = sum(1 for f in flags if f['severity'] == 'high')
    if high_flags_count >= 2 and final_score < 50:
        final_score = 55

    if final_score <= 25:
        label = 'Low Risk'
    elif final_score <= 50:
        label = 'Moderate Risk'
    elif final_score <= 75:
        label = 'High Risk'
    else:
        label = 'Likely Fraud'

    top_ml_signals = _top_fraud_signals(pipeline, description)
    ml_words       = [word for word, _ in top_ml_signals[:5]]

    reasoning_parts = []

    high_flags = [f['flag'] for f in flags if f['severity'] == 'high']
    med_flags  = [f['flag'] for f in flags if f['severity'] == 'medium']
    if high_flags:
        reasoning_parts.append(f"Critical Indian scam signals: {', '.join(high_flags[:3])}")
    if med_flags:
        reasoning_parts.append(f"Warning signals: {', '.join(med_flags[:3])}")

    if ml_words:
        reasoning_parts.append(f"ML-detected suspicious patterns: {', '.join(ml_words)}")

    if not reasoning_parts:
        reasoning_parts.append("No strong fraud indicators detected in this posting.")

    reasoning = '. '.join(reasoning_parts)

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
