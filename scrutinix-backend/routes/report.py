import os
import json
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from extensions import db
from models.report import Report, Vote, Comment
from utils.auth_middleware import login_required, get_optional_user

report_bp = Blueprint('report', __name__, url_prefix='/api')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
REPORTS_PER_PAGE = 10


@report_bp.route('/ticker-reports')
def get_ticker_reports():
    reports = (
        Report.query
        .order_by(Report.created_at.desc())
        .limit(20)
        .all()
    )

    items = []
    for r in reports:
        items.append({
            'type': r.report_type.upper() if r.report_type else 'SMS',
            'identifier': r.masked_phone() if r.phone_number else (r.email_id or 'N/A'),
            'category': r.get_category_label(),
        })

    return jsonify({'items': items})


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@report_bp.route('/reports', methods=['POST'])
@login_required
def submit_report(current_user):
    if request.content_type and 'multipart/form-data' in request.content_type:
        report_type = request.form.get('report_type', 'sms').strip()
        phone_number = request.form.get('phone_number', '').strip() or None
        email_id = request.form.get('email_id', '').strip() or None
        message_description = request.form.get('message_description', '').strip()
        job_description = request.form.get('job_description', '').strip() or None
        category = request.form.get('category', '').strip()
        additional_notes = request.form.get('additional_notes', '').strip() or None
        proof_files = request.files.getlist('proof_images')
    else:
        data = request.get_json() or {}
        report_type = data.get('report_type', 'sms').strip()
        phone_number = data.get('phone_number', '').strip() or None
        email_id = data.get('email_id', '').strip() or None
        message_description = data.get('message_description', '').strip()
        job_description = data.get('job_description', '').strip() or None
        category = data.get('category', '').strip()
        additional_notes = data.get('additional_notes', '').strip() or None
        proof_files = []

    errors = []
    valid_types = ['sms', 'whatsapp', 'email']
    valid_categories = ['job_fraud', 'spam', 'phishing', 'harassment', 'other']

    if report_type not in valid_types:
        errors.append(f'Report type must be one of: {", ".join(valid_types)}')
    if category not in valid_categories:
        errors.append(f'Category must be one of: {", ".join(valid_categories)}')
    if not message_description or len(message_description) < 20:
        errors.append('Description must be at least 20 characters')

    if phone_number:
        phone_number = phone_number.replace(' ', '').replace('-', '').replace('+91', '')
        if not phone_number.isdigit() or len(phone_number) != 10:
            errors.append('Invalid phone number format')

    if errors:
        return jsonify({'success': False, 'message': '; '.join(errors), 'errors': errors}), 400

    if phone_number:
        existing = Report.query.filter_by(
            user_id=current_user.id, phone_number=phone_number
        ).first()
        if existing:
            return jsonify({
                'success': False,
                'message': 'You have already reported this phone number.',
            }), 409

    if email_id:
        existing = Report.query.filter_by(
            user_id=current_user.id, email_id=email_id
        ).first()
        if existing:
            return jsonify({
                'success': False,
                'message': 'You have already reported this email address.',
            }), 409

    proof_urls = []
    for f in proof_files[:5]:
        if f and f.filename and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            filename = f'{current_user.id}_{filename}'
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            f.save(upload_path)
            proof_urls.append(f'/uploads/{filename}')

    report = Report(
        user_id=current_user.id,
        report_type=report_type,
        phone_number=phone_number,
        email_id=email_id,
        message_description=message_description,
        job_description=job_description,
        category=category,
        additional_notes=additional_notes,
    )
    report.proof_image_urls = proof_urls
    db.session.add(report)
    db.session.commit()

    from routes.live_feed import push_event
    push_event({
        'type': report_type.upper(),
        'identifier': report.masked_phone() if phone_number else (email_id or 'N/A'),
        'category': report.get_category_label(),
    })

    return jsonify({
        'success': True,
        'message': 'Report submitted successfully',
        'report_id': report.id,
    })


@report_bp.route('/reports')
def get_reports():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '').strip()
    sort = request.args.get('sort', 'recent').strip()

    query = Report.query

    if category:
        query = query.filter_by(category=category)

    if sort == 'popular':
        query = query.order_by(Report.upvotes.desc())
    else:
        query = query.order_by(Report.created_at.desc())

    pagination = query.paginate(page=page, per_page=REPORTS_PER_PAGE, error_out=False)

    current_user = get_optional_user()
    current_user_id = current_user.id if current_user else None

    reports = [r.to_dict(mask_phone=True, current_user_id=current_user_id) for r in pagination.items]

    return jsonify({
        'reports': reports,
        'total': pagination.total,
        'page': page,
        'pages': pagination.pages,
    })


@report_bp.route('/reports/<int:report_id>')
def get_report_detail(report_id):
    report = Report.query.get(report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404

    current_user = get_optional_user()
    current_user_id = current_user.id if current_user else None

    return jsonify({
        'report': report.to_dict(mask_phone=False, current_user_id=current_user_id),
    })


@report_bp.route('/reports/<int:report_id>/vote', methods=['POST'])
@login_required
def vote_report(current_user, report_id):
    report = Report.query.get(report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404

    data = request.get_json() or {}
    vote_type = data.get('vote_type', 'up')
    if vote_type not in ('up', 'down'):
        return jsonify({'error': 'vote_type must be "up" or "down"'}), 400

    existing = Vote.query.filter_by(report_id=report_id, user_id=current_user.id).first()

    if existing:
        if existing.vote_type == vote_type:
            if vote_type == 'up':
                report.upvotes = max(0, report.upvotes - 1)
            else:
                report.downvotes = max(0, report.downvotes - 1)
            db.session.delete(existing)
            db.session.commit()
            return jsonify({
                'success': True,
                'action': 'removed',
                'upvotes': report.upvotes,
                'downvotes': report.downvotes,
                'user_vote': None,
            })
        else:
            if existing.vote_type == 'up':
                report.upvotes = max(0, report.upvotes - 1)
            else:
                report.downvotes = max(0, report.downvotes - 1)
            existing.vote_type = vote_type
            if vote_type == 'up':
                report.upvotes += 1
            else:
                report.downvotes += 1
            db.session.commit()
            return jsonify({
                'success': True,
                'action': 'switched',
                'upvotes': report.upvotes,
                'downvotes': report.downvotes,
                'user_vote': vote_type,
            })
    else:
        vote = Vote(report_id=report_id, user_id=current_user.id, vote_type=vote_type)
        db.session.add(vote)
        if vote_type == 'up':
            report.upvotes += 1
        else:
            report.downvotes += 1
        db.session.commit()
        return jsonify({
            'success': True,
            'action': 'added',
            'upvotes': report.upvotes,
            'downvotes': report.downvotes,
            'user_vote': vote_type,
        })


@report_bp.route('/reports/<int:report_id>/comments')
def get_comments(report_id):
    report = Report.query.get(report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404

    comments = (
        Comment.query
        .filter_by(report_id=report_id)
        .order_by(Comment.created_at.asc())
        .all()
    )

    return jsonify({
        'comments': [c.to_dict() for c in comments],
        'total': len(comments),
    })


@report_bp.route('/reports/<int:report_id>/comment', methods=['POST'])
@login_required
def add_comment(current_user, report_id):
    report = Report.query.get(report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404

    data = request.get_json() or {}
    content = data.get('content', '').strip()
    parent_id = data.get('parent_comment_id')

    if not content:
        return jsonify({'error': 'Comment cannot be empty'}), 400
    if len(content) > 1000:
        return jsonify({'error': 'Comment too long (max 1000 characters)'}), 400

    comment = Comment(
        report_id=report_id,
        user_id=current_user.id,
        content=content,
        parent_comment_id=parent_id,
    )
    db.session.add(comment)
    db.session.commit()

    return jsonify({
        'success': True,
        'comment': comment.to_dict(),
    })
