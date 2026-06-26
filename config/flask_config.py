import os


class FlaskConfig:
    DATABASE_URL = os.getenv('DATABASE_URL')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///kritis_alarm_lab.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    JSON_SORT_KEYS = False
