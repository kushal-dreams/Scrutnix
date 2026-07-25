from datetime import datetime, timedelta, timezone


CATEGORY_WEIGHTS = {
    'financial_fraud': 1.5,
    'job_scam': 1.3,
    'impersonation': 1.3,
    'registration_scam': 1.2,
    'whatsapp_spam': 0.8,
    'other': 1.0,
}


def calculate_risk_score(reports):
    report_count = len(reports)

    if report_count < 3:
        if report_count == 0:
            label = 'No Reports Yet'
        else:
            label = f'{report_count} Report(s) — Needs More Data'
        return {
            'score': None,
            'band': 'unknown',
            'label': label,
            'report_count': report_count,
        }

    if report_count >= 20:
        base = 90
    elif report_count >= 10:
        base = 70
    elif report_count >= 5:
        base = 50
    else:
        base = 30

    total_weight = 0
    for r in reports:
        total_weight += CATEGORY_WEIGHTS.get(r.category, 1.0)
    avg_weight = total_weight / report_count
    category_bonus = (avg_weight - 1.0) * 20

    now = datetime.now(timezone.utc)
    recent_count = 0
    for r in reports:
        created = r.created_at
        if created and created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        if created and (now - created) < timedelta(days=30):
            recent_count += 1

    recency_ratio = recent_count / report_count
    recency_bonus = recency_ratio * 10

    unique_reporters = len(set(r.reporter_id for r in reports))
    if unique_reporters >= report_count * 0.8:
        diversity_bonus = 5
    else:
        diversity_bonus = 0

    verified_count = sum(1 for r in reports if r.verified)
    verified_bonus = min(verified_count * 3, 15)

    score = base + category_bonus + recency_bonus + diversity_bonus + verified_bonus
    score = max(0, min(100, round(score)))

    if score > 60:
        band = 'high'
        label = 'Heavily Flagged'
    elif score > 30:
        band = 'medium'
        label = 'Caution'
    else:
        band = 'low'
        label = 'Low Activity'

    return {
        'score': score,
        'band': band,
        'label': label,
        'report_count': report_count,
    }
