"""
Auth Middleware — JWT token generation and verification
"""

import jwt
import functools
from datetime import datetime, timedelta, timezone
from flask import request, jsonify
from config import Config


def generate_token(user_id):
    """Generate a JWT token for a user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(hours=Config.JWT_EXPIRY_HOURS),
        'iat': datetime.now(timezone.utc),
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm='HS256')


def decode_token(token):
    """Decode a JWT token, returns user_id or None"""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
        return payload.get('user_id')
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def login_required(f):
    """Decorator that requires a valid JWT token"""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401

        token = auth_header.split(' ', 1)[1]
        user_id = decode_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401

        from models.user import User
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        return f(user, *args, **kwargs)
    return decorated


def get_optional_user():
    """Try to get current user from token, returns None if not authenticated"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None

    token = auth_header.split(' ', 1)[1]
    user_id = decode_token(token)
    if not user_id:
        return None

    from models.user import User
    return User.query.get(user_id)
