"""
Report, Vote, Comment Models — Scrutinix

Supports 3 report types (sms/whatsapp/email)
Upvote/downvote with unique constraint per user
1-level comment replies via parent_comment_id
"""

import json
from datetime import datetime, timezone
from extensions import db


class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    report_type = db.Column(db.String(20), nullable=False)        # sms / whatsapp / email
    phone_number = db.Column(db.String(20), nullable=True, index=True)
    email_id = db.Column(db.String(255), nullable=True, index=True)
    message_description = db.Column(db.Text, nullable=False)
    job_description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)           # job_fraud/spam/phishing/harassment/other
    proof_image_urls_json = db.Column(db.Text, nullable=True)     # JSON array of URLs
    additional_notes = db.Column(db.Text, nullable=True)
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    votes = db.relationship('Vote', backref='report', lazy='dynamic')
    comments_list = db.relationship('Comment', backref='report', lazy='dynamic')

    CATEGORY_LABELS = {
        'job_fraud': 'Job Fraud',
        'spam': 'Spam',
        'phishing': 'Phishing',
        'harassment': 'Harassment',
        'other': 'Other',
    }

    @property
    def proof_image_urls(self):
        if self.proof_image_urls_json:
            try:
                return json.loads(self.proof_image_urls_json)
            except:
                return []
        return []

    @proof_image_urls.setter
    def proof_image_urls(self, urls):
        self.proof_image_urls_json = json.dumps(urls)

    @property
    def comments_count(self):
        return self.comments_list.count()

    def get_category_label(self):
        return self.CATEGORY_LABELS.get(self.category, self.category)

    def masked_phone(self):
        """Mask phone for public display: +91-98XX-XX5678"""
        p = self.phone_number or ''
        if len(p) >= 10:
            return f'+91-{p[:2]}XX-XX{p[-4:]}'
        return p

    def to_dict(self, mask_phone=False, current_user_id=None):
        # Check current user's vote
        user_vote = None
        if current_user_id:
            vote = Vote.query.filter_by(report_id=self.id, user_id=current_user_id).first()
            if vote:
                user_vote = vote.vote_type

        return {
            'id': self.id,
            'report_type': self.report_type,
            'phone_number': self.masked_phone() if mask_phone else self.phone_number,
            'email_id': self.email_id,
            'message_description': self.message_description,
            'job_description': self.job_description,
            'category': self.get_category_label(),
            'category_raw': self.category,
            'proof_image_urls': self.proof_image_urls,
            'additional_notes': self.additional_notes,
            'upvotes': self.upvotes,
            'downvotes': self.downvotes,
            'comments_count': self.comments_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'reporter_username': self.reporter.username if self.reporter else None,
            'user_vote': user_vote,
        }

    def __repr__(self):
        return f'<Report #{self.id} type={self.report_type} cat={self.category}>'


class Vote(db.Model):
    """One vote per user per report (upvote or downvote)"""
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)  # 'up' or 'down'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('report_id', 'user_id', name='uq_vote_report_user'),
    )


class Comment(db.Model):
    """Comments on reports, with 1-level reply support"""
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'report_id': self.report_id,
            'user_name': self.author.nickname if self.author else 'Anonymous',
            'user_username': self.author.username if self.author else None,
            'content': self.content,
            'parent_comment_id': self.parent_comment_id,
            'date': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
        }
