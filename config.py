import os

basedir = os.path.abspath(os.path.dirname(__file__))
uploadsdir = os.path.join(basedir, r'app\static\uploads')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:anx00di1@localhost:5432/flaskdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False