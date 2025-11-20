import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://root:{os.getenv('MYSQL_PASSWORD')}@127.0.0.1/EmergencyAlertSystem"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24)

    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')