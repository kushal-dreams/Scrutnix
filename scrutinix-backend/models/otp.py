"""
OTP Model — Scrutinix

Stores OTP codes with expiration.
In production, use Twilio Verify instead of storing codes.
For development, OTP is printed to console.
"""

from datetime import datetime, timedelta, timezone
from extensions import db


class OTP(db.Model):
    __tablename__ = 'otp_records'

    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(15), nullable=False, index=True)
    otp_code = db.Column(db.String(10), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @classmethod
    def create_otp(cls, phone, code, expiry_minutes=10):
        otp = cls(
            phone_number=phone,
            otp_code=code,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes),
        )
        db.session.add(otp)
        db.session.commit()
        return otp

    def is_valid(self):
        """Check if OTP is not expired and not used"""
        now = datetime.now(timezone.utc)
        expires = self.expires_at
        if expires and expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return not self.verified and now < expires

    def mark_verified(self):
        self.verified = True
        db.session.commit()
