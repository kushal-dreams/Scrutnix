from flask import Blueprint, request, jsonify
from extensions import db
from models.user import User
from models.report import Report, Vote, Comment
from utils.auth_middleware import login_required

profile_bp = Blueprint('profile', __name__, url_prefix='/api')


@profile_bp.route('/profile/<username>')
def get_profile(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    reports = Report.query.filter_by(user_id=user.id).order_by(Report.created_at.desc()).all()
    total_reports = len(reports)
    total_upvotes = sum(r.upvotes for r in reports)
    total_comments = Comment.query.filter_by(user_id=user.id).count()

    unique_numbers = len(set(r.phone_number for r in reports if r.phone_number))
    report_points = min(total_reports * 10, 50)
    upvote_points = min(total_upvotes * 2, 30)
    unique_points = min(unique_numbers * 5, 20)
    community_score = min(100, report_points + upvote_points + unique_points)

    if community_score >= 80:
        level = 'Community Champion'
    elif community_score >= 50:
        level = 'Trusted Sentinel'
    elif community_score >= 20:
        level = 'Active Guardian'
    else:
        level = 'New Reporter'

    return jsonify({
        'user': user.to_dict(),
        'member_since': user.created_at.strftime('%Y-%m-%d') if user.created_at else None,
        'stats': {
            'reports_submitted': total_reports,
            'upvotes_received': total_upvotes,
            'comments_made': total_comments,
        },
        'community_score': {
            'score': community_score,
            'level': level,
        },
        'reports': [r.to_dict(mask_phone=True) for r in reports[:20]],
    })


@profile_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile(current_user):
    data = request.get_json() or {}

    if 'nickname' in data:
        nickname = data['nickname'].strip()
        if nickname and len(nickname) <= 100:
            current_user.nickname = nickname

    if 'avatar_url' in data:
        current_user.avatar_url = data['avatar_url']

    db.session.commit()
    return jsonify({'success': True, 'user': current_user.to_dict()})
