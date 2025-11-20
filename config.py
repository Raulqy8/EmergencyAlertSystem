import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:1234@127.0.0.1/EmergencyAlertSystem'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24)