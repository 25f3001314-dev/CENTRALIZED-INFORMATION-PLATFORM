import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'civicpulse-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///civicpulse.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    SLA_HOURS = {
        'Low': 168,
        'Medium': 120,
        'High': 72,
        'Urgent': 24,
    }
