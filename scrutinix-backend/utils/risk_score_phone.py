"""
risk_score_phone.py — Core Risk Scoring Algorithm
=================================================

PURPOSE: Calculate a 0-100 risk score for a phone number or email
         from community-submitted reports.

This is the CORE ALGORITHM of Scrutinix. Each component is transparent
and explainable — no black-box model.

ALGORITHM COMPONENTS (5 factors):
1. Category Severity Weight  — worse scam types = higher score
2. Report Consensus          — more unique reporters = more confidence
3. Recency Weight            — recent reports count more
4. Community Validation      — upvoted reports are more credible
5. Proof Presence Bonus      — reports with images get a boost

MINIMUM THRESHOLD: 3 reports from 3 different users before a score is shown.

LABELS:
  0-30   → Safe
  31-60  → Suspicious
  61-85  → Dangerous
  86-100 → Critical
"""

from datetime import datetime, timezone


# ─── Component 1: Category Severity Weights ─────────────
# Each report's category carries a base severity score.
# Job fraud and phishing are the most dangerous.

CATEGORY_WEIGHTS = {
    'job_fraud':   9.0,
    'phishing':    8.5,
    'harassment':  7.0,
    'spam':        5.0,
    'other':       3.0,
}


# ─── Maximum expected raw score (calibration constant) ───
MAX_POSSIBLE_RAW = 50.0


def calculate_risk_score(reports):
    """
    Calculate risk score from a list of Report objects.

    Args:
        reports: List of Report model objects

    Returns:
        dict with score, label, report_count, unique_reporters,
        top_category, and breakdown
    """
    report_count = len(reports)

    # ── Threshold Check ──────────────────────────────────
    # Need at least 3 reports from 3 unique users
    unique_reporters = len(set(r.user_id for r in reports))

    if report_count < 3 or unique_reporters < 3:
        return {
            'score': None,
            'label': 'Insufficient Data' if report_count > 0 else 'No Reports',
            'band': 'unknown',
            'report_count': report_count,
            'unique_reporters': unique_reporters,
            'top_category': None,
            'breakdown': None,
        }

    # ── Component 2: Consensus Multiplier ────────────────
    # More unique reporters = more confidence
    # Caps at 1.0 when 10+ unique reporters
    consensus_multiplier = min(1.0, unique_reporters / 10)

    # ── Process each report ──────────────────────────────
    now = datetime.now(timezone.utc)
    report_scores = []
    recency_factors = []
    validation_factors = []
    category_counts = {}

    for r in reports:
        # Category weight
        cat_weight = CATEGORY_WEIGHTS.get(r.category, 3.0)

        # Track category counts for "top category"
        cat_label = r.get_category_label() if hasattr(r, 'get_category_label') else r.category
        category_counts[cat_label] = category_counts.get(cat_label, 0) + 1

        # ── Component 3: Recency Factor ──────────────────
        # Recent reports carry more weight. Decay over 90 days.
        created = r.created_at
        if created and created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)

        if created:
            days_old = (now - created).days
            recency_factor = max(0.3, 1.0 - (days_old / 90))
        else:
            recency_factor = 0.5

        recency_factors.append(recency_factor)

        # ── Component 4: Community Validation ────────────
        # If upvotes exist, a higher ratio means more credibility
        total_votes = (r.upvotes or 0) + (r.downvotes or 0)
        if total_votes > 0:
            validation_factor = (r.upvotes or 0) / total_votes
        else:
            validation_factor = 0.5  # neutral when no votes

        validation_factors.append(validation_factor)

        # ── Component 5: Proof Presence Bonus ────────────
        has_proof = False
        if hasattr(r, 'proof_image_urls') and r.proof_image_urls:
            has_proof = len(r.proof_image_urls) > 0
        elif hasattr(r, 'proof_image_urls_json') and r.proof_image_urls_json:
            has_proof = True
        proof_bonus = 1.2 if has_proof else 1.0

        # ── Per-Report Score ─────────────────────────────
        report_score = (
            cat_weight
            * recency_factor
            * validation_factor
            * proof_bonus
        )
        report_scores.append(report_score)

    # ── Aggregation ──────────────────────────────────────
    raw_score = sum(report_scores) * consensus_multiplier
    normalized_score = min(100, (raw_score / MAX_POSSIBLE_RAW) * 100)
    final_score = round(normalized_score)

    # ── Label Assignment ─────────────────────────────────
    if final_score <= 30:
        label = 'Safe'
        band = 'low'
    elif final_score <= 60:
        label = 'Suspicious'
        band = 'medium'
    elif final_score <= 85:
        label = 'Dangerous'
        band = 'high'
    else:
        label = 'Critical'
        band = 'critical'

    # Find top category
    top_category = max(category_counts, key=category_counts.get) if category_counts else None

    # Build breakdown (for transparency)
    avg_recency = sum(recency_factors) / len(recency_factors) if recency_factors else 0
    avg_validation = sum(validation_factors) / len(validation_factors) if validation_factors else 0

    return {
        'score': final_score,
        'label': label,
        'band': band,
        'report_count': report_count,
        'unique_reporters': unique_reporters,
        'top_category': top_category,
        'breakdown': {
            'consensus_factor': round(consensus_multiplier, 2),
            'avg_recency_factor': round(avg_recency, 2),
            'avg_validation_factor': round(avg_validation, 2),
        },
    }
