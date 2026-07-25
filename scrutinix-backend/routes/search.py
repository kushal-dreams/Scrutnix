"""
Search Routes — Scrutinix

GET /api/search?type=phone&q=9876543210
GET /api/search?type=email&q=scam@example.com

Returns risk score + breakdown using the 5-component algorithm.
"""

from flask import Blueprint, request, jsonify
from models.report import Report
from utils.risk_score_phone import calculate_risk_score

search_bp = Blueprint('search', __name__, url_prefix='/api')


@search_bp.route('/search')
def search():
    search_type = request.args.get('type', 'phone').strip().lower()
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify({'error': 'Query is required (use ?q=...)'}), 400

    if search_type == 'phone':
        # Clean phone number
        clean = query.replace(' ', '').replace('-', '')
        if clean.startswith('+91'):
            clean = clean[3:]
        elif clean.startswith('91') and len(clean) > 10:
            clean = clean[2:]

        if not clean.isdigit() or len(clean) != 10:
            return jsonify({'error': 'Invalid phone number format'}), 400

        reports = Report.query.filter_by(phone_number=clean).order_by(
            Report.created_at.desc()
        ).all()

        risk = calculate_risk_score(reports)

        return jsonify({
            'found': len(reports) > 0,
            'type': 'phone',
            'number': f'+91{clean}',
            'score': risk['score'],
            'label': risk['label'],
            'band': risk['band'],
            'report_count': risk['report_count'],
            'unique_reporters': risk.get('unique_reporters'),
            'top_category': risk.get('top_category'),
            'breakdown': risk.get('breakdown'),
            'reports': [r.to_dict(mask_phone=True) for r in reports[:10]],
        })

    elif search_type == 'email':
        clean_email = query.lower()

        reports = Report.query.filter_by(email_id=clean_email).order_by(
            Report.created_at.desc()
        ).all()

        risk = calculate_risk_score(reports)

        return jsonify({
            'found': len(reports) > 0,
            'type': 'email',
            'email': clean_email,
            'score': risk['score'],
            'label': risk['label'],
            'band': risk['band'],
            'report_count': risk['report_count'],
            'unique_reporters': risk.get('unique_reporters'),
            'top_category': risk.get('top_category'),
            'breakdown': risk.get('breakdown'),
            'reports': [r.to_dict() for r in reports[:10]],
        })

    else:
        return jsonify({'error': 'type must be "phone" or "email"'}), 400
