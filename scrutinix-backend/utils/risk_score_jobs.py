"""
risk_score_jobs.py — Job Description Fraud Analyzer
====================================================

PURPOSE: Analyze a pasted job description and return a fraud risk score.

APPROACH: Hybrid NLP + Community Data (no external API needed)

STAGE 1: Keyword Flag Detection
  - Curated list of weighted red-flag keywords/phrases
  - Each keyword has a weight (1-3)
  - keyword_score = min(60, sum of matched weights × 5)

STAGE 2: Community Corpus Matching
  - All job_description fields from fraud reports are extracted
  - TF-IDF vectorizer is built from this corpus
  - Cosine similarity is computed against the user's input
  - corpus_score = max_similarity × 40

STAGE 3: Score Combination
  - total_score = min(100, keyword_score + corpus_score)

OUTPUT:
  - score (0-100)
  - label (Low Risk / Moderate / High Risk / Likely Fraud)
  - flagged_keywords
  - corpus_similarity
  - reasoning
"""

import re
import math


# ─── Stage 1: Weighted Fraud Signal Keywords ────────────
FRAUD_SIGNALS = {
    # High weight (3) — strong indicators of fraud
    "no experience required": 3,
    "earn from home unlimited": 3,
    "wire transfer": 3,
    "advance fee": 3,
    "whatsapp interview": 3,
    "pay to apply": 3,
    "upfront payment": 3,
    "cryptocurrency payment": 3,
    "registration fee": 3,
    "security deposit": 3,
    "processing fee": 3,
    "send your aadhaar": 3,
    "send your pan": 3,
    "joining fee": 3,

    # Medium weight (2) — suspicious but could be legitimate
    "work from home": 2,
    "easy money": 2,
    "guaranteed income": 2,
    "flexible hours unlimited": 2,
    "no interviews": 2,
    "immediate joining": 2,
    "earn daily": 2,
    "100% genuine": 2,
    "not a scam": 2,
    "copy paste job": 2,
    "simple task": 2,
    "unlimited earning": 2,
    "whatsapp only": 2,

    # Low weight (1) — minor flags
    "part time": 1,
    "commission based": 1,
    "be your own boss": 1,
    "freelance": 1,
    "work from mobile": 1,
    "telegram group": 1,
    "limited seats": 1,
    "hurry up": 1,
    "apply now": 1,
}


# ─── Stopwords for TF-IDF ───────────────────────────────
STOPWORDS = {
    'i', 'me', 'my', 'we', 'our', 'you', 'your', 'he', 'him', 'his',
    'she', 'her', 'it', 'its', 'they', 'them', 'their', 'what', 'which',
    'who', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was',
    'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
    'did', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'as', 'of',
    'at', 'by', 'for', 'with', 'about', 'to', 'from', 'up', 'in',
    'out', 'on', 'off', 'over', 'under', 'again', 'then', 'once',
    'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each',
    'few', 'more', 'most', 'other', 'some', 'such', 'no', 'not',
    'only', 'same', 'so', 'than', 'too', 'very', 'can', 'will',
    'just', 'should', 'now',
}


def tokenize(text):
    """Simple tokenizer: lowercase, remove punctuation, remove stopwords"""
    if not text:
        return []
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    words = [w for w in text.split() if w not in STOPWORDS and len(w) > 2]
    return words


def cosine_similarity_manual(vec_a, vec_b):
    """Compute cosine similarity between two term-frequency dicts"""
    # Get all terms
    all_terms = set(vec_a.keys()) | set(vec_b.keys())
    dot_product = sum(vec_a.get(t, 0) * vec_b.get(t, 0) for t in all_terms)
    mag_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
    mag_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot_product / (mag_a * mag_b)


def build_tfidf(documents):
    """
    Build TF-IDF vectors for a list of token lists.
    Returns list of TF-IDF dicts and the document frequency dict.
    """
    n = len(documents)
    if n == 0:
        return [], {}

    # Document frequency
    df = {}
    for doc in documents:
        unique_tokens = set(doc)
        for token in unique_tokens:
            df[token] = df.get(token, 0) + 1

    # TF-IDF for each document
    tfidf_vectors = []
    for doc in documents:
        tf = {}
        for token in doc:
            tf[token] = tf.get(token, 0) + 1

        tfidf = {}
        for token, count in tf.items():
            idf = math.log((n + 1) / (df.get(token, 0) + 1)) + 1
            tfidf[token] = count * idf

        tfidf_vectors.append(tfidf)

    return tfidf_vectors, df


def analyze_job_description(text, existing_reports=None):
    """
    Analyze a job description for fraud signals.

    Args:
        text: The job description string to analyze
        existing_reports: List of dicts with 'job_desc' field from fraud reports

    Returns:
        dict with score, label, flagged_keywords, corpus_similarity, reasoning
    """
    if not text or not text.strip():
        return {
            'score': 0,
            'label': 'No Input',
            'flagged_keywords': [],
            'flags': [],
            'corpus_similarity': 0,
            'reasoning': 'No text provided to analyze.',
            'similarity_matches': [],
        }

    text_lower = text.lower()

    # ── Stage 1: Keyword Flag Detection ──────────────────
    matched_keywords = []
    total_keyword_weight = 0

    for phrase, weight in FRAUD_SIGNALS.items():
        if phrase in text_lower:
            matched_keywords.append({
                'keyword': phrase,
                'weight': weight,
                'severity': 'high' if weight >= 3 else 'medium' if weight >= 2 else 'low',
            })
            total_keyword_weight += weight

    keyword_score = min(60, total_keyword_weight * 5)

    # ── Stage 2: Community Corpus Matching ───────────────
    corpus_similarity = 0.0
    similarity_matches = []

    if existing_reports:
        # Get fraud reports with job descriptions
        fraud_reports = [
            r for r in existing_reports
            if r.get('job_desc') and r['job_desc'].strip()
        ]

        if fraud_reports:
            # Tokenize all documents
            corpus_tokens = [tokenize(r['job_desc']) for r in fraud_reports]
            query_tokens = tokenize(text)

            # Build TF-IDF
            all_docs = corpus_tokens + [query_tokens]
            tfidf_vectors, df = build_tfidf(all_docs)

            if tfidf_vectors:
                query_vector = tfidf_vectors[-1]  # Last one is the query

                # Compute similarity against each corpus document
                for i, report in enumerate(fraud_reports):
                    sim = cosine_similarity_manual(query_vector, tfidf_vectors[i])
                    if sim >= 0.2:
                        similarity_matches.append({
                            'report_id': report.get('id'),
                            'phone': report.get('phone'),
                            'category': report.get('category'),
                            'similarity': round(sim, 2),
                        })

                similarity_matches.sort(key=lambda x: x['similarity'], reverse=True)

                if similarity_matches:
                    corpus_similarity = similarity_matches[0]['similarity']

    corpus_score = corpus_similarity * 40

    # ── Stage 3: Score Combination ───────────────────────
    total_score = min(100, int(keyword_score + corpus_score))

    # ── Label Assignment ─────────────────────────────────
    if total_score <= 30:
        label = 'Low Risk'
    elif total_score <= 60:
        label = 'Moderate'
    elif total_score <= 85:
        label = 'High Risk'
    else:
        label = 'Likely Fraud'

    # ── Reasoning ────────────────────────────────────────
    reasons = []
    if matched_keywords:
        high_flags = [k for k in matched_keywords if k['severity'] == 'high']
        if high_flags:
            reasons.append(f"{len(high_flags)} high-risk phrases detected")
        medium_flags = [k for k in matched_keywords if k['severity'] == 'medium']
        if medium_flags:
            reasons.append(f"{len(medium_flags)} suspicious phrases found")

    if corpus_similarity >= 0.3:
        reasons.append(
            f"Strong similarity ({int(corpus_similarity * 100)}%) to "
            f"{len(similarity_matches)} known fraud reports in our database"
        )
    elif corpus_similarity >= 0.15:
        reasons.append(
            f"Some similarity ({int(corpus_similarity * 100)}%) to existing fraud reports"
        )

    if not reasons:
        reasons.append("No significant red flags detected")

    reasoning = '. '.join(reasons) + '.'

    # Build flags list for frontend display
    flags = [
        {'flag': k['keyword'], 'severity': k['severity']}
        for k in matched_keywords
    ]

    return {
        'score': total_score,
        'label': label,
        'flagged_keywords': [k['keyword'] for k in matched_keywords],
        'flags': flags,
        'corpus_similarity': round(corpus_similarity, 2),
        'reasoning': reasoning,
        'similarity_matches': similarity_matches[:5],
    }
