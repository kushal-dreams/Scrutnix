import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///scrutinix.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET = os.getenv('JWT_SECRET', 'scrutinix-dev-secret-change-in-production')
    JWT_EXPIRY_HOURS = 72
    DEBUG = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    PORT = int(os.getenv('FLASK_PORT', 5000))
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
