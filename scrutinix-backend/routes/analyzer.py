from flask import Blueprint, request, jsonify

analyzer_bp = Blueprint('analyzer', __name__)


@analyzer_bp.route('/api/analyze/job', methods=['POST'])
def analyze_job():
    data = request.get_json(silent=True)

    if not data or 'description' not in data:
        return jsonify({'error': 'Missing "description" field in request body.'}), 400

    description = data['description'].strip()

    if len(description) < 20:
        return jsonify({'error': 'Job description is too short to analyze (min 20 chars).'}), 400

    try:
        from models.report import Report
        fraud_reports = Report.query.filter_by(category='job_fraud').all()
        db_reports = [
            {
                'report_id':       r.id,
                'phone':           r.phone_number or 'N/A',
                'job_description': r.job_description or r.message_description or ''
            }
            for r in fraud_reports
            if (r.job_description or r.message_description)
        ]
    except Exception:
        db_reports = []

    try:
        from utils.ml_analyzer import analyze_job_description
        result = analyze_job_description(description, db_reports=db_reports)
        return jsonify(result), 200

    except FileNotFoundError as e:
        return jsonify({
            'error': str(e),
            'hint': "Run 'python train_model.py' from the backend folder first, then restart Flask."
        }), 503

    except Exception:
        return jsonify({'error': 'Analysis failed. Check server logs.'}), 500
